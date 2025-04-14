from django.core import validators
from django.db import models


class MLScore(models.Model):
    client = models.ForeignKey(
        "clients.Client",
        on_delete=models.CASCADE,
    )
    advertiser = models.ForeignKey(
        "advertisers.Advertiser",
        on_delete=models.CASCADE,
    )

    score = models.IntegerField(
        default=0, validators=[validators.MinValueValidator(0)]
    )

    def __str__(self) -> str:
        return f"{self.client.login}/{self.advertiser.name}/{self.score}"
