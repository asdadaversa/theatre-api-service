from django.db.models import F, Count
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.pagination import PageNumberPagination

from theatre.models import (
    TheatreHall,
    Actor,
    Genre,
    Play,
    Performance,
    Reservation,
    Ticket
)

from theatre.serialazers import (
    TheatreHallSerializer,
    ActorSerializer,
    GenreSerializer,
    PerformanceSerializer,
    ReservationSerializer,
    TicketSerializer,
    PlaySerializer,
    ActorDetailSerializer,
    GenreDetailSerializer,
    TicketDetailSerializer,
    PlayListSerializer,
    PlayDetailSerializer,
    TheatreHallDetailSerializer,
    ReservationDetailSerializer,
    PerformanceDetailSerializer,
    PerformanceListSerializer
)


def params_to_ints(qs):
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


class OrderPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = "page_size"
    max_page_size = 1000


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TheatreHallDetailSerializer
        return TheatreHallSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    pagination_class = OrderPagination

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ActorDetailSerializer
        return ActorSerializer


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GenreDetailSerializer
        return GenreSerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer

    def get_queryset(self):
        """Retrieve the performances with filters"""
        queryset = self.queryset
        play = self.request.query_params.get("play")
        date = self.request.query_params.get("date")

        if self.action == "list":
            queryset = (
                queryset
                .prefetch_related("tickets")
                .select_related("play", "theatre_hall")
                .annotate(
                    tickets_available=(F("theatre_hall__rows")
                                       * F("theatre_hall__seats_in_row")
                                       - Count("tickets"))
                )
            )

        if play:
            play_id = params_to_ints(play)
            queryset = queryset.filter(play__id__in=play_id)

        if date:
            queryset = queryset.filter(show_time__date=date)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return PerformanceDetailSerializer
        if self.action == "list":
            return PerformanceListSerializer

        return PerformanceSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__play", "tickets__performance__theatre_hall"
    )
    serializer_class = ReservationSerializer
    authentication_classes = (TokenAuthentication, )

    def get_queryset(self):
        """Retrieve the reservations with filters by user"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReservationDetailSerializer
        return ReservationSerializer


class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.prefetch_related("performance__play")
    serializer_class = TicketSerializer

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.prefetch_related("genres", "actors")

    serializer_class = PlaySerializer

    def get_queryset(self):
        """Retrieve the plays with filters"""
        queryset = self.queryset
        actors = self.request.query_params.get("actors")
        genres = self.request.query_params.get("genres")
        title = self.request.query_params.get("title")

        if actors:
            actors_ids = params_to_ints(actors)
            queryset = queryset.filter(actors__id__in=actors_ids)
            if self.action in ("list", "retrieve"):
                queryset = queryset.prefetch_related("actors")

        if genres:
            genres_ids = params_to_ints(genres)
            queryset = queryset.filter(genres__id__in=genres_ids)
            if self.action in ("list", "retrieve"):
                queryset = queryset.prefetch_related("genres")

        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer
        if self.action == "retrieve":
            return PlayDetailSerializer
        return PlaySerializer
