import uuid
from http import HTTPStatus as status

from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from ninja import Router

from ads_platform import error_schemas
from clients import models, schemas

router = Router(tags=["Clients"])


@router.post(
    "/bulk",
    response={
        status.CREATED: list[schemas.ClientOut],
        status.BAD_REQUEST: error_schemas.ValidationError,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
    description=(
        "Создание и обновление клиентов. "
        "Создаются только валидные сущности"
    ),
)
def create_or_update_clients(
    request: HttpRequest, payload: list[schemas.ClientIn]
):
    clients = []

    for client in payload:
        obj = models.Client(
            id=client.client_id,
            **client.dict(exclude="client_id"),
        )
        try:
            obj.full_clean(validate_constraints=False, validate_unique=False)
            clients.append(obj)
        except ValidationError:
            continue

    return status.CREATED, models.Client.objects.bulk_create(
        clients,
        update_conflicts=True,
        unique_fields=["id"],
        update_fields=["login", "age", "location", "gender"],
    )


@router.get(
    "/{client_id}",
    response={
        status.OK: schemas.ClientOut,
        status.NOT_FOUND: error_schemas.NotFoundError,
    },
    exclude_none=True,
)
def get_client(request: HttpRequest, client_id: uuid.UUID):
    return get_object_or_404(models.Client, id=client_id)
