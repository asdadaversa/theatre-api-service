import tempfile
import os

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from theatre.models import Actor


from theatre.serializers import (
    ActorSerializer,
    ActorDetailSerializer,
)


ACTOR_URL = reverse("theatre:actor-list")


def sample_actor(**params):
    defaults = {"first_name": "George", "last_name": "Clooney"}
    defaults.update(params)

    return Actor.objects.create(**defaults)


def image_upload_url(actor_id):
    """Return URL for recipe image upload"""
    return reverse("theatre:actor-upload-image", args=[actor_id])


def detail_url(actor_id):
    return reverse("theatre:actor-detail", args=[actor_id])


class UnauthenticatedActorApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(ACTOR_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedActorApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user("test@test.com", "testpass")
        self.client.force_authenticate(self.user)

    def test_list_actors(self):
        sample_actor(first_name="First", last_name="Actor1")
        sample_actor(first_name="Second", last_name="Actor2")

        res = self.client.get(ACTOR_URL)

        actors = Actor.objects.all()
        serializer = ActorSerializer(actors, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_actor_detail(self):
        actor = sample_actor(first_name="First", last_name="Actor1")

        url = detail_url(actor.id)
        res = self.client.get(url)

        serializer = ActorDetailSerializer(actor)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_actor_forbidden(self):
        payload = {
            "first_name": "Name",
            "last_name": "Surname",
        }
        res = self.client.post(ACTOR_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_put_actor_forbidden(self):
        payload = {
            "first_name": "Name",
            "last_name": "Surname",
        }

        actor = sample_actor()
        url = detail_url(actor.id)

        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_actor_forbidden(self):
        actor = sample_actor()
        url = detail_url(actor.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminActorApiTests(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "testpass", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_actor(self):
        payload = {
            "first_name": "Name",
            "last_name": "Surname",
        }

        res = self.client.post(ACTOR_URL, payload)
        actor = Actor.objects.get(id=res.data["id"])
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(actor, key))


class ActorImageUploadTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            "admin@myproject.com", "password"
        )
        self.client.force_authenticate(self.user)
        self.actor = sample_actor()

    def tearDown(self):
        self.actor.image.delete()

    def test_upload_image_to_actor(self):
        """Test uploading an image to actor"""
        url = image_upload_url(self.actor.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(url, {"image": ntf}, format="multipart")
        self.actor.refresh_from_db()

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("image", res.data)
        self.assertTrue(os.path.exists(self.actor.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image"""
        url = image_upload_url(self.actor.id)
        res = self.client.post(url, {"image": "not image"}, format="multipart")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_image_to_actor_list(self):
        url = ACTOR_URL
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            res = self.client.post(
                url,
                {
                    "first_name": "Name",
                    "last_name": "Surname",
                },
                format="multipart",
            )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        actor = Actor.objects.get(last_name="Surname")
        self.assertFalse(actor.image)

    def test_image_url_is_shown_on_actor_detail(self):
        url = image_upload_url(self.actor.id)
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            self.client.post(url, {"image": ntf}, format="multipart")
        res = self.client.get(detail_url(self.actor.id))

        self.assertIn("image", res.data)
