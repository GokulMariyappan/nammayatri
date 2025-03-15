from .views import *
from django.urls import path
from .services import *
from .customAuthenticaton import *

urlpatterns = [
    path('home', HomeView.as_view(), name = "home"),
    path('request-ride/', request_ride, name='request_ride'),
    path('available-rides/', available_rides, name='available_rides'),
    path('accept-ride/<int:ride_id>/', accept_ride, name='accept_ride'),
    path("register/", register, name="register"),  
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),
]