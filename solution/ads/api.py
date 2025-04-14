import uuid
from http import HTTPStatus as status

from django.db.models import Q
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from ads import schemas
from ads.score import select_best_campaign
from ads_platform import error_schemas, errors
from advertisers.models import Campaign
from clients.models import Client
from stats import metrics
from time_emulation.cache import get_date

router = Router(tags=["Ads"])


@router.get(
    "",
    response={
        status.OK: schemas.AdsOut,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
)
def get_ads(request: HttpRequest, client_id: uuid.UUID):
    client = get_object_or_404(Client, id=client_id)
    current_date = get_date()

    campaigns = Campaign.objects.filter(
        Q(targeting__isnull=True)
        | (
            Q(targeting__gender__isnull=True)
            | Q(targeting__gender="ALL")
            | Q(targeting__gender=client.gender)
        ),
        (
            Q(targeting__age_from__isnull=True)
            | Q(targeting__age_from__lte=client.age)
        ),
        (
            Q(targeting__age_to__isnull=True)
            | Q(targeting__age_to__gte=client.age)
        ),
        (
            Q(targeting__location__isnull=True)
            | Q(targeting__location__exact=client.location)
        ),
        start_date__lte=current_date,
        end_date__gte=current_date,
    )

    if not campaigns:
        return status.NOT_FOUND, error_schemas.NotFoundError()

    best_campaign = select_best_campaign(client, campaigns, current_date)

    if not best_campaign:
        return status.NOT_FOUND, error_schemas.NotFoundError()

    best_campaign.impressions_count += 1
    best_campaign.impressions.add(
        client,
        through_defaults={
            "date": current_date,
            "cost": best_campaign.cost_per_impression,
        },
    )
    best_campaign.save()

    metrics.campaign_impressions.labels(campaign_id=best_campaign.id).inc(1)
    metrics.campaign_daily_impressions.labels(
        campaign_id=best_campaign.id,
        date=get_date(),
    ).inc(1)

    metrics.advertiser_impressions.labels(
        advertiser_id=best_campaign.advertiser.id
    ).inc(1)
    metrics.advertiser_daily_impressions.labels(
        advertiser_id=best_campaign.advertiser.id,
        date=get_date(),
    ).inc(1)

    return best_campaign


@router.post(
    "/{ad_id}/click",
    response={
        status.NO_CONTENT: None,
        status.BAD_REQUEST: error_schemas.ValidationError,
        status.FORBIDDEN: error_schemas.ForbiddenError,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
)
def click(
    request: HttpRequest,
    ad_id: uuid.UUID,
    payload: schemas.AdsClickIn,
):
    campaign = get_object_or_404(Campaign, id=ad_id)
    client = get_object_or_404(Client, id=payload.client_id)

    if client not in campaign.impressions.all():
        raise errors.ForbiddenError()  # noqa: RSE102

    if client not in campaign.clicks.all():
        campaign.clicks_count += 1
        campaign.clicks.add(
            client,
            through_defaults={
                "date": get_date(),
                "cost": campaign.cost_per_click,
            },
        )
        campaign.save()
        metrics.campaign_impressions.labels(campaign_id=ad_id).inc(1)
        metrics.campaign_daily_clicks.labels(
            campaign_id=ad_id,
            date=get_date(),
        ).inc(1)

    return status.NO_CONTENT, None
