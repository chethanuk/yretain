from pydantic import BaseModel


class Users(BaseModel):
    id: int
    name: str
    email: str
    phone: int
