from django.contrib import admin
from django.urls import include
from django.urls import path

urlpatterns = [
    path('v1/', include(('api.v1.urls', 'api'), namespace='v1')),
    path('v1/', include(('users.api.v1.urls', 'users'), namespace='users-v1')),
]