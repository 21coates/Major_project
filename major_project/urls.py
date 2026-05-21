from django.contrib import admin 
from django.urls import include, path
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('users:login')),
    path('admin/', admin.site.urls),
    path('users/', include(("users.urls", "users"), namespace="users")),
    path('my_app/', include(("my_app.urls", "my_app"), namespace="my_app")),
]