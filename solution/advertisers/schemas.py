import uuid

from ninja import Field, ModelSchema, Schema

from advertisers import models


class AdvertiserIn(ModelSchema):
    advertiser_id: uuid.UUID

    class Meta:
        model = models.Advertiser
        fields = ["name"]


class AdvertiserOut(ModelSchema):
    advertiser_id: uuid.UUID = Field(..., alias="id")

    class Meta:
        model = models.Advertiser
        fields = ["name"]


class Targeting(ModelSchema):
    class Meta:
        model = models.Targeting
        fields = [
            "gender",
            "age_from",
            "age_to",
            "location",
        ]


class CampaignIn(ModelSchema):
    targeting: None | Targeting = None

    class Meta:
        model = models.Campaign
        fields = [
            "impressions_limit",
            "clicks_limit",
            "cost_per_impression",
            "cost_per_click",
            "ad_title",
            "ad_text",
            "start_date",
            "end_date",
        ]


class CampaignOut(ModelSchema):
    campaign_id: uuid.UUID = Field(..., alias="id")
    advertiser_id: uuid.UUID = Field(..., alias="advertiser.id")

    targeting: None | Targeting = None

    class Meta:
        model = models.Campaign
        fields = [
            "impressions_limit",
            "clicks_limit",
            "cost_per_impression",
            "cost_per_click",
            "ad_title",
            "ad_text",
            "start_date",
            "end_date",
            "image",
        ]


class CampaignPadination(Schema):
    size: int = Field(10, gt=0)
    page: int = Field(1, gt=0)


class CampaignGenerationIn(Schema):
    product_name: str
    target_action: str
    target_audience: str


class CampaignGenerationOut(Schema):
    text: str
