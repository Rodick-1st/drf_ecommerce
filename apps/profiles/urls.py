from django.urls import path

from apps.profiles.views import ProfileView, ShippingAddressesView, ShippingAddressViewID, OrdersView, OrderItemsView, \
    ProductReviewDetailView, DeletedProductReviewDetail, ProductReviewsListView

urlpatterns = [
    path("", ProfileView.as_view()),
    path("shipping_addresses/", ShippingAddressesView.as_view()),
    path("shipping_addresses/detail/<str:id>/", ShippingAddressViewID.as_view()),
    path("orders/", OrdersView.as_view()),
    path("orders/<str:tx_ref>/", OrderItemsView.as_view()),
    ####################################################################################################################
                                # # # Далее следуют самописные маршруты # # #
    ####################################################################################################################
    path("product_reviews/user_list_reviews/", ProductReviewsListView.as_view()),
    path("product_reviews/detail/<slug:product_slug>/", ProductReviewDetailView.as_view()),
    path("product_reviews/deleted_detail/<slug:product_slug>/", DeletedProductReviewDetail.as_view()),
]
