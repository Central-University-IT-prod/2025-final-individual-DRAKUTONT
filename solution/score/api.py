from http import HTTPStatus as status

from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from ads_platform import error_schemas
from advertisers import models as advertisers_models
from clients import models as client_models
from score import models, schemas

router = Router(tags=["Advertisers"])


@router.post(
    "",
    response={
        status.OK: schemas.MLScoreOut,
        status.BAD_REQUEST: error_schemas.ValidationError,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
)
def create_or_update_score(request: HttpRequest, payload: schemas.MLScoreIn):
    try:
        obj = models.MLScore.objects.get(
            client=payload.client_id, advertiser=payload.advertiser_id
        )
        obj.score = payload.score
    except models.MLScore.DoesNotExist:
        client = get_object_or_404(client_models.Client, id=payload.client_id)
        advertiser = get_object_or_404(
            advertisers_models.Advertiser,
            id=payload.advertiser_id,
        )

        obj = models.MLScore(
            client=client,
            advertiser=advertiser,
            score=payload.score,
        )
    obj.full_clean()
    obj.save()
    return obj
