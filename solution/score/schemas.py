import uuid

from ninja import Field, ModelSchema

from score import models


class MLScoreIn(ModelSchema):
    advertiser_id: uuid.UUID
    client_id: uuid.UUID

    class Meta:
        model = models.MLScore
        fields = ["score"]


class MLScoreOut(ModelSchema):
    advertiser_id: uuid.UUID = Field(..., alias="advertiser.id")
    client_id: uuid.UUID = Field(..., alias="client.id")

    class Meta:
        model = models.MLScore
        fields = ["score"]
