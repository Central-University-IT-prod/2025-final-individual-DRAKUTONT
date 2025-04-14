from django.http import HttpRequest
from ninja import Router, errors

from time_emulation import schemas
from time_emulation.cache import get_date, set_date

router = Router(tags=["Time"])


@router.post("/advance", response=schemas.CurrentDay)
def set_data(
    request: HttpRequest,
    payload: schemas.CurrentDay,
):
    if payload.current_date < get_date():
        raise errors.ValidationError(
            errors=["the set date cannot be less than the current one"]
        )
    set_date(payload.current_date)
    return payload
