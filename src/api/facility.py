from fastapi import APIRouter, Depends, Request

from core.di import get_facility_service
from schema.request import FacilityReservationRequest, FacilityMultiReservationRequest, ConfirmUserRequest, \
    FacilityReservationConfirmRequest
from service.facility_service import FacilityService

router = APIRouter(prefix="/facility", tags=["Facility"])

@router.post("/reserve", status_code=201)
async def facility_reservation(
        request: FacilityReservationRequest,
        facility_service: FacilityService = Depends(get_facility_service)
):
    return await facility_service.reservation(request)

@router.post("/confirm", status_code=201)
async def facility_reservation_confirm(
        request: FacilityReservationConfirmRequest,
        facility_service: FacilityService = Depends(get_facility_service)
):
    return await facility_service.reserve_confirm(request)

@router.post("/reserve/multi/check", status_code=200)
async def check_multi_reservation_users(
        request: FacilityMultiReservationRequest,
        facility_service: FacilityService = Depends(get_facility_service)
):
    return await facility_service.check_multi_users_before_reservation(request)
