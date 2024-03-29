import os
import uuid

from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.text import slugify


def play_image_file_path(instance, filename):
    filename_without_ext, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/plays/", filename)


def actor_image_file_path(instance, filename):
    filename_without_ext, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.full_name)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads/actors/", filename)


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.IntegerField()
    seats_in_row = models.IntegerField()

    class Meta:
        verbose_name_plural = "theatre_halls"
        ordering = ["-id"]

    @property
    def theatre_capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    image = models.ImageField(null=True, upload_to=actor_image_file_path)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


class Genre(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    genres = models.ManyToManyField(Genre, related_name="plays", blank=True)
    actors = models.ManyToManyField(Actor, related_name="plays", blank=True)
    image = models.ImageField(null=True, upload_to=play_image_file_path)

    class Meta:
        verbose_name_plural = "plays"
        ordering = ["id"]

    def __str__(self):
        return self.title


class Performance(models.Model):
    show_time = models.DateTimeField()
    play = models.ForeignKey(
        Play, on_delete=models.CASCADE, related_name="performances"
    )
    theatre_hall = models.ForeignKey(
        TheatreHall, on_delete=models.CASCADE, related_name="performances"
    )

    class Meta:
        verbose_name_plural = "performances"
        ordering = ["-show_time"]

    def __str__(self):
        return f"{self.play.title} {str(self.show_time)}"


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return str(self.created_at)


class Ticket(models.Model):
    performance = models.ForeignKey(
        Performance, on_delete=models.CASCADE, related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="tickets"
    )
    row = models.IntegerField()
    seat = models.IntegerField()

    @staticmethod
    def validate_seats(
        seat: int,
        seat_in_row: int,
        row: int,
        rows: int,
        error_to_raise: ValidationError,
    ):
        if seat not in range(1, seat_in_row + 1):
            raise error_to_raise(
                {
                    "seat": (
                        f"number must be in available range:"
                        f"[1, {seat_in_row}], not {seat}"
                    )
                }
            )

        if row not in range(1, rows + 1):
            raise error_to_raise(
                {
                    "row": (
                        f"number must be in "
                        f"available range:" f"[1, {rows}] , not {row}"
                    )
                }
            )

    def clean(self):
        Ticket.validate_seats(
            self.seat,
            self.performance.theatre_hall.seats_in_row,
            self.row,
            self.performance.theatre_hall.rows,
            ValidationError,
        )

    def save(
        self,
        force_insert=False,
        force_update=False,
        using=None,
        update_fields=None,
    ):
        self.full_clean()
        super(Ticket, self).save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    class Meta:
        unique_together = ("performance", "row", "seat")

    def __str__(self):
        return f"{str(self.performance)} (row: {self.row}, seat: {self.seat})"
