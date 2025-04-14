import uuid

from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models

from time_emulation.cache import get_date


class Advertiser(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    name = models.CharField()

    def __str__(self) -> str:
        return self.name


class Targeting(models.Model):
    class Gender(models.TextChoices):
        MALE = "MALE"
        FEMALE = "FEMALE"
        ALL = "ALL"

    gender = models.CharField(  # noqa: DJ001
        choices=Gender.choices,
        null=True,
        blank=True,
    )

    age_from = models.IntegerField(
        blank=True,
        null=True,
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(100),
        ],
    )

    age_to = models.IntegerField(
        blank=True,
        null=True,
        validators=[
            validators.MinValueValidator(0),
            validators.MaxValueValidator(100),
        ],
    )

    location = models.CharField(  # noqa: DJ001
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return f"{self.location}/{self.gender}"

    def clean(self):
        if self.age_from and self.age_to:  # noqa: SIM102
            if self.age_from > self.age_to:
                raise ValidationError(message="age_from > age_to")

        return super().clean()


class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)

    impressions_limit = models.IntegerField(
        validators=[
            validators.MinValueValidator(0),
        ]
    )

    impressions_count = models.IntegerField(default=0)

    clicks_limit = models.IntegerField(
        validators=[
            validators.MinValueValidator(0),
        ]
    )

    clicks_count = models.IntegerField(default=0)

    cost_per_impression = models.FloatField(
        validators=[
            validators.MinValueValidator(0),
        ],
    )

    cost_per_click = models.FloatField(
        validators=[
            validators.MinValueValidator(0),
        ],
    )

    ad_title = models.CharField()

    ad_text = models.CharField()

    start_date = models.IntegerField(
        validators=[
            validators.MinValueValidator(0),
        ]
    )

    end_date = models.IntegerField(
        validators=[
            validators.MinValueValidator(0),
        ]
    )

    targeting = models.ForeignKey(
        Targeting,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    advertiser = models.ForeignKey(
        Advertiser,
        on_delete=models.CASCADE,
    )

    is_active = models.BooleanField(default=False)

    impressions = models.ManyToManyField(
        "clients.Client",
        related_name="campaign_impressions",
        through="Impression",
    )
    clicks = models.ManyToManyField(
        "clients.Client",
        related_name="campaign_clicks",
        through="Click",
    )

    image = models.ImageField(
        blank=True,
        null=True,
    )

    def __str__(self) -> str:
        return self.ad_title

    def active_check(self) -> bool:
        if self.start_date <= get_date() <= self.end_date:
            self.is_active = True
        else:
            self.is_active = False

        return self.is_active

    def get_non_editable_fields(self):
        if self.active_check():
            return []

        return [
            "impressions_limit",
            "clicks_limit",
            "start_date",
            "end_date",
        ]

    def clean(self):
        if self.end_date < self.start_date:
            raise ValidationError(message="end_date < start_date")

        if self.end_date < get_date() or self.start_date < get_date():
            raise ValidationError(
                message="the campaign cannot start/end in the past"
            )

        if self.clicks_limit > self.impressions_limit:
            raise ValidationError(
                message="clicks_limit > impressions_limit"
            )
        self.active_check()


class Click(models.Model):
    client = models.ForeignKey(
        "clients.Client",
        related_name="click_client",
        on_delete=models.CASCADE,
    )

    campaign = models.ForeignKey(
        Campaign,
        related_name="click_campaign",
        on_delete=models.CASCADE,
    )

    date = models.IntegerField(default=0)
    cost = models.FloatField(
        validators=[
            validators.MinValueValidator(0),
        ],
    )

    def __str__(self) -> str:
        return f"{self.client.login} - {self.campaign.ad_title}"


class Impression(models.Model):
    client = models.ForeignKey(
        "clients.Client",
        related_name="impression_client",
        on_delete=models.CASCADE,
    )

    campaign = models.ForeignKey(
        Campaign,
        related_name="impression_campaign",
        on_delete=models.CASCADE,
    )

    date = models.IntegerField(default=0)
    cost = models.FloatField(
        validators=[
            validators.MinValueValidator(0),
        ],
    )

    def __str__(self) -> str:
        return f"{self.client.login} - {self.campaign.ad_title}"
