from rest_framework import routers

from theatre.views import (
    TheatreHallViewSet,
    ActorViewSet,
    GenreViewSet,
    PerformanceViewSet,
    ReservationViewSet,
    TicketViewSet,
    PlayViewSet
)


router = routers.DefaultRouter()
router.register("theatre_halls", TheatreHallViewSet)
router.register("actors", ActorViewSet)
router.register("genres", GenreViewSet)
router.register("performances", PerformanceViewSet)
router.register("reservations", ReservationViewSet)
router.register("tickets", TicketViewSet)
router.register("plays", PlayViewSet)

urlpatterns = router.urls

app_name = "theatre"
