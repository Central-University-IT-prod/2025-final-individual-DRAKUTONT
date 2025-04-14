from django.contrib import admin
from django.urls import include, path

from ads_platform.api import api

urlpatterns = [
    path("", api.urls),
    path("admin/", admin.site.urls),
    path("metrics/", include("django_prometheus.urls")),
]
