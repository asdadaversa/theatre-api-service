import random

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import TheatreHall, Ticket, Performance, Play, Reservation

from theatre.serializers import (
    TicketSerializer,
    TicketDetailSerializer,
)


TICKET_URL = reverse("theatre:ticket-list")


def sample_ticket(**params):
    theatre_hall = TheatreHall.objects.create(
        name="Blue", rows=20, seats_in_row=20
    )
    play = Play.objects.create(
        title="Play",
        description="short description"
    )
    performance = Performance.objects.create(
        play=play,
        theatre_hall=theatre_hall,
        show_time="2024-03-10T14:52:15Z"
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


def detail_url(ticket_id):
    return reverse("theatre:ticket-detail", args=[ticket_id])


class UnauthenticatedTicketApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TICKET_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedTicketApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@test.com",
            "testpass"
        )
        self.client.force_authenticate(self.user)

    def test_list_ticket_forbidden(self):
        sample_ticket()
        sample_ticket()

        res = self.client.get(TICKET_URL)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_ticket_detail_forbidden(self):
        ticket = sample_ticket()

        url = detail_url(ticket.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_ticket_forbidden(self):
        payload = {"reservation": 2, "performance": 1, "row": 5, "seat": 1}
        res = self.client.post(TICKET_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminTicketApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_ticket(self):
        sample_ticket()
        sample_ticket()

        res = self.client.get(TICKET_URL)

        ticket = Ticket.objects.all()
        serializer = TicketSerializer(ticket, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_tickets_detail(self):
        ticket = sample_ticket()

        url = detail_url(ticket.id)
        res = self.client.get(url)

        serializer = TicketDetailSerializer(ticket)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_ticket(self):
        theatre_hall = TheatreHall.objects.create(
            name="Blue", rows=20, seats_in_row=20
        )
        play = Play.objects.create(
            title="Play", description="short description"
        )
        performance = Performance.objects.create(
            play=play, theatre_hall=theatre_hall,
            show_time="2024-03-10T14:52:15Z"
        )
        user = get_user_model().objects.create_user(
            f"user{random.randint(1,10000)}2@test.com", "testpass"
        )
        reservation = Reservation.objects.create(user=user)

        payload = {
            "reservation": reservation.id,
            "performance": performance.id,
            "row": 5,
            "seat": 15,
        }

        res = self.client.post(TICKET_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_put_ticket_not_allowed(self):
        payload = {"reservation": 1, "performance": 2, "row": 5, "seat": 6}

        ticket = sample_ticket()
        url = detail_url(ticket.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_ticket_not_allowed(self):
        ticket = sample_ticket()
        url = detail_url(ticket.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
