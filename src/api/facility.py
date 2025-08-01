from fastapi import APIRouter, Depends, Request

from core.di import get_facility_service
from schema.request import FacilityReservationRequest, FacilityReservationConfirmRequest, \
    FacilityMultiReservationRequest, FacilityMultiReservationConfirmRequest
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

@router.get("/{facility_id}")
async def get_reservations_by_facility(
    facility_id: int,
    facility_service: FacilityService = Depends(get_facility_service)
):
    return await facility_service.get_reservations_by_facility(facility_id)

@router.post("/multi-reserve", status_code=201)
async def facility_multi_reserve(
    request: FacilityMultiReservationRequest,
    facility_service: FacilityService = Depends(get_facility_service)
):
    return await facility_service.multi_reserve(request)


@router.post("/multi-confirm", status_code=201)
async def facility_multi_confirm(
    request: FacilityMultiReservationConfirmRequest,
    facility_service: FacilityService = Depends(get_facility_service)
):
    return await facility_service.multi_confirm(request)