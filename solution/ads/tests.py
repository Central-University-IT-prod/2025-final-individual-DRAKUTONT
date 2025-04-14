from http import HTTPStatus as status
from django import test
from advertisers.models import Campaign, Impression
from clients.models import Client
from time_emulation.cache import get_date
import uuid


class AdsTest(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        self.prefix = "/ads"

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
        self.campaign_data1 = {
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
            "ad_title": "Test Ad 1",
            "ad_text": "Test Text 1",
            "start_date": get_date(),
            "end_date": get_date() + 5,
        }
        self.campaign_data2 = {
            "targeting": {
                "gender": "MALE",
                "age_from": 20,
                "age_to": 30,
                "location": "Moscow",
            },
            "impressions_limit": 10,
            "clicks_limit": 5,
            "cost_per_impression": 0.2,
            "cost_per_click": 1.5,
            "ad_title": "Test Ad 2",
            "ad_text": "Test Text 2",
            "start_date": get_date(),
            "end_date": get_date() + 5,
        }
        self.ml_score_data1 = {
            "advertiser_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "client_id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
            "score": 80,
        }
        self.ml_score_data2 = {
            "advertiser_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
            "client_id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
            "score": 90,
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
        response1 = self.client.post(
            f"/advertisers/{self.advertiser_data['advertiser_id']}/campaigns",
            data=self.campaign_data1,
            content_type="application/json",
        )
        self.campaign_id1 = response1.json()["campaign_id"]
        response2 = self.client.post(
            f"/advertisers/{self.advertiser_data['advertiser_id']}/campaigns",
            data=self.campaign_data2,
            content_type="application/json",
        )
        self.campaign_id2 = response2.json()["campaign_id"]
        self.client.post(
            "/ml-scores",
            data=self.ml_score_data1,
            content_type="application/json",
        )
        advertiser2 = {
            "advertiser_id": "4fa85f64-5717-4562-b3fc-2c963f66afa7",
            "name": "advertiser2",
        }
        self.client.post(
            "/advertisers/bulk",
            data=[advertiser2],
            content_type="application/json",
        )
        self.client.post(
            "/ml-scores",
            data=self.ml_score_data2,
            content_type="application/json",
        )

    def test_get_ads_valid(self):
        response = self.client.get(
            f"{self.prefix}?client_id={self.client_data['client_id']}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertIn("ad_id", response.json())
        self.assertIn("ad_title", response.json())
        self.assertIn("ad_text", response.json())
        self.assertIn("advertiser_id", response.json())

    def test_get_ads_invalid_client_id(self):
        invalid_id = "invalid-id"
        response = self.client.get(
            f"{self.prefix}?client_id={invalid_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_ads_no_campaigns(self):
        Campaign.objects.all().delete()
        response = self.client.get(
            f"{self.prefix}?client_id={self.client_data['client_id']}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.NOT_FOUND)

    def test_get_ads_nonexistent_client(self):
        nonexistent_id = str(uuid.uuid4())
        response = self.client.get(
            f"{self.prefix}?client_id={nonexistent_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.NOT_FOUND)

    def test_get_ads_high_score_priority(self):
        response = self.client.get(
            f"{self.prefix}?client_id={self.client_data['client_id']}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(
            response.json()["ad_title"], "Test Ad 2"
        )

    def test_get_ads_progress_over_105(self):
        campaign = Campaign.objects.get(id=self.campaign_id1)
        campaign.impressions_count = 11
        campaign.save()
        response = self.client.get(
            f"{self.prefix}?client_id={self.client_data['client_id']}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(
            response.json()["ad_title"], "Test Ad 2"
        )

    def test_click_valid(self):
        ad_response = self.client.get(
            f"{self.prefix}?client_id={self.client_data['client_id']}",
            content_type="application/json",
        )
        ad_id = ad_response.json()["ad_id"]

        response = self.client.post(
            f"{self.prefix}/{ad_id}/click",
            data={"client_id": self.client_data["client_id"]},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.NO_CONTENT)
        campaign = Campaign.objects.get(id=ad_id)
        self.assertEqual(campaign.clicks_count, 1)

    def test_click_invalid_ad_id(self):
        invalid_id = "invalid-id"
        response = self.client.post(
            f"{self.prefix}/{invalid_id}/click",
            data={"client_id": self.client_data["client_id"]},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_click_nonexistent_ad(self):
        nonexistent_id = str(uuid.uuid4())
        response = self.client.post(
            f"{self.prefix}/{nonexistent_id}/click",
            data={"client_id": self.client_data["client_id"]},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.NOT_FOUND)

    def test_click_invalid_client_id(self):
        ad_response = self.client.get(
            f"{self.prefix}?client_id={self.client_data['client_id']}",
            content_type="application/json",
        )
        ad_id = ad_response.json()["ad_id"]

        response = self.client.post(
            f"{self.prefix}/{ad_id}/click",
            data={"client_id": "invalid-id"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_click_no_impression(self):
        client_data = {
            "client_id": "7fa85f64-5717-4562-b3fc-2c963f66afa6",
            "login": "anon",
            "age": 25,
            "location": "Moscow",
            "gender": "MALE",
        }
        self.client.post(
            "/clients/bulk",
            data=[client_data],
            content_type="application/json",
        )
        response = self.client.post(
            f"{self.prefix}/{self.campaign_id1}/click",
            data={"client_id": client_data["client_id"]},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.FORBIDDEN)

    def test_click_multiple_impressions(self):
        ad_response = self.client.get(
            f"{self.prefix}?client_id={self.client_data['client_id']}",
            content_type="application/json",
        )
        ad_id = ad_response.json()["ad_id"]

        self.client.post(
            f"{self.prefix}/{ad_id}/click",
            data={"client_id": self.client_data["client_id"]},
            content_type="application/json",
        )
        self.client.post(
            f"{self.prefix}/{ad_id}/click",
            data={"client_id": self.client_data["client_id"]},
            content_type="application/json",
        )
        campaign = Campaign.objects.get(id=ad_id)
        self.assertEqual(campaign.clicks_count, 1)

    def test_click_after_impression_limit(self):
        campaign = Campaign.objects.get(id=self.campaign_id1)
        campaign.impressions_count = 10
        campaign.save()
        Impression.objects.create(
            client=Client.objects.get(id=self.client_data["client_id"]),
            campaign=campaign,
            date=get_date(),
            cost=campaign.cost_per_impression,
        )

        response = self.client.get(
            f"{self.prefix}?client_id={self.client_data['client_id']}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        ad_id = response.json()["ad_id"]
        self.assertNotEqual(
            ad_id, self.campaign_id1
        )
