from http import HTTPStatus as status
from django import test
from clients.models import Client
import uuid


class ClientsTest(test.TestCase):
    def setUp(self):
        self.test_valid_clients = [
            {
                "client_id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
                "login": "user1",
                "age": 25,
                "location": "Moscow",
                "gender": "MALE",
            },
            {
                "client_id": "2fa85f64-5717-4562-b3fc-2c963f66afa6",
                "login": "user2",
                "age": 30,
                "location": "SaintPetersburg",
                "gender": "FEMALE",
            },
        ]

        self.test_invalid_clients = [
            {
                "client_id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
                "login": "",
                "age": -1,
                "location": "Moscow",
                "gender": "INVALID",
            },
            {
                "client_id": uuid.uuid4(),
                "login": "user3",
                "age": 28,
                "location": "Ekaterinburg",
                "gender": "ALL",
            },
        ]

        self.client = test.Client()
        self.prefix = "/clients"

    def test_bulk_create(self):
        response = self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_valid_clients,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(Client.objects.count(), 2)

    def test_bulk_invalid_create(self):
        clients_count = Client.objects.count()
        response = self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_invalid_clients,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(response.json(), [])
        self.assertEqual(clients_count, Client.objects.count())

    def test_bulk_mixed_create(self):
        mixed_clients = self.test_valid_clients + self.test_invalid_clients
        response = self.client.post(
            f"{self.prefix}/bulk",
            data=mixed_clients,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(len(response.json()), 2)
        self.assertEqual(Client.objects.count(), 2)

    def test_bulk_update(self):
        self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_valid_clients,
            content_type="application/json",
        )
        self.assertEqual(Client.objects.count(), 2)

        updated_client = [
            {
                "client_id": "1fa85f64-5717-4562-b3fc-2c963f66afa6",
                "login": "updated_user1",
                "age": 26,
                "location": "Moscow",
                "gender": "MALE",
            }
        ]
        response = self.client.post(
            f"{self.prefix}/bulk",
            data=updated_client,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.CREATED)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(Client.objects.count(), 2)
        updated = Client.objects.get(id=updated_client[0]["client_id"])
        self.assertEqual(updated.login, "updated_user1")
        self.assertEqual(updated.age, 26)

    def test_get_client(self):
        self.client.post(
            f"{self.prefix}/bulk",
            data=self.test_valid_clients,
            content_type="application/json",
        )
        client_id = self.test_valid_clients[0]["client_id"]

        response = self.client.get(
            f"{self.prefix}/{client_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.OK)
        self.assertEqual(response.json()["client_id"], client_id)

    def test_get_invalid_client_id(self):
        invalid_id = "invalid-id"
        response = self.client.get(
            f"{self.prefix}/{invalid_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.BAD_REQUEST)

    def test_get_nonexistent_client(self):
        nonexistent_id = str(uuid.uuid4())
        response = self.client.get(
            f"{self.prefix}/{nonexistent_id}",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.NOT_FOUND)
