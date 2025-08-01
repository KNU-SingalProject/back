from pydantic import BaseModel, constr, Field
from typing import Literal, List, Optional
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

class FacilityReservationRequest(BaseModel):
    facility_id: int
    name: str
    birth: date

class FacilityReservationConfirmRequest(BaseModel):
    facility_id: int
    name: str
    birth: date
    phone: str

class MemberReserveInfo(BaseModel):
    name: str
    birth: date

class FacilityMultiReservationRequest(BaseModel):
    facility_id: int
    members: List[MemberReserveInfo] = Field(..., max_items=4)


# Confirm용 (phone 있음)
class MemberConfirmInfo(MemberReserveInfo):
    phone: Optional[str] = None

class FacilityMultiReservationConfirmRequest(BaseModel):
    facility_id: int
    members: List[MemberConfirmInfo] = Field(..., max_items=4)