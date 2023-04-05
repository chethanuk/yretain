from datetime import datetime

import sqlalchemy
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Table

from yretain.app.models.db import metadata

customers = Table(
    "customers",
    metadata,
    Column("phone_number", sqlalchemy.String(10), primary_key=True,
           nullable=False, unique=True),
    Column("name", sqlalchemy.String(200), nullable=False),
    Column("email", sqlalchemy.String(200), nullable=False),
    Column("city", sqlalchemy.String(200), nullable=False)
)


class Customers(BaseModel):
    phone_number: str
    name: str
    email: str
    city: str


customers_activity = Table(
    "customers_activity",
    metadata,
    Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    Column("phone_number", sqlalchemy.String(200), nullable=False),
    # Column("is_weekly", sqlalchemy.Boolean, nullable=False),
    # Column("is_food", sqlalchemy.Boolean, nullable=False),
    # Column("is_delivery", sqlalchemy.Boolean, nullable=False),
    Column("updated", sqlalchemy.DATETIME, nullable=False),
)


class CustomersActivityCreate(BaseModel):
    phone_number: str

    updated: datetime = Field(default_factory=datetime.utcnow)
    # is_taxi: bool = True
    # is_food: bool = False
    # is_delivery: bool = False


class CustomersActivity(CustomersActivityCreate):
    id: int
#


reports = Table(
    "reports",
    metadata,
    Column("name", sqlalchemy.String(200), primary_key=True,
           nullable=False, unique=True),
    Column("is_weekly", sqlalchemy.Boolean, nullable=False),
    Column("is_monthly", sqlalchemy.Boolean, nullable=False),
)


class ReportFormat(BaseModel):
    name: str
    is_weekly: bool = False
    is_monthly: bool = False
