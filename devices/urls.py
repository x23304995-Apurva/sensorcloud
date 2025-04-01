# devices/urls.py
from django.urls import path
from .views import DeviceListView, DeviceDetailView, DashboardView, DeviceDataAPI, register_device

urlpatterns = [
    path("", DeviceListView.as_view(), name="device-list"),
    path("<str:device_id>/", DeviceDetailView.as_view(), name="device-detail"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("data/", DeviceDataAPI.as_view(), name="device-data-api"),
    path("register/", register_device, name="register_device"),  # Make sure this line is correctly defined
]
