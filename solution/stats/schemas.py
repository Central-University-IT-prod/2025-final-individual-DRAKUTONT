from ninja import Schema
from pydantic import computed_field


class BaseStat(Schema):
    impressions_count: int
    clicks_count: int
    spent_impressions: float
    spent_clicks: float

    @computed_field
    @property
    def conversion(self) -> float:
        if self.impressions_count > 0:
            return round(self.clicks_count / self.impressions_count * 100, 2)
        return 0

    @computed_field
    @property
    def spent_total(self) -> float:
        return self.spent_impressions + self.spent_clicks


class CampaignStat(BaseStat): ...


class CampaignStatDaily(BaseStat):
    date: int


class AdvertiserCampaignStat(BaseStat): ...


class AdvertiserCampaignStatDaily(BaseStat):
    date: int
