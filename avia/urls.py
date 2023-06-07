from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from rest_framework.authtoken import views as rest_views
from airlines import views

router_v1 = routers.DefaultRouter()
router_v1.register(r'country', views.CountryViewSet)
router_v1.register(r'city', views.CityViewSet)
router_v1.register(r'airport', views.AirportViewSet)
router_v1.register(r'model-airplane', views.ModelAirplaneViewSet)
router_v1.register(r'airplane', views.AirplaneViewSet)
router_v1.register(r'client', views.ClientViewSet)
router_v1.register(r'document', views.DocumentViewSet)
router_v1.register(r'flight', views.FlightViewSet)
router_v1.register(r'ticket', views.TicketViewSet)
router_v1.register(r'ticket-book', views.TicketBookingViewSet)


router_v2 = routers.DefaultRouter()
router_v2.register(r'country', views.Country2ViewSet)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include((router_v1.urls, 'avia'), namespace='api')),
    path('api/v2/', include((router_v2.urls, 'avia'), namespace='v2')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api-token-auth/', rest_views.obtain_auth_token),
    path(r"", views.find_flight_view, name='find_flight'),
    path(r"flight/", views.flights_view, name='flights'),
    path(r"flight/<int:flight_id>/buy", views.flight_buy_view, name='flight_buy'),
    path(r"check-seat/<int:flight_id>", views.check_seat, name='check_seat'),
    path('register/', views.register_client, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile', views.profile, name='profile'),
]
