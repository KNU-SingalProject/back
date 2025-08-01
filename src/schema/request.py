from pydantic import BaseModel, constr
from typing import Literal, List
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

# 다중 예약 (여러 명 name + birth)
class MultiUserInfo(BaseModel):
    name: str
    birth: date

class FacilityMultiReservationRequest(BaseModel):
    facility_id: int
    users: List[MultiUserInfo]

# 전화번호 선택 후 예약 확정 (member_id 사용)
class ConfirmUserRequest(BaseModel):
    facility_id: int
    member_ids: List[str]