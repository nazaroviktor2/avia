import json

from django.contrib.auth import login, authenticate, logout
import requests
from django.shortcuts import render, redirect

from django.urls import reverse
from django.http import JsonResponse, Http404
from django.shortcuts import get_object_or_404

from rest_framework import permissions, viewsets, status as status_codes
from . import config
from airlines.serializers import (
    CountrySerializer, CitySerializer, AirportSerializer, ModelAirplaneSerializer,
    AirplaneSerializer, ClientSerializer, DocumentSerializer, FlightSerializer, TicketSerializer,
    TicketBookingSerializer
)
from airlines.models import (
    Country, City, Airport, ModelAirplane, Airplane, Client,
    Document, Flight, Ticket, ON_SCHEDULE, TicketBooking
)
from django.db import models
from django.contrib import messages

from .forms import ClientRegistrationForm


class Country2ViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""

    queryset = Country.objects.all().order_by('name')
    serializer_class = CountrySerializer
    permission_classes = [permissions.IsAuthenticated]


class Permission(permissions.BasePermission):
    def has_permission(self, request, _):
        if request.method in config.SAFE_METHODS:
            return bool(request.user and request.user.is_authenticated)
        elif request.method in config.UNSAFE_METHODS:
            return bool(request.user and request.user.is_superuser)
        return False


def query_from_request(request, cls_serializer=None) -> dict:
    if cls_serializer:
        query = {}
        for attr in cls_serializer.Meta.fields:
            attr_value = request.GET.get(attr, '')
            if attr_value:
                query[attr] = attr_value
        return query
    return request.GET


def create_viewset(cls_model: models.Model, serializer, permission, order_field):
    class_name = f"{cls_model.__name__}ViewSet"
    doc = f"API endpoint that allows users to be viewed or edited for {cls_model.__name__}"
    return type(class_name, (viewsets.ModelViewSet,), {
        "__doc__": doc,
        "serializer_class": serializer,
        "queryset": cls_model.objects.all().order_by(order_field),
        "permission_classes": [permission],
        "get_queryset": lambda self, *args, **kwargs:
        cls_model.objects.filter(**query_from_request(self.request, serializer)).order_by(order_field),
    })


CountryViewSet = create_viewset(Country, CountrySerializer, Permission, 'name')
CityViewSet = create_viewset(City, CitySerializer, Permission, 'name')
AirportViewSet = create_viewset(Airport, AirportSerializer, Permission, 'name')
ModelAirplaneViewSet = create_viewset(ModelAirplane, ModelAirplaneSerializer, Permission, 'name')
AirplaneViewSet = create_viewset(Airplane, AirplaneSerializer, Permission, 'name')
ClientViewSet = create_viewset(Client, ClientSerializer, Permission, 'id')
DocumentViewSet = create_viewset(Document, DocumentSerializer, Permission, 'doc_name')
FlightViewSet = create_viewset(Flight, FlightSerializer, Permission, 'id')
TicketViewSet = create_viewset(Ticket, TicketSerializer, Permission, 'id')
TicketBookingViewSet = create_viewset(TicketBooking, TicketBookingSerializer, Permission, 'id')


def register_client(request):
    if request.method == 'POST':
        form = ClientRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Replace 'home' with the URL name of your homepage
    else:
        form = ClientRegistrationForm()

    return render(request, 'register.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('find_flight')


def profile(request):
    client = get_object_or_404(Client, user=request.user)
    tickets = TicketBooking.objects.filter(ticket__client=client)
    context = {'client': client, "tickets": tickets}

    if request.method == 'POST':
        body = json.loads(request.body)
        if body.get("date"):
            client.date_of_birth_day = body.get("date")
            client.save()
        if body.get("bank") and client.bank_account != body.get('bank'):
            client.bank_account = body.get("bank")
            client.save()

    return render(request, 'profile.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('find_flight')
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')


def find_flight_view(request):
    airports = Airport.objects.all()
    return render(request, "find_flight.html", {"airports": airports})


def flights_view(request):
    post = request.POST

    departure_airport = get_object_or_404(Airport, id=post.get('departure_id'))
    destination_airport = get_object_or_404(Airport, id=post.get('destination_id'))
    departure = post.get("date")
    flights = Flight.objects.filter(departure_airport=departure_airport, destination_airport=destination_airport,
                                    # departure__date__gte=departure,
                                    departure__date=departure,
                                    status=ON_SCHEDULE)
    return render(request, 'flights.html', {'flights': flights})


def flight_buy_view(request, flight_id):
    flight = get_object_or_404(Flight, id=flight_id)
    seats = [[0] * flight.airplane.model.scheme['columns'] for _ in range(flight.airplane.model.scheme['rows'])]
    for seat in flight.airplane.model.scheme['seats']:
        if Ticket.objects.filter(flight=flight, seat=seat['name']).count():
            seat['available'] = False
        if seat['name'] == 'pass':
            seat['name'] = ""
        seats[seat['row'] - 1][seat['column'] - 1] = seat
    if request.method == "POST":
        if not request.user.is_authenticated:
            raise Http404
        client = get_object_or_404(Client, user=request.user)
        ticket = Ticket(client=client, seat=request.POST.get('selected_seat'), flight=flight)
        ticket.save()
        ticket_book = TicketBooking(ticket=ticket)
        ticket_book.save()
        try:
            response = requests.post(
                url=config.BOOST_URL.format(id=''),
                headers=config.BOOST_HEADERS,
                json={
                    'recipient': config.BOOST_ACCOUNT,
                    'amount': ticket.price,
                    'callback':
                        {
                            'redirect': request.build_absolute_uri(reverse('profile')),
                            'url': request.build_absolute_uri(f'/api/v1/ticket-book/{ticket_book.id}/'),
                            'headers': config.BOOST_CALLBACK_HEADERS
                        }
                }
            )

            id = response.json().get('id')
            ticket_book.url = config.BOOST_REDIRECT.format(id=id)
            ticket_book.save()
            return redirect(config.BOOST_REDIRECT.format(id=id))

        except Exception:
            return render(
                request, "error.html", {
                    'error_message': 'Something wrong with payments. Please contact us to pay for the ticket'
                }
            )
    return render(request, 'flight_buy.html', {
        'flight': flight, "seats": seats,
        'seat_colors': {'economy': "#000"}
    })


def check_seat(request, flight_id):
    if request.GET:
        seat = request.GET.get('seat')
        if not Ticket.objects.filter(flight=flight_id, seat=seat).count():
            return JsonResponse({"available": True}, status=status_codes.HTTP_200_OK)
        return JsonResponse({"available": False}, status=status_codes.HTTP_200_OK)
    return JsonResponse({"available": False}, status=status_codes.HTTP_404_NOT_FOUND)
