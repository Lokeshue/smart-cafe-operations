"""Drink menu and customization endpoints."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Drink, Ingredient
from app.schemas import CustomizeDrinkRequest, CustomizeDrinkResponse, DrinkResponse, IngredientResponse
from app.services.nutrition import calculate_nutrition

logger = logging.getLogger(__name__)
router = APIRouter(tags=["Drinks"])


@router.get("/drinks", response_model=list[DrinkResponse])
def list_drinks(db: Session = Depends(get_db)):
    """Return all base drinks on the menu."""
    drinks = db.query(Drink).order_by(Drink.name).all()
    logger.info("Fetched %d drinks", len(drinks))
    return drinks


@router.get("/ingredients", response_model=list[IngredientResponse])
def list_ingredients(db: Session = Depends(get_db)):
    """Return all customization ingredients with nutrition deltas."""
    return db.query(Ingredient).order_by(Ingredient.category, Ingredient.name).all()


@router.post("/customize-drink", response_model=CustomizeDrinkResponse)
def customize_drink(request: CustomizeDrinkRequest, db: Session = Depends(get_db)):
    """
    Calculate live nutrition for a customized drink.

    Updates instantly as the customer changes milk, syrups, size, and add-ons.
    """
    try:
        drink, customizations, nutrition = calculate_nutrition(db, request)
    except ValueError as e:
        logger.error("Customize drink failed: %s", e)
        raise HTTPException(status_code=404, detail=str(e))

    logger.info(
        "Customized %s (%s): %.0f cal, %.1fg sugar",
        drink.name,
        request.size,
        nutrition.calories,
        nutrition.sugar,
    )

    return CustomizeDrinkResponse(
        drink_name=drink.name,
        size=request.size,
        customizations=customizations,
        nutrition=nutrition,
    )
