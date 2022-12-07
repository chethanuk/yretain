from datetime import datetime

from pydantic import BaseModel, Field


class Customers(BaseModel):
    id: int
    name: str
    email: str
    phone_number: int
    city: str


class CustomersActivity(BaseModel):
    id: int
    phone_number: str
    is_taxi: bool = True
    is_food: bool = False
    is_delivery: bool = False
    updated: datetime = Field(default_factory=datetime.utcnow)


class ReportFormat(BaseModel):
    is_weekly: bool = False
    is_monthly: bool = False
