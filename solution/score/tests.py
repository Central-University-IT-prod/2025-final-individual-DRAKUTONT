from http import HTTPStatus as status
from django import test
from score.models import MLScore
from clients.models import Client
from advertisers.models import Advertiser
import uuid


class MLScoreTest(test.TestCase):
    def setUp(self):
        self.client = test.Client()
        self.prefix = "/ml-scores"

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

        response = self.client.post(
            "/clients/bulk",
            data=[self.client_data],
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)
        response = self.client.post(
            "/advertisers/bulk",
            data=[self.advertiser_data],
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)

        self.valid_ml_score = {
            "advertiser_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "client_id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
            "score": 80,
        }
        self.invalid_ml_score = {
            "advertiser_id": "invalid-id",
            "client_id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
            "score": 50,
        }
        self.invalid_score_value = {
            "advertiser_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "client_id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
            "score": -1,
        }

    def test_create_score(self):
        response = self.client.post(
            self.prefix,
            data=self.valid_ml_score,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(MLScore.objects.count(), 1)
        ml_score = MLScore.objects.get(
            client__id=self.valid_ml_score["client_id"],
            advertiser__id=self.valid_ml_score["advertiser_id"],
        )
        self.assertEqual(ml_score.score, 80)

    def test_create_invalid_advertiser_id(self):
        response = self.client.post(
            self.prefix,
            data=self.invalid_ml_score,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)
        self.assertEqual(MLScore.objects.count(), 0)

    def test_create_invalid_client_id(self):
        invalid_score = {
            "advertiser_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "client_id": "invalid-id",
            "score": 50,
        }
        response = self.client.post(
            self.prefix,
            data=invalid_score,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)
        self.assertEqual(MLScore.objects.count(), 0)

    def test_create_invalid_score_value(self):
        response = self.client.post(
            self.prefix,
            data=self.invalid_score_value,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)
        self.assertEqual(MLScore.objects.count(), 0)

    def test_update_score(self):
        self.client.post(
            self.prefix,
            data=self.valid_ml_score,
            content_type="application/json",
        )
        self.assertEqual(MLScore.objects.count(), 1)

        updated_score = {**self.valid_ml_score, "score": 90}
        response = self.client.post(
            self.prefix,
            data=updated_score,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        ml_score = MLScore.objects.get(
            client__id=self.valid_ml_score["client_id"],
            advertiser__id=self.valid_ml_score["advertiser_id"],
        )
        self.assertEqual(ml_score.score, 90)
