from http import HTTPStatus as status
from django import test
from advertisers.models import Advertiser
from time_emulation.cache import get_date
import uuid


class AdvertisersTest(test.TestCase):
    def setUp(self):
        self.test_valid_advertisers = [
            {
                "advertiser_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "advertiser 1",
            },
            {
                "advertiser_id": "4fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "advertiser 2",
            },
            {
                "advertiser_id": "5fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "advertiser 3",
            },
        ]

        self.test_invalid_advertisers = [
            {
                "advertiser_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "",
            },
            {
                "advertiser_id": uuid.uuid4(),
                "name": "",
            },
        ]

        self.valid_campaign = {
            "targeting": {
                "gender": "MALE",
                "age_from": 10,
                "age_to": 50,
                "location": "Moscow",
            },
            "impressions_limit": 10,
            "clicks_limit": 10,
            "cost_per_impression": 10,
            "cost_per_click": 10,
            "ad_title": "SHAHOV",
            "ad_text": "POBEDA",
            "start_date": get_date(),
            "end_date": get_date(),
        }

        self.valid_campaign_without_target = {
            "targeting": None,
            "impressions_limit": 10,
            "clicks_limit": 10,
            "cost_per_impression": 10,
            "cost_per_click": 10,
            "ad_title": "SHAHOV",
            "ad_text": "POBEDA",
            "start_date": get_date(),
            "end_date": get_date(),
        }

        self.invalid_campaign = {
            "targeting": {
                "gender": "FRONTENDER",
                "age_from": 50,
                "age_to": 10,
                "location": "Moscow",
            },
            "impressions_limit": 10,
        }

        self.client = test.Client()
        self.prefix = "/advertisers"

    def create_advertisers(self):
        response = self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_valid_advertisers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)

    def create_campaigns(self):
        self.create_advertisers()
        self.client.post(
            f"{self.prefix}/3fa85f64-5717-4562-b3fc-2c963f66afa6/campaigns",
            data=self.valid_campaign,
            content_type="application/json",
        )
        self.client.post(
            f"{self.prefix}/3fa85f64-5717-4562-b3fc-2c963f66afa6/campaigns",
            data=self.valid_campaign_without_target,
            content_type="application/json",
        )

    def test_bulk_create(self):
        response = self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_valid_advertisers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(Advertiser.objects.count(), 3)

    def test_bulk_invalid_create(self):
        advertisers_count = Advertiser.objects.count()
        response = self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_invalid_advertisers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(response.json(), [])
        self.assertEqual(advertisers_count, Advertiser.objects.count())

    def test_bulk_mixed_create(self):
        mixed_advertisers = (
            self.test_valid_advertisers + self.test_invalid_advertisers
        )
        response = self.client.post(
            f"{self.prefix}/bulk",
            data=mixed_advertisers,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(len(response.json()), 3)
        self.assertEqual(Advertiser.objects.count(), 3)

    def test_bulk_update(self):
        self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_valid_advertisers,
            content_type="application/json",
        )
        self.assertEqual(Advertiser.objects.count(), 3)

        updated_advertiser = [
            {
                "advertiser_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "SHAHOV POBEDA",
            }
        ]
        response = self.client.post(
            f"{self.prefix}/bulk",
            data=updated_advertiser,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(Advertiser.objects.count(), 3)
        self.assertEqual(
            updated_advertiser[0]["name"],
            Advertiser.objects.get(
                id=updated_advertiser[0]["advertiser_id"]
            ).name,
        )

    def test_get_advertiser(self):
        self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_valid_advertisers,
            content_type="application/json",
        )
        advertiser_id = self.test_valid_advertisers[0]["advertiser_id"]

        response = self.client.get(
            f"{self.prefix}/{advertiser_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(response.json()["advertiser_id"], advertiser_id)

    def test_get_invalid_advertiser_id(self):
        invalid_id = "invalid-id"
        response = self.client.get(
            f"{self.prefix}/{invalid_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_nonexistent_advertiser(self):
        nonexistent_id = str(uuid.uuid4())
        response = self.client.get(
            f"{self.prefix}/{nonexistent_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.NOT_FOUND)

    def test_create_valid_campaign(self):
        self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_valid_advertisers,
            content_type="application/json",
        )
        response = self.client.post(
            f"{self.prefix}/3fa85f64-5717-4562-b3fc-2c963f66afa6/campaigns",
            data=self.valid_campaign,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)

    def test_create_invalid_campaign(self):
        self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_valid_advertisers,
            content_type="application/json",
        )
        response = self.client.post(
            f"{self.prefix}/3fa85f64-5717-4562-b3fc-2c963f66afa6/campaigns",
            data=self.invalid_campaign,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_campaigns_with_pagination(self):
        self.create_campaigns()

        response = self.client.get(
            f"{self.prefix}/3fa85f64-5717-4562-b3fc-2c963f66afa6/campaigns?size=10&page=5",
            content_type="application/json",
        )
        self.assertEqual(len(response.json()), 0)

        response = self.client.get(
            f"{self.prefix}/3fa85f64-5717-4562-b3fc-2c963f66afa6/campaigns?size=10&page=1",
            content_type="application/json",
        )
        self.assertEqual(len(response.json()), 2)

    def test_delete_campaign(self):
        self.create_advertisers()

        campaign_id = (
            self.client.post(
                f"{self.prefix}/3fa85f64-5717-4562-b3fc-2c963f66afa6/campaigns",
                data=self.valid_campaign,
                content_type="application/json",
            )
            .json()
            .get("campaign_id")
        )

        response = self.client.delete(
            f"{self.prefix}/3fa85f64-5717-4562-b3fc-2c963f66afa6/campaigns/{campaign_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.NO_CONTENT)

        response = self.client.delete(
            f"{self.prefix}/3fa85f64-5717-4562-b3fc-2c963f66afa6/campaigns/{campaign_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.NOT_FOUND)
