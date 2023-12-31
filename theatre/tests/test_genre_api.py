from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Genre


from theatre.serializers import (
    GenreSerializer,
    GenreDetailSerializer,
)


GENRE_URL = reverse("theatre:genre-list")


def sample_genre(**params):
    defaults = {"name": "Genre"}
    defaults.update(params)

    return Genre.objects.create(**defaults)


def detail_url(genre_id):
    return reverse("theatre:genre-detail", args=[genre_id])


class UnauthenticatedGenreApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(GENRE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedGenreApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@test.com", "testpass")
        self.client.force_authenticate(self.user)

    def test_list_genres(self):
        sample_genre(name="First")
        sample_genre(name="Second")

        res = self.client.get(GENRE_URL)

        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_genre_detail(self):
        genre = sample_genre(name="First")

        url = detail_url(genre.id)
        res = self.client.get(url)

        serializer = GenreDetailSerializer(genre)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_genre_forbidden(self):
        payload = {
            "name": "Genre",
        }
        res = self.client.post(GENRE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_genre_forbidden(self):
        payload = {
            "name": "Genre",
        }

        genre = sample_genre()
        url = detail_url(genre.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_genre_forbidden(self):
        genre = sample_genre()
        url = detail_url(genre.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminGenreApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_genre(self):
        payload = {
            "name": "Name",
        }

        res = self.client.post(GENRE_URL, payload)
        genre = Genre.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(genre, key))
