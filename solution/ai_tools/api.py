from django.http import HttpRequest
from ninja import Router

from ai_tools.cache import (
    disable_moderation,
    enable_moderation,
    get_moderation_mode,
)

router = Router(tags=["Moderation"])


@router.post("/enable")
def enable(
    request: HttpRequest,
):
    enable_moderation()
    return "Ok"


@router.post("/disable")
def disable(
    request: HttpRequest,
):
    disable_moderation()
    return "Ok"


@router.get("")
def get_moderation_status(
    request: HttpRequest,
):
    return {"Mode": "enabled" if get_moderation_mode() else "disabled"}
