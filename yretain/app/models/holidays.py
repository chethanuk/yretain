from datetime import datetime

import sqlalchemy
from pydantic import BaseModel, Field, validator
from sqlalchemy import Column, Table
from yretain.app.models.db import metadata

holidays = sqlalchemy.Table(
    "holidays",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, autoincrement=True),
    sqlalchemy.Column("name", sqlalchemy.String(200), nullable=False),
    sqlalchemy.Column("date", sqlalchemy.Date, nullable=False),
    sqlalchemy.Column("country", sqlalchemy.String(2), nullable=False),
    sqlalchemy.Column("year", sqlalchemy.Integer, nullable=False),
    sqlalchemy.Column("public", sqlalchemy.Boolean, nullable=False),
)


class HolidayCreate(BaseModel):
    name: str
    date: str
    country: str
    year: int
    public: bool


class Holiday(HolidayCreate):
    id: int


