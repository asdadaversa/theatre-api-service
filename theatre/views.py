from django.db.models import F, Count
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from theatre.permissions import IsAdminOrIfAuthenticatedReadOnly
from theatre.models import (
    TheatreHall,
    Actor,
    Genre,
    Play,
    Performance,
    Reservation,
    Ticket,
)
from theatre.serializers import (
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
    PerformanceListSerializer,
    ActorImageSerializer,
    PlayImageSerializer,
)


def params_to_ints(qs):
    """Converts a list of string IDs to a list of integers"""
    return [int(str_id) for str_id in qs.split(",")]


class OrderPagination(PageNumberPagination):
    page_size = 4
    page_size_query_param = "page_size"
    max_page_size = 1000


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TheatreHallDetailSerializer
        return TheatreHallSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return ActorDetailSerializer
        if self.action == "upload_image":
            return ActorImageSerializer
        return ActorSerializer

    @action(
        methods=["GET", "POST", "RETRIEVE"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific play"""
        actor = self.get_object()
        serializer = self.get_serializer(actor, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GenreDetailSerializer
        return GenreSerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    pagination_class = OrderPagination
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

    def get_queryset(self):
        """Retrieve the performances with filters"""
        queryset = self.queryset
        play = self.request.query_params.get("play")
        date = self.request.query_params.get("date")

        if self.action == "list":
            queryset = (
                queryset.prefetch_related("tickets")
                .select_related("play", "theatre_hall")
                .annotate(
                    tickets_available=(
                        F("theatre_hall__rows") * F("theatre_hall__seats_in_row")
                        - Count("tickets")
                    )
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                type={"type": "datetime.date", "items": {"type": "datetime.date"}},
                description="filtering by date",
            )
        ]
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="play",
                type={"type": "list", "items": {"type": "number"}},
                description="filtering by play",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReservationViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Reservation.objects.prefetch_related(
        "tickets__performance__play", "tickets__performance__theatre_hall"
    )
    serializer_class = ReservationSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Retrieve the reservations with filters by user"""
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action in ("list", "retrieve"):
            return ReservationDetailSerializer
        return ReservationSerializer


class TicketViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet,
):
    queryset = Ticket.objects.prefetch_related("performance__play")
    serializer_class = TicketSerializer
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.prefetch_related("genres", "actors")
    serializer_class = PlaySerializer
    permission_classes = (IsAdminOrIfAuthenticatedReadOnly,)

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
        if self.action == "upload_image":
            return PlayImageSerializer

        return PlaySerializer

    @action(
        methods=["GET", "POST", "RETRIEVE"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        """Endpoint for uploading image to specific play"""
        play = self.get_object()
        serializer = self.get_serializer(play, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="title",
                type={"type": "str", "items": {"type": "str"}},
                description="filtering by title",
            )
        ]
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="genres",
                type={"type": "list", "items": {"type": "number"}},
                description="filtering by genre",
            )
        ]
    )
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="actors",
                type={"type": "list", "items": {"type": "number"}},
                description="filtering by actors",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
