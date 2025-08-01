from pydantic import BaseModel, constr
from typing import Literal
from datetime import date

class SignUpRequest(BaseModel):
    member_id: constr(min_length=1, max_length=10)
    name: constr(min_length=2, max_length=20)
    gender: Literal["male", "female"]
    birth: date
    phone_num: constr(min_length=10, max_length=11)

class LogInRequest(BaseModel):
    name: constr(min_length=2, max_length=20)
    birth: date