import uuid

from ninja import Field, ModelSchema, Schema

from advertisers.models import Campaign


class AdsOut(ModelSchema):
    ad_id: uuid.UUID = Field(..., alias="id")
    advertiser_id: uuid.UUID = Field(..., alias="advertiser.id")

    class Meta:
        model = Campaign
        fields = ["ad_title", "ad_text"]


class AdsClickIn(Schema):
    client_id: uuid.UUID
