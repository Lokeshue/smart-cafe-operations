"""SQLAlchemy ORM models for drinks, ingredients, and orders."""

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Drink(Base):
    """Base drink menu item with per-size nutrition values."""

    __tablename__ = "drinks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    # Base nutrition for grande size (used as reference; tall/venti scaled)
    base_calories: Mapped[float] = mapped_column(Float, default=0)
    base_sugar: Mapped[float] = mapped_column(Float, default=0)
    base_protein: Mapped[float] = mapped_column(Float, default=0)
    base_caffeine: Mapped[float] = mapped_column(Float, default=0)


class Ingredient(Base):
    """Customization ingredient with nutrition deltas."""

    __tablename__ = "ingredients"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # milk, syrup, addon
    calories_delta: Mapped[float] = mapped_column(Float, default=0)
    sugar_delta: Mapped[float] = mapped_column(Float, default=0)
    protein_delta: Mapped[float] = mapped_column(Float, default=0)
    caffeine_delta: Mapped[float] = mapped_column(Float, default=0)


class Order(Base):
    """Customer order in the barista queue."""

    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    drink_name: Mapped[str] = mapped_column(String(100), nullable=False)
    customizations: Mapped[str] = mapped_column(Text, default="{}")  # JSON string
    channel: Mapped[str] = mapped_column(String(20), nullable=False)  # mobile, drive-thru, walk-in
    order_time: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    priority_score: Mapped[float] = mapped_column(Float, default=0)
    status: Mapped[str] = mapped_column(String(20), default="Received")
    estimated_wait_minutes: Mapped[float] = mapped_column(Float, default=0)
