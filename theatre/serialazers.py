from rest_framework import serializers


from theatre.models import (
    TheatreHall,
    Actor,
    Genre,
    Play,
    Performance,
    Reservation,
    Ticket
)


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row", "theatre_capacity")


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name", "full_name")


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ("id", "name", )


class GenreDetailSerializer(serializers.ModelSerializer):
    plays_in_genre = serializers.SlugRelatedField(
        source="plays",
        many=True,
        read_only=True,
        slug_field="title"
    )

    class Meta:
        model = Genre
        fields = ("name", "plays_in_genre",)


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = ("id", "show_time", "play", "theatre_hall")


class PerformanceTicketSerializer(PerformanceSerializer):
    play_title = serializers.CharField(source="play.title", read_only=True)
    theatre_hall_name = serializers.CharField(source="theatre_hall.name", read_only=True)

    class Meta:
        model = Performance
        fields = ("id", "show_time", "play_title", "theatre_hall_name")


class PerformanceHallSerializer(PerformanceSerializer):
    play_title = serializers.CharField(source="play.title", read_only=True)

    class Meta:
        model = Performance
        fields = ("id", "show_time", "play_title")


class TicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")

    def validate(self, attrs):
        data = super().validate(attrs)
        Ticket.validate_seats(
            attrs["seat"],
            attrs["performance"].theatre_hall.seats_in_row,
            attrs["row"],
            attrs["performance"].theatre_hall.rows,
            serializers.ValidationError,
        )
        return data


class TicketDetailSerializer(TicketSerializer):
    performance = PerformanceTicketSerializer(many=False, read_only=False)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")


class PerformanceReservationSerializer(PerformanceSerializer):
    play_title = serializers.CharField(source="play.title", read_only=True)

    class Meta:
        model = Performance
        fields = ("show_time", "play_title")


class TicketReservationSerializer(TicketSerializer):
    performance = PerformanceReservationSerializer(many=False, read_only=False)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "description", "genres", "actors")


class PlayListSerializer(PlaySerializer):
    genres = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )
    actors = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="full_name"
    )


class PlayDetailSerializer(PlaySerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)

    class Meta:
        model = Play
        fields = ("id", "title", "description", "genres", "actors")


class ActorDetailSerializer(ActorSerializer):
    plays_in = serializers.SlugRelatedField(
        source="plays",
        many=True,
        read_only=True,
        slug_field="title"
    )

    class Meta:
        model = Actor
        fields = ("first_name", "last_name", "full_name", "plays_in",)


class TheatreHallDetailSerializer(TheatreHallSerializer):
    performances = PerformanceHallSerializer(many=True, read_only=True)

    class Meta:
        model = TheatreHall
        fields = ("id", "name", "rows", "seats_in_row", "theatre_capacity", "performances")


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        reservation = Reservation.objects.create(**validated_data)

        for ticket_data in tickets_data:
            Ticket.objects.create(reservation=reservation, **ticket_data)
        return reservation


class ReservationDetailSerializer(ReservationSerializer):
    tickets = TicketReservationSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at")


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=False)

    class Meta:
        model = Reservation
        fields = ("id", "tickets", "created_at",)
