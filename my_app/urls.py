from django.urls import path
from . import views

app_name = "my_app"

urlpatterns = [
    path("", views.create_gym_session, name="home"),
    path("create_gym_session/", views.create_gym_session, name="create_gym_session"),
]