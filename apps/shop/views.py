from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import OpenApiParameter, OpenApiTypes
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from apps.common.paginations import CustomPagination
from apps.common.permissions import IsSeller
from apps.shop.serializers import CategorySerializer, ProductSerializer, OrderItemSerializer, ToggleCartItemSerializer, CheckoutSerializer, OrderSerializer
from apps.shop.models import Category, Product
from apps.sellers.models import Seller
from apps.profiles.models import OrderItem, ShippingAddress, Order
from apps.shop.filters import ProductFilter
from apps.shop.schema_examples import PRODUCT_PARAM_EXAMPLE

tags = ["Shop"]


class CategoriesView(APIView):
    serializer_class = CategorySerializer
    permission_classes = [IsSeller]
    @extend_schema(
        summary="Categories Fetch",
        description="""
            This endpoint returns all categories.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        categories = Category.objects.all()
        serializer = self.serializer_class(categories, many=True)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Category Creating",
        description="""
            This endpoint creates categories.
        """,
        tags=tags
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            new_cat = Category.objects.create(**serializer.validated_data)
            serializer = self.serializer_class(new_cat)
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class ProductsByCategoryView(APIView):
    serializer_class = ProductSerializer
    permission_classes = [IsSeller]

    @extend_schema(
        operation_id="category_products",
        summary="Category Products Fetch",
        description="""
            This endpoint returns all products in a particular category.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        category = Category.objects.get_or_none(slug=kwargs["slug"])
        if not category:
            return Response(data={"message": "Category does not exist!"}, status=404)
        products = Product.objects.select_related("category", "seller", "seller__user").filter(category=category)
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)


class ProductsView(APIView):
    serializer_class = ProductSerializer
    pagination_class = CustomPagination

    @extend_schema(
        operation_id="all_products",
        summary="Product Fetch",
        description="""
            This endpoint returns all products.
        """,
        tags=tags,
        parameters=PRODUCT_PARAM_EXAMPLE,
    )
    def get(self, request, *args, **kwargs):
        products = Product.objects.select_related("category", "seller", "seller__user").all()
        filterset = ProductFilter(request.GET, queryset=products)
        if filterset.is_valid():
            queryset = filterset.qs
            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(queryset, request)
            serializer = self.serializer_class(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        else:
            return Response(filterset.errors, status=400)
## class ProductsView(APIView):
##     serializer_class = ProductSerializer
##
##     @extend_schema(
##         operation_id="all_products",
##         summary="Product Fetch",
##         description="""
##             This endpoint returns all products.
##         """,
##         tags=tags,
##         parameters=[
##             OpenApiParameter(
##                 name="max_price",
##                 description="Filter products by MAX current price",
##                 required=False,
##                 type=OpenApiTypes.INT,
##             ),
##             OpenApiParameter(
##                 name="min_price",
##                 description="Filter products by MIN current price",
##                 required=False,
##                 type=OpenApiTypes.INT,
##             ),
# #        ]
# #    )
##     def get(self, request, *args, **kwargs):
# #        products = Product.objects.select_related("category", "seller", "seller__user").all()
##
##         # Получаем параметры как строки
#  #       max_price_str = request.GET.get('max_price')
# #        min_price_str = request.GET.get('min_price')
##
##         # Преобразование и валидация
# #        try:
##             min_price = int(min_price_str) if min_price_str else None
##         except (ValueError, TypeError):
#             return Response(
#                 data={"message": "min_price и max_price должны быть целыми числами"},
#                 status=status.HTTP_400_BAD_REQUEST
#             )
#
#         # Проверка логики: оба параметра заданы
#         if max_price is not None and min_price is not None:
#             if max_price <= min_price:
#                 return Response(
#                     data={"message": "Максимальная цена должна быть больше минимальной"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#
#         # Фильтрация (max_price/min_price — int или None)
#         if max_price is not None:
#             products = products.filter(price_current__lte=max_price)
#         if min_price is not None:
#             products = products.filter(price_current__gte=min_price)
#
#         serializer = self.serializer_class(products, many=True)
#         return Response(data=serializer.data, status=status.HTTP_200_OK)


class ProductsBySellerView(APIView):
    serializer_class = ProductSerializer
    permission_classes = [IsSeller]

    @extend_schema(
        summary="Seller Products Fetch",
        description="""
            This endpoint returns all products in a particular seller.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        seller = Seller.objects.get_or_none(slug=kwargs["slug"])
        if not seller:
            return Response(data={"message": "Seller does not exist!"}, status=404)
        products = Product.objects.select_related("category", "seller", "seller__user").filter(seller=seller)
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)


class ProductView(APIView):
    serializer_class = ProductSerializer
    permission_classes = [IsSeller]

    def get_object(self, slug):
        product = Product.objects.get_or_none(slug=slug)
        return product

    @extend_schema(
        operation_id="product_detail",
        summary="Product Details Fetch",
        description="""
            This endpoint returns the details for a product via the slug.
        """,
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        product = self.get_object(kwargs['slug'])
        if not product:
            return Response(data={"message": "Product does not exist!"}, status=404)
        serializer = self.serializer_class(product)
        return Response(data=serializer.data, status=200)


class CartView(APIView):
    serializer_class = OrderItemSerializer
    permission_classes = [IsSeller]

    @extend_schema(
        summary="Cart Items Fetch",
        description="""
            This endpoint returns all items in a user cart.
        """,
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        orderitems = OrderItem.objects.filter(user=user, order=None).select_related(
            "product", "product__seller", "product__seller__user")
        serializer = self.serializer_class(orderitems, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Toggle Item in cart",
        description="""
            This endpoint allows a user or guest to add/update/remove an item in cart.
            If quantity is 0, the item is removed from cart
        """,
        tags=tags,
        request=ToggleCartItemSerializer,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = ToggleCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        quantity = data["quantity"]

        product = Product.objects.select_related("seller", "seller__user").get_or_none(slug=data["slug"])
        if not product:
            return Response({"message": "No Product with that slug"}, status=404)
        orderitem, created = OrderItem.objects.update_or_create(
            user=user,
            order=None,
            product=product,
            defaults={"quantity": quantity},
        )
        resp_message_substring = "Updated In"
        status_code = 200
        if created:
            status_code = 201
            resp_message_substring = "Added To"
        if orderitem.quantity == 0:
            resp_message_substring = "Removed From"
            orderitem.delete()
            data = None
        if resp_message_substring != "Removed From":
            serializer = self.serializer_class(orderitem)
            data = serializer.data
        return Response(data={"message": f"Item {resp_message_substring} Cart", "item": data}, status=status_code)


class CheckoutView(APIView):
    serializer_class = CheckoutSerializer
    permission_classes = [IsSeller]

    @extend_schema(
        summary="Checkout",
        description="""
               This endpoint allows a user to create an order through which payment can then be made through.
               """,
        tags=tags,
        request=CheckoutSerializer,
    )
    def post(self, request, *args, **kwargs):
        # Proceed to checkout
        user = request.user
        orderitems = OrderItem.objects.filter(user=user, order=None)
        if not orderitems.exists():
            return Response({"message": "No Items in Cart"}, status=404)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_id = data.get("shipping_id")
        # Получаем информацию о доставке на основе идентификатора доставки, введенного пользователем.
        shipping = ShippingAddress.objects.get_or_none(id=shipping_id)
        if not shipping:
            return Response({"message": "No shipping address with that ID"}, status=404)

        fields_to_update = [
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "country",
            "zipcode",
        ]
        data = {}
        for field in fields_to_update:
            value = getattr(shipping, field)
            data[field] = value

        order = Order.objects.create(user=user, **data)
        orderitems.update(order=order)

        serializer = OrderSerializer(order)
        return Response(data={"message": "Checkout Successful", "item": serializer.data}, status=200)