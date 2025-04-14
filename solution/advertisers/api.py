import uuid
from http import HTTPStatus as status

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import File, Query, Router
from ninja import errors as ninja_errors
from ninja.files import UploadedFile

from ads_platform import error_schemas
from advertisers import models, schemas
from ai_tools.cache import get_moderation_mode
from ai_tools.utils import generation_ad_text, moderation_ad_text

router = Router(tags=["Advertisers", "Campaigns"])


@router.post(
    "/bulk",
    response={
        status.CREATED: list[schemas.AdvertiserOut],
        status.BAD_REQUEST: error_schemas.ValidationError,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
    tags=["Advertisers"],
    description=(
        "Создание и обновление рекламодателей. "
        "Создаются только валидные сущности"
    ),
)
def create_or_update_advertiser(
    request: HttpRequest, payload: list[schemas.AdvertiserIn]
):
    advertisers = []

    for advertiser in payload:
        obj = models.Advertiser(
            id=advertiser.advertiser_id,
            **advertiser.dict(exclude="advertiser_id"),
        )

        try:
            obj.full_clean(validate_constraints=False, validate_unique=False)
            advertisers.append(obj)
        except ValidationError:
            continue

    return status.CREATED, models.Advertiser.objects.bulk_create(
        advertisers,
        update_conflicts=True,
        unique_fields=["id"],
        update_fields=["name"],
    )


@router.get(
    "/{advertiser_id}",
    response={
        status.OK: schemas.AdvertiserOut,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
    tags=["Advertisers"],
)
def get_advertiser(request: HttpRequest, advertiser_id: uuid.UUID):
    return get_object_or_404(models.Advertiser, id=advertiser_id)


@router.post(
    "/{advertiser_id}/campaigns",
    response={
        status.CREATED: schemas.CampaignOut,
        status.BAD_REQUEST: error_schemas.ValidationError,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
    tags=["Campaigns"],
)
def create_campaign(
    request: HttpRequest, advertiser_id: uuid.UUID, payload: schemas.CampaignIn
):
    advertiser = get_object_or_404(models.Advertiser, id=advertiser_id)

    if get_moderation_mode():  # noqa: SIM102
        if not moderation_ad_text(ad_text=payload.ad_text):
            raise ninja_errors.ValidationError(
                errors=[
                    "The text of the advertisement did not pass moderation"
                ]
            )

    if payload.targeting:
        targeting = models.Targeting(**payload.targeting.dict())
        targeting.full_clean()
        targeting.save()

    else:
        targeting = None

    campaign = models.Campaign(
        **payload.dict(exclude="targeting"),
        targeting=targeting,
        advertiser=advertiser,
    )
    campaign.full_clean()
    campaign.save()

    return status.CREATED, campaign


@router.get(
    "/{advertiser_id}/campaigns",
    response={
        status.OK: list[schemas.CampaignOut],
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
    tags=["Campaigns"],
)
def get_campaigns(
    request: HttpRequest,
    advertiser_id: uuid.UUID,
    filters: schemas.CampaignPadination = Query(...),  # noqa: B008
):
    advertiser = get_object_or_404(models.Advertiser, id=advertiser_id)
    offset = (filters.page - 1) * filters.size

    return models.Campaign.objects.filter(advertiser=advertiser)[
        offset : offset + filters.size
    ]


@router.post(
    "/{advertiser_id}/campaigns/generation",
    response={
        status.OK: schemas.CampaignGenerationOut,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
    tags=["Campaigns"],
)
def generate_campaign_text(
    request: HttpRequest,
    advertiser_id: uuid.UUID,
    payload: schemas.CampaignGenerationIn,
):
    return schemas.CampaignGenerationOut(
        text=generation_ad_text(**payload.dict())
    )


@router.get(
    "/{advertiser_id}/campaigns/{campaign_id}",
    response={
        status.OK: schemas.CampaignOut,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
    tags=["Campaigns"],
)
def get_campaign(
    request: HttpRequest,
    advertiser_id: uuid.UUID,
    campaign_id: uuid.UUID,
):
    advertiser = get_object_or_404(models.Advertiser, id=advertiser_id)
    return get_object_or_404(
        models.Campaign, id=campaign_id, advertiser=advertiser
    )


@router.put(
    "/{advertiser_id}/campaigns/{campaign_id}",
    response={
        status.OK: schemas.CampaignOut,
        status.BAD_REQUEST: error_schemas.ValidationError,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    tags=["Campaigns"],
)
def update_campaign(
    request: HttpRequest,
    advertiser_id: uuid.UUID,
    campaign_id: uuid.UUID,
    payload: schemas.CampaignIn,
):
    advertiser = get_object_or_404(models.Advertiser, id=advertiser_id)
    campaign = get_object_or_404(
        models.Campaign, id=campaign_id, advertiser=advertiser
    )
    if payload.ad_text and get_moderation_mode():  # noqa: SIM102
        if not moderation_ad_text(ad_text=payload.ad_text):
            raise ninja_errors.ValidationError(
                errors=[
                    "The text of the advertisement did not pass moderation"
                ]
            )

    for attr, value in payload.dict().items():
        if attr == "targeting" and value is not None:
            targeting = models.Targeting(**value)
            targeting.full_clean()
            targeting.save()

            value = targeting  # noqa: PLW2901

        if attr in campaign.get_non_editable_fields():
            continue

        setattr(campaign, attr, value)
    campaign.full_clean()
    campaign.save()

    return campaign


@router.post(
    "/{advertiser_id}/campaigns/{campaign_id}/upload",
    response={
        status.CREATED: schemas.CampaignOut,
        status.BAD_REQUEST: error_schemas.ValidationError,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    tags=["Campaigns"],
)
def upload_campaign_image(
    request: HttpRequest,
    advertiser_id: uuid.UUID,
    campaign_id: uuid.UUID,
    image: File[UploadedFile],
):
    advertiser = get_object_or_404(models.Advertiser, id=advertiser_id)
    campaign = get_object_or_404(
        models.Campaign, id=campaign_id, advertiser=advertiser
    )

    campaign.image = image
    campaign.save()

    return status.CREATED, campaign


@router.delete(
    "/{advertiser_id}/campaigns/{campaign_id}",
    response={
        status.NO_CONTENT: dict,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
    tags=["Campaigns"],
)
def delete_campaign(
    request: HttpRequest,
    advertiser_id: uuid.UUID,
    campaign_id: uuid.UUID,
):
    advertiser = get_object_or_404(models.Advertiser, id=advertiser_id)
    campaign = get_object_or_404(
        models.Campaign, id=campaign_id, advertiser=advertiser
    )
    campaign.delete()

    return status.NO_CONTENT, {"status": "success"}
