from http import HTTPStatus as status
from django import test
from advertisers.models import Campaign, Advertiser, Impression, Click
from clients.models import Client
from time_emulation.cache import get_date
import uuid


class StatsTest(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        self.stats_prefix = "/stats"

        self.client_data = {
            "client_id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
            "login": "user1",
            "age": 25,
            "location": "Moscow",
            "gender": "MALE",
        }
        self.advertiser_data = {
            "advertiser_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "advertiser1",
        }
        self.campaign_data = {
            "targeting": {
                "gender": "MALE",
                "age_from": 20,
                "age_to": 30,
                "location": "Moscow",
            },
            "impressions_limit": 10,
            "clicks_limit": 5,
            "cost_per_impression": 0.1,
            "cost_per_click": 1.0,
            "ad_title": "Test Ad",
            "ad_text": "Test Text",
            "start_date": get_date(),
            "end_date": get_date() + 5,
        }

        self.client.post(
            "/clients/bulk",
            data=[self.client_data],
            content_type="application/json",
        )
        self.client.post(
            "/advertisers/bulk",
            data=[self.advertiser_data],
            content_type="application/json",
        )
        response = self.client.post(
            f"/advertisers/{self.advertiser_data['advertiser_id']}/campaigns",
            data=self.campaign_data,
            content_type="application/json",
        )
        self.campaign_id = response.json()["campaign_id"]

        campaign = Campaign.objects.get(id=self.campaign_id)
        client = Client.objects.get(id=self.client_data["client_id"])
        day1 = get_date()
        day2 = day1 + 1
        day3 = day1 + 2

        Impression.objects.create(
            client=client,
            campaign=campaign,
            date=day1,
            cost=campaign.cost_per_impression,
        )
        Impression.objects.create(
            client=client,
            campaign=campaign,
            date=day1,
            cost=campaign.cost_per_impression,
        )
        Click.objects.create(
            client=client,
            campaign=campaign,
            date=day1,
            cost=campaign.cost_per_click,
        )

        Impression.objects.create(
            client=client,
            campaign=campaign,
            date=day2,
            cost=campaign.cost_per_impression,
        )
        Click.objects.create(
            client=client,
            campaign=campaign,
            date=day2,
            cost=campaign.cost_per_click,
        )
        Click.objects.create(
            client=client,
            campaign=campaign,
            date=day2,
            cost=campaign.cost_per_click,
        )

        campaign.impressions_count = 3
        campaign.clicks_count = 3
        campaign.save()

    def test_get_campaign_stat(self):
        response = self.client.get(
            f"{self.stats_prefix}/campaigns/{self.campaign_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(response.json()["impressions_count"], 3)
        self.assertEqual(response.json()["clicks_count"], 3)
        self.assertEqual(round(response.json()["spent_impressions"], 2), 0.3)
        self.assertEqual(response.json()["spent_clicks"], 3.0)

    def test_get_campaign_stat_no_impressions_clicks(self):
        new_campaign_data = {**self.campaign_data, "ad_title": "Empty Ad"}
        response = self.client.post(
            f"/advertisers/{self.advertiser_data['advertiser_id']}/campaigns",
            data=new_campaign_data,
            content_type="application/json",
        )
        new_campaign_id = response.json()["campaign_id"]

        response = self.client.get(
            f"{self.stats_prefix}/campaigns/{new_campaign_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(response.json()["impressions_count"], 0)
        self.assertEqual(response.json()["clicks_count"], 0)
        self.assertEqual(response.json()["spent_impressions"], 0.0)
        self.assertEqual(response.json()["spent_clicks"], 0.0)

    def test_get_invalid_campaign_id(self):
        invalid_id = "invalid-id"
        response = self.client.get(
            f"{self.stats_prefix}/campaigns/{invalid_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_nonexistent_campaign_stat(self):
        nonexistent_id = str(uuid.uuid4())
        response = self.client.get(
            f"{self.stats_prefix}/campaigns/{nonexistent_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.NOT_FOUND)

    def test_get_advertiser_stat(self):
        response = self.client.get(
            f"{self.stats_prefix}/advertisers/{self.advertiser_data['advertiser_id']}/campaigns",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(response.json()["impressions_count"], 3)
        self.assertEqual(response.json()["clicks_count"], 3)
        self.assertEqual(round(response.json()["spent_impressions"], 2), 0.3)
        self.assertEqual(response.json()["spent_clicks"], 3.0)

    def test_get_advertiser_stat_no_campaigns(self):
        new_advertiser = {
            "advertiser_id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "advertiser2",
        }
        self.client.post(
            "/advertisers/bulk",
            data=[new_advertiser],
            content_type="application/json",
        )

        response = self.client.get(
            f"{self.stats_prefix}/advertisers/{new_advertiser['advertiser_id']}/campaigns",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(response.json()["impressions_count"], 0)
        self.assertEqual(response.json()["clicks_count"], 0)
        self.assertEqual(response.json()["spent_impressions"], 0.0)
        self.assertEqual(response.json()["spent_clicks"], 0.0)

    def test_get_invalid_advertiser_id(self):
        invalid_id = "invalid-id"
        response = self.client.get(
            f"{self.stats_prefix}/advertisers/{invalid_id}/campaigns",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_campaign_daily_stat(self):
        response = self.client.get(
            f"{self.stats_prefix}/campaigns/{self.campaign_id}/daily",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        data = response.json()
        self.assertEqual(len(data), 2)

        day1_data = next(item for item in data if item["date"] == get_date())
        self.assertEqual(day1_data["impressions_count"], 2)
        self.assertEqual(day1_data["clicks_count"], 1)
        self.assertEqual(round(day1_data["spent_impressions"], 2), 0.2)
        self.assertEqual(day1_data["spent_clicks"], 1.0)

        # Проверяем день 2
        day2_data = next(
            item for item in data if item["date"] == (get_date() + 1)
        )
        self.assertEqual(day2_data["impressions_count"], 1)
        self.assertEqual(day2_data["clicks_count"], 2)
        self.assertEqual(round(day2_data["spent_impressions"], 2), 0.1)
        self.assertEqual(day2_data["spent_clicks"], 2.0)

    def test_get_campaign_daily_stat_no_data(self):
        # Создаем новую кампанию без показов и кликов
        new_campaign_data = {**self.campaign_data, "ad_title": "Empty Ad"}
        response = self.client.post(
            f"/advertisers/{self.advertiser_data['advertiser_id']}/campaigns",
            data=new_campaign_data,
            content_type="application/json",
        )
        new_campaign_id = response.json()["campaign_id"]

        response = self.client.get(
            f"{self.stats_prefix}/campaigns/{new_campaign_id}/daily",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(len(response.json()), 0)

    def test_get_invalid_campaign_id_daily(self):
        invalid_id = "invalid-id"
        response = self.client.get(
            f"{self.stats_prefix}/campaigns/{invalid_id}/daily",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_nonexistent_campaign_daily_stat(self):
        nonexistent_id = str(uuid.uuid4())
        response = self.client.get(
            f"{self.stats_prefix}/campaigns/{nonexistent_id}/daily",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.NOT_FOUND)

    def test_get_advertiser_daily_stat(self):
        response = self.client.get(
            f"{self.stats_prefix}/advertisers/{self.advertiser_data['advertiser_id']}/campaigns/daily",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        data = response.json()
        self.assertEqual(len(data), 2)

        day1_data = next(item for item in data if item["date"] == get_date())
        self.assertEqual(day1_data["impressions_count"], 2)
        self.assertEqual(day1_data["clicks_count"], 1)
        self.assertEqual(round(day1_data["spent_impressions"], 2), 0.2)
        self.assertEqual(day1_data["spent_clicks"], 1.0)

        day2_data = next(
            item for item in data if item["date"] == (get_date() + 1)
        )
        self.assertEqual(day2_data["impressions_count"], 1)
        self.assertEqual(day2_data["clicks_count"], 2)
        self.assertEqual(round(day2_data["spent_impressions"], 2), 0.1)
        self.assertEqual(day2_data["spent_clicks"], 2.0)

    def test_get_advertiser_daily_stat_no_campaigns(self):
        new_advertiser = {
            "advertiser_id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
            "name": "advertiser2",
        }
        self.client.post(
            "/advertisers/bulk",
            data=[new_advertiser],
            content_type="application/json",
        )

        response = self.client.get(
            f"{self.stats_prefix}/advertisers/{new_advertiser['advertiser_id']}/campaigns/daily",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(len(response.json()), 0)

    def test_get_invalid_advertiser_id_daily(self):
        invalid_id = "invalid-id"
        response = self.client.get(
            f"{self.stats_prefix}/advertisers/{invalid_id}/campaigns/daily",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)
