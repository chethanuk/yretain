from pydantic import BaseModel


class Coupons(BaseModel):
    id: int
    code: str
    message: float
    expiry_days: int

