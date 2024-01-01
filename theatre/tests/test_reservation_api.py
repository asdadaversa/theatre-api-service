import random

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import TheatreHall, Ticket, Performance, Play, Reservation

from theatre.serializers import (
    ReservationSerializer,
)


RESERVATION_URL = reverse("theatre:reservation-list")


def sample_reservation(**params):
    user = get_user_model().objects.create_user(
        f"user{random.randint(1,10000)}2@test.com", "testpass"
    )

    defaults = {
        "user": user,
    }
    defaults.update(params)

    return Reservation.objects.create(**defaults)


def sample_ticket(**params):
    theatre_hall = TheatreHall.objects.create(name="Blue", rows=20, seats_in_row=20)
    play = Play.objects.create(title="Play", description="short description")
    performance = Performance.objects.create(
        play=play, theatre_hall=theatre_hall, show_time="2024-03-10T14:52:15Z"
    )
    user = get_user_model().objects.create_user(
        f"user{random.randint(1,10000)}2@test.com", "testpass"
    )
    reservation = Reservation.objects.create(user=user)

    defaults = {
        "reservation": reservation,
        "performance": performance,
        "row": 10,
        "seat": 20,
    }
    defaults.update(params)

    return Ticket.objects.create(**defaults)


def detail_url(reservation_id):
    return reverse("theatre:reservation-detail", args=[reservation_id])


class UnauthenticatedReservationApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedReservationApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("user@user.com", "testpass")
        self.client.force_authenticate(self.user)

    def test_create_reservation_with_ticket(self):
        ticket1 = sample_ticket(row=1, seat=19)
        ticket2 = sample_ticket(row=2, seat=18)

        payload = {
            "tickets": [
                {"id": 1, "row": 11, "seat": 11, "performance": 1},
                {"id": 1, "row": 14, "seat": 11, "performance": 1},
            ]
        }

        res = self.client.post(RESERVATION_URL, payload, format="json")
        reservation = Reservation.objects.get(id=res.data["id"])
        tickets = reservation.tickets.all()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        self.assertEqual(tickets.count(), 2)

    def test_list_reservations(self):
        ticket1 = sample_ticket(row=1, seat=15)
        ticket2 = sample_ticket(row=2, seat=15)
        ticket3 = sample_ticket(row=3, seat=15)
        ticket4 = sample_ticket(row=4, seat=15)

        reservation1 = sample_reservation(user=self.user)
        reservation2 = sample_reservation(user=self.user)

        reservation1.tickets.set([ticket1, ticket2])
        reservation2.tickets.set([ticket3, ticket4])

        res = self.client.get(RESERVATION_URL)

        reservations = Reservation.objects.all()
        serializer = ReservationSerializer(reservations, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_reservation_detail(self):
        reservation = sample_reservation(user=self.user)

        url = detail_url(reservation.id)
        res = self.client.get(url)

        serializer = ReservationSerializer(reservation)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_put_reservation_not_allowed(self):
        ticket1 = sample_ticket(row=1, seat=19)
        ticket2 = sample_ticket(row=2, seat=18)

        payload = {
            "tickets": [
                {"id": 1, "row": 11, "seat": 11, "performance": 1},
                {"id": 1, "row": 14, "seat": 11, "performance": 1},
            ]
        }

        reservation = sample_reservation(user=self.user)
        url = detail_url(reservation.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_reservation_not_allowed(self):
        reservation = sample_reservation(user=self.user)
        url = detail_url(reservation.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
