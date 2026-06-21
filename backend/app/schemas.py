"""Pydantic schemas for request/response validation."""

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator

OrderChannel = Literal["mobile", "drive-thru", "walk-in"]
OrderStatus = Literal["Received", "In Progress", "Ready", "Picked Up"]
DrinkSize = Literal["tall", "grande", "venti"]
MilkType = Literal["whole milk", "almond milk", "oat milk", "nonfat milk"]


class DrinkResponse(BaseModel):
    id: int
    name: str
    description: str
    base_calories: float
    base_sugar: float
    base_protein: float
    base_caffeine: float

    model_config = {"from_attributes": True}


class IngredientResponse(BaseModel):
    id: int
    name: str
    category: str
    calories_delta: float
    sugar_delta: float
    protein_delta: float
    caffeine_delta: float

    model_config = {"from_attributes": True}


class CustomizeDrinkRequest(BaseModel):
    drink_id: int
    size: DrinkSize = "grande"
    milk_type: MilkType = "whole milk"
    vanilla_pumps: int = Field(default=0, ge=0, le=12)
    caramel_pumps: int = Field(default=0, ge=0, le=12)
    mocha_pumps: int = Field(default=0, ge=0, le=12)
    whipped_cream: bool = False
    protein_boost: bool = False
    extra_espresso_shot: bool = False


class NutritionResponse(BaseModel):
    calories: float
    sugar: float
    protein: float
    caffeine: float
    summary: str


class CustomizeDrinkResponse(BaseModel):
    drink_name: str
    size: str
    customizations: dict
    nutrition: NutritionResponse


class OrderCreate(BaseModel):
    customer_name: str = Field(..., min_length=1, max_length=100)
    drink_id: int
    size: DrinkSize = "grande"
    milk_type: MilkType = "whole milk"
    vanilla_pumps: int = Field(default=0, ge=0, le=12)
    caramel_pumps: int = Field(default=0, ge=0, le=12)
    mocha_pumps: int = Field(default=0, ge=0, le=12)
    whipped_cream: bool = False
    protein_boost: bool = False
    extra_espresso_shot: bool = False
    channel: OrderChannel

    @field_validator("customer_name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        return v.strip()


class OrderResponse(BaseModel):
    id: int
    customer_name: str
    drink_name: str
    customizations: dict
    channel: str
    order_time: datetime
    priority_score: float
    status: str
    estimated_wait_minutes: float
    queue_position: Optional[int] = None

    model_config = {"from_attributes": True}


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class QueueStatusResponse(BaseModel):
    total_in_queue: int
    orders: list[OrderResponse]
    rush_detected: bool
    rush_message: Optional[str] = None
    average_wait_minutes: float


class RushAnalyticsResponse(BaseModel):
    rush_detected: bool
    orders_last_10_minutes: int
    message: str
    threshold: int = 12


class AnalyticsDashboardResponse(BaseModel):
    total_orders: int
    average_wait_minutes: float
    orders_by_channel: dict[str, int]
    rush_detected: bool
    rush_message: Optional[str] = None
    active_queue_size: int
