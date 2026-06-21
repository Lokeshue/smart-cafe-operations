"""Seed sample drinks and ingredients into the database."""

import json
import logging
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models import Drink, Ingredient, Order

logger = logging.getLogger(__name__)

DRINKS = [
    {
        "name": "Latte",
        "description": "Rich espresso with steamed milk and a light layer of foam.",
        "base_calories": 190,
        "base_sugar": 18,
        "base_protein": 13,
        "base_caffeine": 150,
    },
    {
        "name": "Cold Brew",
        "description": "Slow-steeped cold coffee served over ice.",
        "base_calories": 5,
        "base_sugar": 0,
        "base_protein": 0,
        "base_caffeine": 205,
    },
    {
        "name": "Frappuccino",
        "description": "Blended coffee beverage with whipped cream.",
        "base_calories": 380,
        "base_sugar": 52,
        "base_protein": 5,
        "base_caffeine": 95,
    },
    {
        "name": "Matcha",
        "description": "Finely ground green tea whisked with steamed milk.",
        "base_calories": 240,
        "base_sugar": 32,
        "base_protein": 12,
        "base_caffeine": 80,
    },
    {
        "name": "Refresher",
        "description": "Fruit-forward iced beverage with green coffee extract.",
        "base_calories": 90,
        "base_sugar": 20,
        "base_protein": 0,
        "base_caffeine": 45,
    },
]

INGREDIENTS = [
    # Milk types (replace default whole milk baseline)
    {"name": "whole milk", "category": "milk", "calories_delta": 0, "sugar_delta": 0, "protein_delta": 0, "caffeine_delta": 0},
    {"name": "almond milk", "category": "milk", "calories_delta": -80, "sugar_delta": -10, "protein_delta": -8, "caffeine_delta": 0},
    {"name": "oat milk", "category": "milk", "calories_delta": -20, "sugar_delta": 2, "protein_delta": -2, "caffeine_delta": 0},
    {"name": "nonfat milk", "category": "milk", "calories_delta": -50, "sugar_delta": -2, "protein_delta": 2, "caffeine_delta": 0},
    # Syrups (per pump)
    {"name": "vanilla", "category": "syrup", "calories_delta": 20, "sugar_delta": 5, "protein_delta": 0, "caffeine_delta": 0},
    {"name": "caramel", "category": "syrup", "calories_delta": 25, "sugar_delta": 6, "protein_delta": 0, "caffeine_delta": 0},
    {"name": "mocha", "category": "syrup", "calories_delta": 25, "sugar_delta": 5, "protein_delta": 1, "caffeine_delta": 5},
    # Add-ons
    {"name": "whipped cream", "category": "addon", "calories_delta": 80, "sugar_delta": 3, "protein_delta": 1, "caffeine_delta": 0},
    {"name": "protein boost", "category": "addon", "calories_delta": 50, "sugar_delta": 2, "protein_delta": 10, "caffeine_delta": 0},
    {"name": "extra espresso shot", "category": "addon", "calories_delta": 5, "sugar_delta": 0, "protein_delta": 0, "caffeine_delta": 75},
]

SAMPLE_ORDERS = [
    {
        "customer_name": "Alex Chen",
        "drink_name": "Latte",
        "customizations": {"size": "grande", "milk_type": "oat milk", "vanilla_pumps": 2},
        "channel": "mobile",
        "minutes_ago": 8,
        "status": "In Progress",
    },
    {
        "customer_name": "Jordan Lee",
        "drink_name": "Cold Brew",
        "customizations": {"size": "venti", "milk_type": "almond milk"},
        "channel": "drive-thru",
        "minutes_ago": 6,
        "status": "Received",
    },
    {
        "customer_name": "Sam Rivera",
        "drink_name": "Frappuccino",
        "customizations": {"size": "grande", "whipped_cream": True, "caramel_pumps": 3},
        "channel": "walk-in",
        "minutes_ago": 5,
        "status": "Received",
    },
    {
        "customer_name": "Taylor Kim",
        "drink_name": "Matcha",
        "customizations": {"size": "tall", "milk_type": "nonfat milk"},
        "channel": "mobile",
        "minutes_ago": 4,
        "status": "Received",
    },
    {
        "customer_name": "Morgan Davis",
        "drink_name": "Refresher",
        "customizations": {"size": "venti"},
        "channel": "drive-thru",
        "minutes_ago": 3,
        "status": "Received",
    },
    {
        "customer_name": "Casey Wong",
        "drink_name": "Latte",
        "customizations": {"size": "grande", "extra_espresso_shot": True},
        "channel": "walk-in",
        "minutes_ago": 2,
        "status": "Received",
    },
]


def seed_database(db: Session) -> None:
    """Populate database with drinks, ingredients, and sample orders if empty."""
    if db.query(Drink).count() > 0:
        logger.info("Database already seeded, skipping.")
        return

    for drink_data in DRINKS:
        db.add(Drink(**drink_data))

    for ing_data in INGREDIENTS:
        db.add(Ingredient(**ing_data))

    db.flush()

    from app.services.queue import compute_priority_score, estimate_wait_time

    active_count = 0
    for order_data in SAMPLE_ORDERS:
        order_time = datetime.utcnow() - timedelta(minutes=order_data["minutes_ago"])
        priority = compute_priority_score(
            order_time=order_time,
            channel=order_data["channel"],
            drink_name=order_data["drink_name"],
            active_orders=[],
        )
        db.add(
            Order(
                customer_name=order_data["customer_name"],
                drink_name=order_data["drink_name"],
                customizations=json.dumps(order_data["customizations"]),
                channel=order_data["channel"],
                order_time=order_time,
                priority_score=priority,
                status=order_data["status"],
                estimated_wait_minutes=estimate_wait_time(active_count),
            )
        )
        if order_data["status"] != "Picked Up":
            active_count += 1

    db.commit()
    logger.info("Seeded %d drinks, %d ingredients, %d sample orders.", len(DRINKS), len(INGREDIENTS), len(SAMPLE_ORDERS))
