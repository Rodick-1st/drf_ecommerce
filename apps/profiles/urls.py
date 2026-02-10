from django.urls import path

from apps.profiles.views import ProfileView, ShippingAddressesView, ShippingAddressViewID, OrdersView, OrderItemsView, \
    ProductReviewDetailView, DeletedProductReviewDetail

urlpatterns = [
    path("", ProfileView.as_view()),
    path("shipping_addresses/", ShippingAddressesView.as_view()),
    path("shipping_addresses/detail/<str:id>/", ShippingAddressViewID.as_view()),
    path("orders/", OrdersView.as_view()),
    path("orders/<str:tx_ref>/", OrderItemsView.as_view()),
    path("product_reviews/detail/<slug:slug>/", ProductReviewDetailView.as_view()),
    path("product_reviews/deleted_detail/<slug:slug>/", DeletedProductReviewDetail.as_view()),

]
