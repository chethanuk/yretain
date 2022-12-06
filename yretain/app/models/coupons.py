from pydantic import BaseModel


class Coupons(BaseModel):
    id: int
    code: str
    message: str
    expiry_days: int

