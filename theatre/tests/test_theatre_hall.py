from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import TheatreHall


from theatre.serializers import (
    TheatreHallSerializer,
    TheatreHallDetailSerializer,
)


THEATRE_HALL_URL = reverse("theatre:theatrehall-list")


def sample_theatre_hall(**params):
    defaults = {"name": "Theatre Hall", "rows": 10, "seats_in_row": 30}
    defaults.update(params)

    return TheatreHall.objects.create(**defaults)


def detail_url(theatre_hall_id):
    return reverse("theatre:theatrehall-detail", args=[theatre_hall_id])


class UnauthenticatedTheatreHallApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(THEATRE_HALL_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTheatreHallApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com", "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_theatre_halls(self):
        sample_theatre_hall()
        sample_theatre_hall()

        res = self.client.get(THEATRE_HALL_URL)

        theatre_halls = TheatreHall.objects.all()
        serializer = TheatreHallSerializer(theatre_halls, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_theatre_hall_detail(self):
        theatre_hall = sample_theatre_hall(name="First")

        url = detail_url(theatre_hall.id)
        res = self.client.get(url)

        serializer = TheatreHallDetailSerializer(theatre_hall)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_theatre_hall_forbidden(self):
        payload = {"name": "Theatre Hall", "rows": 10, "seats_in_row": 30}
        res = self.client.post(THEATRE_HALL_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_theatre_hall_forbidden(self):
        payload = {"name": "Theatre Hall", "rows": 10, "seats_in_row": 30}

        theatre_hall = sample_theatre_hall()
        url = detail_url(theatre_hall.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_theatre_hall_forbidden(self):
        theatre_hall = sample_theatre_hall()
        url = detail_url(theatre_hall.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTheatreHallApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_theatre_hall(self):
        payload = {"name": "Theatre Hall", "rows": 10, "seats_in_row": 30}

        res = self.client.post(THEATRE_HALL_URL, payload)
        theatre_hall = TheatreHall.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(theatre_hall, key))
