from django.urls import path

from apps.profiles.views import ProfileView, ShippingAddressesView, ShippingAddressViewID

urlpatterns = [
    path("", ProfileView.as_view()),
    path("shipping_addresses/", ShippingAddressesView.as_view()),
    path("shipping_addresses/detail/<str:id>/", ShippingAddressViewID.as_view()),   # New
]
