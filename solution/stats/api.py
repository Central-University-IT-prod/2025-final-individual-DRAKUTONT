import uuid
from collections import defaultdict
from http import HTTPStatus as status

from django.db.models import Count, Sum
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from ads_platform import error_schemas
from advertisers.models import Advertiser, Campaign, Click, Impression
from stats import schemas

router = Router(tags=["Statistics"])


@router.get(
    "/campaigns/{campaign_id}",
    response={
        status.OK: schemas.CampaignStat,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
)
def get_campaign_stat(request: HttpRequest, campaign_id: uuid.UUID):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    impressions = Impression.objects.filter(campaign=campaign)
    clicks = Click.objects.filter(campaign=campaign)

    campaign.spent_impressions = impressions.aggregate(Sum("cost", default=0))[
        "cost__sum"
    ]
    campaign.spent_clicks = clicks.aggregate(Sum("cost", default=0))[
        "cost__sum"
    ]

    return campaign


@router.get(
    "/advertisers/{advertiser_id}/campaigns",
    response={
        status.OK: schemas.AdvertiserCampaignStat,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
)
def get_advertiser_stat(request: HttpRequest, advertiser_id: uuid.UUID):
    advertiser = get_object_or_404(Advertiser, id=advertiser_id)
    campaigns = Campaign.objects.filter(advertiser=advertiser)

    impressions = Impression.objects.filter(campaign__in=campaigns)
    clicks = Click.objects.filter(campaign__in=campaigns)

    impressions_count = impressions.count()
    clicks_count = clicks.count()

    spent_impressions = impressions.aggregate(Sum("cost", default=0))[
        "cost__sum"
    ]
    spent_clicks = clicks.aggregate(Sum("cost", default=0))["cost__sum"]
    return schemas.AdvertiserCampaignStat(
        impressions_count=impressions_count,
        clicks_count=clicks_count,
        spent_impressions=spent_impressions,
        spent_clicks=spent_clicks,
    )


@router.get(
    "/campaigns/{campaign_id}/daily",
    response={
        status.OK: list[schemas.CampaignStatDaily],
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
)
def get_campaign_stat_daily(request: HttpRequest, campaign_id: uuid.UUID):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    impressions = Impression.objects.filter(campaign=campaign)
    clicks = Click.objects.filter(campaign=campaign)

    impressions_days = (
        impressions.values("date")
        .order_by("date")
        .annotate(
            impressions_count=Count("id"), total_impressions_sum=Sum("cost")
        )
    )
    clicks_days = (
        clicks.values("date")
        .order_by("date")
        .annotate(click_count=Count("id"), total_click_sum=Sum("cost"))
    )

    result = defaultdict(
        lambda: {
            "impressions_count": 0,
            "clicks_count": 0,
            "spent_impressions": 0.0,
            "spent_clicks":  0.0
        }
    )

    for entry in impressions_days:
        date = entry["date"]
        result[date]["impressions_count"] += entry["impressions_count"]
        result[date]["spent_impressions"] += entry["total_impressions_sum"]

    for entry in clicks_days:
        date = entry["date"]
        result[date]["clicks_count"] += entry["click_count"]
        result[date]["spent_clicks"] += entry["total_click_sum"]

    result = dict(result)

    response = []
    for date, data in result.items():
        response.append(
            schemas.CampaignStatDaily(
                impressions_count=data["impressions_count"],
                clicks_count=data["clicks_count"],
                spent_clicks=data["spent_clicks"],
                spent_impressions=data["spent_impressions"],
                date=date,
            )
        )

    return response


@router.get(
    "/advertisers/{advertiser_id}/campaigns/daily",
    response={
        status.OK: list[schemas.CampaignStatDaily],
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
)
def get_advertiser_stat_daily(request: HttpRequest, advertiser_id: uuid.UUID):
    advertiser = get_object_or_404(Advertiser, id=advertiser_id)
    campaigns = Campaign.objects.filter(advertiser=advertiser)

    impressions = Impression.objects.filter(campaign__in=campaigns)
    clicks = Click.objects.filter(campaign__in=campaigns)

    impressions_days = (
        impressions.values("date")
        .order_by("date")
        .annotate(
            impressions_count=Count("id"), total_impressions_sum=Sum("cost")
        )
    )
    clicks_days = (
        clicks.values("date")
        .order_by("date")
        .annotate(click_count=Count("id"), total_click_sum=Sum("cost"))
    )

    result = defaultdict(
        lambda: {
            "impressions_count": 0,
            "clicks_count": 0,
            "spent_impressions": 0.0,
            "spent_clicks": 0.0,
        }
    )

    for entry in impressions_days:
        date = entry["date"]
        result[date]["impressions_count"] += entry["impressions_count"]
        result[date]["spent_impressions"] += entry["total_impressions_sum"]

    for entry in clicks_days:
        date = entry["date"]
        result[date]["clicks_count"] += entry["click_count"]
        result[date]["spent_clicks"] += entry["total_click_sum"]

    result = dict(result)

    response = []
    for date, data in result.items():
        response.append(
            schemas.CampaignStatDaily(
                impressions_count=data["impressions_count"],
                clicks_count=data["clicks_count"],
                spent_clicks=data["spent_clicks"],
                spent_impressions=data["spent_impressions"],
                date=date,
            )
        )

    return response
