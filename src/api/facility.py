from fastapi import APIRouter, Depends, Request

from core.di import get_facility_service
from schema.request import FacilityReservationRequest
from service.facility_service import FacilityService

router = APIRouter(prefix="/facility", tags=["Facility"])

@router.post("/reserve", status_code=201)
async def facility_reservation(
        request: FacilityReservationRequest,
        facility_service: FacilityService = Depends(get_facility_service)
):
    return await facility_service.reservation(request)

@router.get("/reserve", status_code=200)
async def get_reservation_list(
        facility_id: int,
        facility_service: FacilityService = Depends(get_facility_service)
):
    return await facility_service.get_reservation_list(facility_id)