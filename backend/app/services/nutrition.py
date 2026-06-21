"""Nutrition calculation service for customized drinks."""

from sqlalchemy.orm import Session

from app.models import Drink, Ingredient
from app.schemas import CustomizeDrinkRequest, NutritionResponse

# Size multipliers relative to grande (reference size)
SIZE_MULTIPLIERS = {
    "tall": 0.75,
    "grande": 1.0,
    "venti": 1.25,
}


def get_ingredient_map(db: Session) -> dict[str, Ingredient]:
    """Build a lookup map of ingredient name -> Ingredient model."""
    return {ing.name: ing for ing in db.query(Ingredient).all()}


def calculate_nutrition(db: Session, request: CustomizeDrinkRequest) -> tuple[Drink, dict, NutritionResponse]:
    """
    Calculate total nutrition for a customized drink.

    Applies size scaling, milk substitution, syrup pumps, and add-ons.
    """
    drink = db.query(Drink).filter(Drink.id == request.drink_id).first()
    if not drink:
        raise ValueError(f"Drink with id {request.drink_id} not found.")

    ingredients = get_ingredient_map(db)
    multiplier = SIZE_MULTIPLIERS.get(request.size, 1.0)

    calories = drink.base_calories * multiplier
    sugar = drink.base_sugar * multiplier
    protein = drink.base_protein * multiplier
    caffeine = drink.base_caffeine * multiplier

    # Milk substitution (whole milk is baseline; others apply delta scaled by size)
    milk = ingredients.get(request.milk_type)
    if milk:
        calories += milk.calories_delta * multiplier
        sugar += milk.sugar_delta * multiplier
        protein += milk.protein_delta * multiplier
        caffeine += milk.caffeine_delta * multiplier

    # Syrup pumps
    for pump_name, count in [
        ("vanilla", request.vanilla_pumps),
        ("caramel", request.caramel_pumps),
        ("mocha", request.mocha_pumps),
    ]:
        syrup = ingredients.get(pump_name)
        if syrup and count > 0:
            calories += syrup.calories_delta * count
            sugar += syrup.sugar_delta * count
            protein += syrup.protein_delta * count
            caffeine += syrup.caffeine_delta * count

    # Add-ons
    if request.whipped_cream:
        addon = ingredients.get("whipped cream")
        if addon:
            calories += addon.calories_delta
            sugar += addon.sugar_delta
            protein += addon.protein_delta

    if request.protein_boost:
        addon = ingredients.get("protein boost")
        if addon:
            calories += addon.calories_delta
            sugar += addon.sugar_delta
            protein += addon.protein_delta

    if request.extra_espresso_shot:
        addon = ingredients.get("extra espresso shot")
        if addon:
            calories += addon.calories_delta
            caffeine += addon.caffeine_delta

    # Round to one decimal place
    calories = round(calories, 1)
    sugar = round(sugar, 1)
    protein = round(protein, 1)
    caffeine = round(caffeine, 1)

    customizations = {
        "size": request.size,
        "milk_type": request.milk_type,
        "vanilla_pumps": request.vanilla_pumps,
        "caramel_pumps": request.caramel_pumps,
        "mocha_pumps": request.mocha_pumps,
        "whipped_cream": request.whipped_cream,
        "protein_boost": request.protein_boost,
        "extra_espresso_shot": request.extra_espresso_shot,
    }

    summary = (
        f"Your customized {drink.name} has {calories} calories, "
        f"{sugar}g sugar, and {protein}g protein."
    )

    nutrition = NutritionResponse(
        calories=calories,
        sugar=sugar,
        protein=protein,
        caffeine=caffeine,
        summary=summary,
    )

    return drink, customizations, nutrition
