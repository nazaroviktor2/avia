from django.contrib import admin
from .models import Country, City, Airport, ModelAirplane, Airplane, Client, Document, Flight, Ticket, TicketBooking


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'country')
    list_filter = ('country',)
    search_fields = ('name', 'country__name')
    ordering = ('name',)  # Add ordering by name


@admin.register(Airport)
class AirportAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'city')
    list_filter = ('city__country', 'city')
    search_fields = ('name', 'short_name', 'city__name', 'city__country__name')
    ordering = ('name',)


@admin.register(ModelAirplane)
class ModelAirplaneAdmin(admin.ModelAdmin):
    list_display = ('name', 'seats', 'load_capacity')
    search_fields = ('name',)


@admin.register(Airplane)
class AirplaneAdmin(admin.ModelAdmin):
    list_display = ('name', 'model')
    list_filter = ('model',)
    search_fields = ('name', 'model__name')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('date_of_birth_day', 'user', "bank_account")
    search_fields = ('user__first_name', 'user__last_name', 'user__username')


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('client', 'doc_name', 'first_name', 'last_name', 'surname', 'number')
    list_filter = ('doc_name',)
    search_fields = ('client__first_name', 'client__last_name', 'client__surname', 'first_name', 'last_name', 'number')


@admin.register(Flight)
class FlightAdmin(admin.ModelAdmin):
    list_display = (
        'flight_number', 'status', 'departure', 'arrived', 'departure_airport', 'destination_airport', 'airplane'
    )
    # list_filter = ('status', 'departure', 'arrived', 'departure_airport', 'destination_airport', 'airplane')
    search_fields = ('flight_number', 'departure_airport__name', 'destination_airport__name')


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('client', 'flight', 'seat', 'price')
    readonly_fields = ('price',)
    list_filter = ('flight__status', 'flight__departure', 'flight__departure_airport', 'flight__destination_airport')
    search_fields = ('client__user__first_name', 'client__user__last_name', 'flight__flight_number', 'seat')


@admin.register(TicketBooking)
class TicketBookingAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    # search_fields = ('name', 'model__name')
