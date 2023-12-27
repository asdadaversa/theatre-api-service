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


class ReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reservation
        fields = ("id", "created_at", "user")


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
    performance = PerformanceSerializer(many=False, read_only=False)

    class Meta:
        model = Ticket
        fields = ("id", "row", "seat", "performance")


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = ("id", "title", "genres", "actors")


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
