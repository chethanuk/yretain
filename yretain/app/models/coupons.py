import sqlalchemy
from pydantic import BaseModel

from yretain.app.models.db import metadata, sync_engine

coupons = sqlalchemy.Table(
    "coupons",
    metadata,
    # sqlalchemy.Column("id", sqlalchemy.String, primary_key=True,
    # autoincrement=True, index=True, unique=True, nullable=False),
    sqlalchemy.Column("code", sqlalchemy.String(100),
                      primary_key=True, nullable=False, index=True, unique=True),
    sqlalchemy.Column("message", sqlalchemy.String(255), nullable=False),
    sqlalchemy.Column("expiry_days", sqlalchemy.Integer, nullable=False)
)


class CouponsCreate(BaseModel):
    code: str
    message: str
    expiry_days: int
