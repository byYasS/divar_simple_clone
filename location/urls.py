from django.urls import path
from .views import set_city

app_name = "location"

urlpatterns = [
    path("select/", set_city, name="set_city")
]
