import uuid

from ninja import Field, ModelSchema

from clients.models import Client


class ClientIn(ModelSchema):
    client_id: uuid.UUID

    class Meta:
        model = Client
        fields = [
            "login",
            "age",
            "location",
            "gender",
        ]


class ClientOut(ModelSchema):
    client_id: uuid.UUID = Field(..., alias="id")

    class Meta:
        model = Client
        fields = [
            "login",
            "age",
            "location",
            "gender",
        ]
