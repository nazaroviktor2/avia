
from rest_framework import serializers
from airplane.airplane_model import Airplane as AirplaneScheme
from .models import Country, City, Airport, ModelAirplane, Airplane, Client, Document, Flight, Ticket, TicketBooking
from django.contrib.auth.models import User


class CountrySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name']


class CitySerializer(serializers.HyperlinkedModelSerializer):
    country = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all())

    class Meta:
        model = City
        fields = ['id', 'name', 'country']


class AirportSerializer(serializers.HyperlinkedModelSerializer):
    city = CitySerializer()

    class Meta:
        model = Airport
        fields = ['id', 'name', 'short_name', 'city']


class ModelAirplaneSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ModelAirplane
        fields = ['id', 'name', 'seats', 'load_capacity', 'scheme']


class AirplaneSerializer(serializers.HyperlinkedModelSerializer):
    model = serializers.PrimaryKeyRelatedField(queryset=ModelAirplane.objects.all())

    class Meta:
        model = Airplane
        fields = ['id', 'name', 'model']


class ClientSerializer(serializers.HyperlinkedModelSerializer):

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = Client
        fields = ['id', 'user', 'first_name', 'last_name', 'surname', 'date_of_birth_day']

    def validate_user(self, value):
        clients = Client.objects.filter(user=value)
        if clients:
            raise serializers.ValidationError(f"user {value} all ready has client")
        return value


class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())

    class Meta:
        model = Document
        fields = ['id', 'client', 'doc_name', 'first_name', 'last_name', 'surname', 'number']


class FlightSerializer(serializers.HyperlinkedModelSerializer):
    departure_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    destination_airport = serializers.PrimaryKeyRelatedField(queryset=Airport.objects.all())
    airplane = serializers.PrimaryKeyRelatedField(queryset=Airplane.objects.all())
    departure = serializers.DateTimeField()
    arrived = serializers.DateTimeField()
    tickets = ClientSerializer(many=True, required=False)
    flight_number = serializers.CharField()

    class Meta:
        model = Flight
        fields = ['id', 'status', "departure", "arrived", "airplane", "departure_airport", "destination_airport",
                  "flight_number", "tickets", "prices"]
        read_only_fields = ["tickets"]
        extra_kwargs = {
            'tickets': {
                'read_only': True
            }
        }

    def validate_prices(self, value):
        if not value and not isinstance(value, dict):
            raise serializers.ValidationError("Prices is not valid JSON")
        return value

    def validate_unique_flight(self, flight_number, departure, arrived, pk=None):
        # Additional validation for unique flight number within a month
        flights_with_same_number = Flight.objects.filter(
            flight_number=flight_number,
            departure__month=departure.month,
            departure__year=departure.year,
        )
        if pk:  # Exclude current instance if it's being updated
            flights_with_same_number = flights_with_same_number.exclude(pk=pk)

        if flights_with_same_number.filter(
                departure__day__lte=departure.day,
                arrived__day__gte=arrived.day) \
                or flights_with_same_number.filter(
            departure__day__lte=departure.day,
            arrived__day__gte=departure.day,
            arrived__day__lte=arrived.day) \
                or flights_with_same_number.filter(
            departure__day__gte=departure.day,
            departure__day__lte=arrived.day,
            arrived__day__gte=arrived.day) \
                or flights_with_same_number.filter(
            departure__day__gte=departure.day,
            departure__day__lte=arrived.day,
            arrived__day__gte=departure.day,
            arrived__day__lte=arrived.day) \
                or flights_with_same_number.filter(
            departure__day__lte=departure.day,
            arrived__day__gte=departure.day,
            arrived__day__lte=arrived.day) \
                or flights_with_same_number.filter(
            departure__day__gte=departure.day,
            departure__day__lte=arrived.day,
            arrived__day__gte=arrived.day):
            raise serializers.ValidationError({'flight_number': 'Conflicting flight number for a date...'})

    def validate(self, attrs):
        pk = None
        if self.instance:
            pk = self.instance.pk
        self.validate_unique_flight(attrs["flight_number"], attrs["departure"], attrs["arrived"], pk)

        if attrs["arrived"] < attrs["departure"]:
            raise serializers.ValidationError("Arrived must be less than departure")
        types_seat = AirplaneScheme.parse_obj(attrs["airplane"].model.scheme).get_types_seat()
        need_price = []
        for seat_type in types_seat:
            if seat_type in attrs["prices"] and isinstance(attrs["prices"].get(seat_type), (float, int)):
                continue
            need_price.append(seat_type)
        if need_price:
            s_price = ", ".join(need_price)
            raise serializers.ValidationError({'prices': f"You need add prises for {s_price}"})
        return attrs


class TicketSerializer(serializers.HyperlinkedModelSerializer):
    client = serializers.PrimaryKeyRelatedField(queryset=Client.objects.all())
    flight = serializers.PrimaryKeyRelatedField(queryset=Flight.objects.all())

    class Meta:
        model = Ticket
        fields = ['id', 'client', 'flight', 'seat', 'price']
        read_only_fields = ["price"]

    def validate_flight(self, flight):
        if Ticket.objects.filter(flight=flight).count() >= flight.airplane.model.seats:
            raise serializers.ValidationError("No more seats available on the plane.")
        return flight

    def validate(self, attrs):
        seat = attrs['seat']
        flight = attrs["flight"]
        seats_name = {seat.get('name'): seat.get("available") for seat in flight.airplane.model.scheme.get("seats")}
        if not seats_name.get(seat):
            raise serializers.ValidationError(f"Seat '{seat}' not available in airplane {flight.airplane}")
        if Ticket.objects.filter(flight=flight, seat=seat).count():
            raise serializers.ValidationError(f"Seat '{seat}' is taken {flight.airplane}")
        return attrs


class TicketBookingSerializer(serializers.HyperlinkedModelSerializer):
    ticket = serializers.PrimaryKeyRelatedField(queryset=Ticket.objects.all())

    class Meta:
        model = TicketBooking
        fields = ['id', 'ticket', 'status', 'created_at', 'pay_before']
