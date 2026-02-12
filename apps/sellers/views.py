from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsSeller
from apps.common.utils import set_dict_attr
from apps.profiles.exceptions import ObjectNotFound
from apps.shop.models import Category, Product
from apps.sellers.models import Seller
from apps.sellers.serializers import SellerSerializer
from apps.profiles.models import Order, OrderItem
from apps.shop.serializers import ProductSerializer, CreateProductSerializer, OrderSerializer, \
    CheckItemOrderSerializer


tags = ["Sellers"]


class SellersView(APIView):
    serializer_class = SellerSerializer

    @extend_schema(
        summary="Apply to become a seller",
        description="""
            This endpoint allows a buyer to apply to become a seller.
        """,
        tags=tags)
    def post(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data, partial=False)
        if serializer.is_valid():
            data = serializer.validated_data
            seller, _ = Seller.objects.update_or_create(user=user, defaults=data)
            user.account_type = 'SELLER'
            user.save()
            serializer = self.serializer_class(seller)
            return Response(data=serializer.data, status=201)
        else:
            return Response(data=serializer.errors, status=400)


class SellerProductsView(APIView):
    serializer_class = ProductSerializer
    permission_classes = [IsSeller]

    @extend_schema(
        summary="Seller Products Fetch",
        description="""
            This endpoint returns all products from a seller.
            Products can be filtered by name, sizes or colors.
        """,
        tags=tags, )
    def get(self, request, *args, **kwargs):
        seller = Seller.objects.get_or_none(user=request.user, is_approved=True)
        if not seller:
            return Response(data={"message": "Access is denied"}, status=403)
        products = Product.objects.select_related("category", "seller", "seller__user").filter(seller=seller)
        serializer = self.serializer_class(products, many=True)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Create a product",
        description="""
            This endpoint allows a seller to create a product.
        """,
        tags=tags,
        request=CreateProductSerializer,
        responses=ProductSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = CreateProductSerializer(data=request.data)
        seller = Seller.objects.get_or_none(user=request.user, is_approved=True)
        if not seller:
            return Response(data={"message": "Access is denied"}, status=403)
        if serializer.is_valid():
            data = serializer.validated_data
            category_slug = data.pop("category_slug", None)
            category = Category.objects.get_or_none(slug=category_slug)
            if not category:
                return Response(data={"message": "Category does not exist!"}, status=404)
            data['category'] = category
            data['seller'] = seller
            new_prod = Product.objects.create(**data)
            serializer = ProductSerializer(new_prod)
            return Response(serializer.data, status=201)
        else:
            return Response(serializer.errors, status=400)


class SellerProductView(APIView):
    serializer_class = CreateProductSerializer
    permission_classes = [IsSeller]

    def get_object(self, request, slug):
        product = Product.objects.unfiltered(slug=slug)
        if product is None:
            raise ObjectNotFound("Такого продукта не существует")
        return product

    @extend_schema(
        summary="Seller Products Update",
        description="""
                This endpoint updates a seller product.
            """,
        tags=tags
    )
    def put(self, request, *args, **kwargs):
        product = self.get_object(request, kwargs['slug'])
        if not product:
            return Response(data={"message": "Product does not exist!"}, status=404)
        elif product.seller != request.user.seller:
            return Response(data={"message": "Access is denied"}, status=403)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            category_slug = data.pop("category_slug", None)
            category = Category.objects.get_or_none(slug=category_slug)
            if not category:
                return Response(data={"message": "Category does not exist!"}, status=404)
            data['category'] = category
            if data["price_current"] != product.price_current:
                data["price_old"] = product.price_current
            product = set_dict_attr(product, data)
            product.save()
            serializer = ProductSerializer(product)
            return Response(data=serializer.data, status=200)
        else:
            return Response(data=serializer.errors, status=400)

    @extend_schema(
        summary="Seller Products Delete",
        description="""
                This endpoint allows a seller to delete a product.
            """,
        tags=tags
    )
    def delete(self, request, *args, **kwargs):
        product = self.get_object(request, kwargs['slug'])
        if not product:
            return Response(data={"message": "Product does not exists!"}, status=404)
        elif product.seller != request.user.seller:
            return Response(data={"message": "Access is denied"}, status=403)
        product.hard_delete()
        return Response(data={"message": "Product deleted successfully"}, status=200)


class SellerOrdersView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsSeller]

    @extend_schema(
        operation_id="seller_orders_view",
        summary="Seller Orders Fetch",
        description="""
            This endpoint returns all orders for a particular seller.
        """,
        tags=tags
    )
    def get(self, request):
        seller = request.user.seller
        orders = (
            Order.objects.filter(orderitems__product__seller=seller)
            .distinct()
            .order_by("-created_at")
        )
        serializer = self.serializer_class(orders, many=True)
        return Response(data=serializer.data, status=200)


class SellerOrderItemsView(APIView):
    serializer_class = CheckItemOrderSerializer
    permission_classes = [IsSeller]

    @extend_schema(
        operation_id="seller_order_items_view",
        summary="Seller Items Order Fetch",
        description="""
            This endpoint returns all items order for a particular seller.
        """,
        tags=tags,

    )
    def get(self, request, **kwargs):
        seller = request.user.seller
        order = Order.objects.get_or_none(tx_ref=kwargs["tx_ref"])
        if not order:
            return Response(data={"message": "Order does not exist!"}, status=404)
        order_items = OrderItem.objects.filter(order=order, product__seller=seller)
        serializer = self.serializer_class(order_items, many=True)
        return Response(data=serializer.data, status=200)