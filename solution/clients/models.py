import uuid

from django.core import validators
from django.db import models


class Client(models.Model):
    class Gender(models.TextChoices):
        MALE = "MALE"
        FEMALE = "FEMALE"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    login = models.CharField()

    age = models.IntegerField(
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(100),
        ],
    )

    location = models.CharField()

    gender = models.CharField(
        choices=Gender.choices,
    )

    def __str__(self) -> str:
        return self.login
