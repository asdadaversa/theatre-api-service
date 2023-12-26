from django.contrib import admin

from theatre.models import TheatreHall, Actor, Genre, Performance, Play, Reservation, Ticket


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Reservation)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)


admin.site.register(TheatreHall)
admin.site.register(Actor)
admin.site.register(Ticket)
admin.site.register(Genre)
admin.site.register(Performance)
admin.site.register(Play)
