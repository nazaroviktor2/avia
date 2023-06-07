from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from airplane.airplane_model import Airplane as AirplaneScheme
from pydantic.error_wrappers import ValidationError as pyValidationError
from django.core.exceptions import ValidationError
from django.utils import timezone

from avia.settings import PAY_BEFORE_TIMEDELTA

ON_SCHEDULE = "OS"
CHECK_OPEN = "CO"
CHECK_CLOSE = "CC"
LANDING = "LA"
DEPARTED = "DE"
IN_FLIGHT = "IF"
ARRIVED = "AR"
CANCELED = "CA"

RUSSIAN_PASSPORT = "RUS_PASS"

FLIGHT_STATUS = [
    (ON_SCHEDULE, "On schedule"),
    (CHECK_OPEN, "Check is open"),
    (CHECK_CLOSE, "Check is close"),
    (LANDING, "Landing"),
    (DEPARTED, "Departed"),
    (IN_FLIGHT, "In flight"),
    (ARRIVED, "Arrived"),
    (CANCELED, "Canceled")
]

DOCUMENTS = [
    (RUSSIAN_PASSPORT, "Russian passport")
]

TICKET_WAITING = "Waiting"
TICKET_CONFIRMED = "Confirmed"
TICKET_CANCELLED = "Cancelled"

TICKET_STATUS = [
    (TICKET_WAITING, "Waiting"),
    (TICKET_CONFIRMED, "Confirmed"),
    (TICKET_CANCELLED, "Cancelled"),
]


class Country(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)

    def __str__(self):
        return f"{self.name}"


class City(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


class Airport(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    short_name = models.CharField(max_length=100, null=False, blank=False)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f"{self.name} ({self.short_name})"


def validate_airplane_scheme(scheme: dict):
    try:
        AirplaneScheme.parse_obj(scheme)
    except pyValidationError as ex:

        raise ValidationError(f"{ex}", params={'error': ex})


def validate_unique_client(user):
    clients = Client.objects.filter(user=user)
    if clients:
        raise ValidationError(f"user {user.id} all ready has client")


class ModelAirplane(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    seats = models.IntegerField(null=False, blank=False)
    load_capacity = models.DecimalField(max_digits=12, decimal_places=2)
    scheme = models.JSONField(null=False, blank=False, default=dict, validators=[validate_airplane_scheme])

    def __str__(self):
        return f"{self.id}: {self.name} total seats {self.seats}"


class Airplane(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    model = models.ForeignKey(ModelAirplane, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id}: {self.name}"


class Client(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_of_birth_day = models.DateField(null=True, blank=True)
    bank_account = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.id}: {self.user.first_name} {self.user.last_name}"


class Document(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    doc_name = models.CharField(max_length=20, choices=DOCUMENTS, null=False, blank=False)
    first_name = models.CharField(max_length=100, null=False, blank=False)
    last_name = models.CharField(max_length=100, null=False, blank=False)
    surname = models.CharField(max_length=100, null=True, blank=True, default="-")
    number = models.CharField(max_length=20, null=False, blank=False)


class Flight(models.Model):
    status = models.CharField(max_length=2, choices=FLIGHT_STATUS, default=ON_SCHEDULE)
    departure = models.DateTimeField(default=timezone.now, editable=True)
    arrived = models.DateTimeField(default=timezone.now, editable=True)
    flight_number = models.CharField(max_length=100, null=False, blank=False)
    departure_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="departure_airport")
    destination_airport = models.ForeignKey(Airport, on_delete=models.CASCADE, related_name="destination_airport")
    airplane = models.ForeignKey(Airplane, on_delete=models.CASCADE)
    tickets = models.ManyToManyField(Client, through="Ticket")
    prices = models.JSONField(null=False, blank=False, default=dict)

    def __str__(self):
        time = f"{self.departure.date()} {str(self.departure.time())[:5]}"
        total_airplane = self.airplane.model.seats
        total = len(Ticket.objects.filter(flight=self.id))
        return f"{self.id}: {self.flight_number} {self.departure_airport} - {self.destination_airport} {time} " + \
            f"status - {self.status} seats - {total}/{total_airplane}"

    def validate_unique(self, exclude=None):
        super().validate_unique(exclude)
        # Additional validation for unique flight number within a month
        flights_with_same_number = Flight.objects.filter(
            flight_number=self.flight_number,
            departure__month=self.departure.month,
            departure__year=self.departure.year,
        )
        if self.pk:  # Exclude current instance if it's being updated
            flights_with_same_number = flights_with_same_number.exclude(pk=self.pk)

        if flights_with_same_number.filter(
                departure__day__lte=self.departure.day,
                arrived__day__gte=self.arrived.day) \
                or flights_with_same_number.filter(
            departure__day__lte=self.departure.day,
            arrived__day__gte=self.departure.day,
            arrived__day__lte=self.arrived.day) \
                or flights_with_same_number.filter(
            departure__day__gte=self.departure.day,
            departure__day__lte=self.arrived.day,
            arrived__day__gte=self.arrived.day) \
                or flights_with_same_number.filter(
            departure__day__gte=self.departure.day,
            departure__day__lte=self.arrived.day,
            arrived__day__gte=self.departure.day,
            arrived__day__lte=self.arrived.day) \
                or flights_with_same_number.filter(
            departure__day__lte=self.departure.day,
            arrived__day__gte=self.departure.day,
            arrived__day__lte=self.arrived.day) \
                or flights_with_same_number.filter(
            departure__day__gte=self.departure.day,
            departure__day__lte=self.arrived.day,
            arrived__day__gte=self.arrived.day):
            raise ValidationError({'flight_number': 'Conflicting flight number for a date...'})

    def clean(self, *args, **kwargs):
        super().clean()
        self.validate_unique()
        if self.arrived < self.departure:
            raise ValidationError("Arrived must be less than departure")
        types_seat = AirplaneScheme.parse_obj(self.airplane.model.scheme).get_types_seat()
        need_price = []
        for seat_type in types_seat:
            if seat_type in self.prices and isinstance(self.prices.get(seat_type), (float, int)):
                continue
            need_price.append(seat_type)
        if need_price:
            s_price = ", ".join(need_price)
            raise ValidationError({'prices': f"You need add prises for {s_price}"})

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     self.clean()


def validate_ticket_flight(flight):
    if Ticket.objects.filter(flight=flight).count() >= Flight.objects.get(id=flight).airplane.model.seats:
        raise ValidationError("No more seats available on the plane.")


class Ticket(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE, validators=[validate_ticket_flight])
    seat = models.CharField(max_length=100, null=False, blank=False)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=False, blank=False)

    def clean(self, *args, **kwargs):
        airplane = self.flight.airplane
        seats_name = [seat.get('name') for seat in airplane.model.scheme.get("seats")]
        if self.seat not in seats_name or self.seat == "pass":
            raise ValidationError({'seat': f"Seat '{self.seat}' not exist in airplane {airplane}"})

        if Ticket.objects.filter(flight=self.flight, seat=self.seat).count():
            raise ValidationError({"seat": f"Seat '{self.seat}' is taken {self.flight.airplane}"})

    def save(self, *args, **kwargs):
        seat_type = None
        for seat in self.flight.airplane.model.scheme.get("seats"):
            if seat.get("name"):
                seat_type = seat.get("seat_type")
                break
        self.price = self.flight.prices.get(seat_type)
        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('seat', 'flight')


class TicketBooking(models.Model):
    ticket = models.OneToOneField(Ticket, on_delete=models.CASCADE)
    status = models.CharField(max_length=9, choices=TICKET_STATUS, default=TICKET_WAITING)
    created_at = models.DateTimeField(auto_now_add=True)
    pay_before = models.DateTimeField(blank=True, null=True)
    url = models.URLField(blank=True, null=True)


@receiver(post_save, sender=TicketBooking)
def create_ticket_instance(sender, instance, **kwargs):
    if instance.pk is None:
        instance.pay_before = instance.created_at + PAY_BEFORE_TIMEDELTA
    if instance.status == TICKET_CANCELLED:
        instance.ticket.delete()
