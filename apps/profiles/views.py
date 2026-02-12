from uuid import UUID
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.common.utils import set_dict_attr
from apps.profiles.exceptions import ObjectNotFound
from apps.profiles.schema_examples import DELETE_PARAM
from apps.profiles.serializers import ProfileSerializer, ShippingAddressSerializer, ProductReviewSerializer, \
    BaseProductReviewSerializer
from apps.profiles.models import ShippingAddress, Order, OrderItem, ProductReview
from apps.shop.models import Product
from apps.shop.serializers import OrderSerializer, CheckItemOrderSerializer
from apps.common.permissions import IsOwner, IsSeller


tags = ["Profiles"]
my_tag = ["Сам сделал :)"]


class ProfileView(APIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwner, IsSeller]

    @extend_schema(
        summary="Retrieve Profile",
        description="""
            This endpoint allows a user to retrieve his/her profile.
        """,
        tags=tags,
    )
    def get(self, request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Update Profile",
        description="""
                This endpoint allows a user to update his/her profile.
            """,
        tags=tags,
        request={"multipart/form-data": serializer_class},
    )
    def put(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = set_dict_attr(user, serializer.validated_data)
        user.save()
        serializer = self.serializer_class(user)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Deactivate account",
        description="""
            This endpoint allows a user to deactivate his/her account.
        """,
        tags=tags,
    )
    def delete(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response(data={"message": "User Account Deactivated"})


class ShippingAddressesView(APIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsOwner, IsSeller]

    @extend_schema(
        summary="Shipping Addresses Fetch",
        description="""
            This endpoint returns all shipping addresses associated with a user.
        """,
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        shipping_addresses = ShippingAddress.objects.filter(user=user)

        serializer = self.serializer_class(shipping_addresses, many=True)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Create Shipping Address",
        description="""
            This endpoint allows a user to create a shipping address.
        """,
        tags=tags,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_address, _ = ShippingAddress.objects.get_or_create(user=user, **data)
        serializer = self.serializer_class(shipping_address)
        return Response(data=serializer.data, status=201)


class ShippingAddressViewID(APIView):
    serializer_class = ShippingAddressSerializer
    permission_classes = [IsOwner, IsSeller]

    def get_object(self, user, shipping_id):
        shipping_address = ShippingAddress.objects.get_or_none(id=shipping_id)
        if not shipping_address:
            raise NotFound(detail={"message": "Shipping Address does not exist!"}, code=404)
        self.check_object_permissions(self.request, shipping_address)
        return shipping_address

    @extend_schema(
        summary="Shipping Address Fetch ID",
        description="""
        This endpoint returns a single shipping address associated with a user.
        """,
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        user = request.user
        shipping_address = self.get_object(user, kwargs["id"])
        serializer = self.serializer_class(shipping_address)
        return Response(data=serializer.data)

    @extend_schema(
        summary="Update Shipping Address ID",
        description="""
        This endpoint allows a user to update his/her shipping address.
        """,
        tags=tags,
    )
    def put(self, request, *args, **kwargs):
        user = request.user
        shipping_address = self.get_object(user, kwargs["id"])
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_address = set_dict_attr(shipping_address, data)
        shipping_address.save()
        serializer = self.serializer_class(shipping_address)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Delete Shipping Address ID",
        description="""
        This endpoint allows a user to delete his/her shipping address.
        """,
        tags=tags,
    )
    def delete(self, request, *args, **kwargs):
        user = request.user
        shipping_address = self.get_object(user, kwargs["id"])
        shipping_address.delete()
        return Response(data={"message": "Shipping address deleted successfully"}, status=200)


class OrdersView(APIView):
    serializer_class = OrderSerializer
    permission_classes = [IsOwner, IsSeller]

    @extend_schema(
        operation_id="orders_view",
        summary="Orders Fetch",
        description="""
            This endpoint returns all orders for a particular user.
        """,
        tags=tags
    )
    def get(self, request):
        user = request.user
        orders = (Order.objects.filter(user=user).select_related("user")
                  .prefetch_related("orderitems", "orderitems__product")
                  .order_by("-created_at"))
        serializer = self.serializer_class(orders, many=True)
        return Response(data=serializer.data, status=200)


class OrderItemsView(APIView):
    serializer_class = CheckItemOrderSerializer
    permission_classes = [IsOwner, IsSeller]

    @extend_schema(
        operation_id="order_items_view",
        summary="Items Order Fetch",
        description="""
            This endpoint returns all items order for a particular user.
        """,
        tags=tags,

    )
    def get(self, request, **kwargs):
        order = Order.objects.get_or_none(tx_ref=kwargs["tx_ref"])
        if not order or order.user != request.user:
            return Response(data={"message": "Order does not exist!"}, status=404)
        order_items = OrderItem.objects.filter(order=order).select_related(
            "product", "product__seller", "product__seller__user"
        )
        serializer = self.serializer_class(order_items, many=True)
        return Response(data=serializer.data, status=200)


########################################################################################################################
                                        # # # ВНИЗУ МОИ ВЬЮШКИ # # #
########################################################################################################################


class ProductReviewDetailView(APIView):
    serializer_class = ProductReviewSerializer
    # permission_classes = ...

    def get_object(self, user, slug, method=None):
        review = ProductReview.objects.select_related("product", "user").get_or_none(
            user=user, product__slug=slug)
        if review is None and method != 'post':
            raise ObjectNotFound("У вас нет отзыва на данный товар")
        self.check_object_permissions(self.request, review)
        return review

    @extend_schema(
        summary="Твой отзыв на товар",
        description="""
        Введи slug продукта, чтобы посмотреть свой 
        уникальный отзыв на продукт (товар)
                """,
        tags=my_tag,
    )
    def get(self, request, product_slug):
        review = self.get_object(user=request.user, slug=product_slug)
        serializer = self.serializer_class(review)
        return Response(data=serializer.data, status=200)

    @extend_schema(
        summary="Создание отзыва",
        description="""
        Введи slug продукта, а также полностью заполни требуемые поля,
        чтобы оставить свой отзыв на продукт (товар)!
            """,
        request=BaseProductReviewSerializer,
        tags=my_tag,
    )
    def post(self, request, product_slug):
        review = self.get_object(request.user,product_slug, method='post')
        if review:
            return Response({"message": "Вы уже писали отзыв на данный товар!"}, status=403)
        product = Product.objects.get_or_none(slug=product_slug)
        if not product:
            return Response({"message": "No Product with that slug"}, status=404)
        serializer = BaseProductReviewSerializer(data=request.data)
        if not serializer.is_valid(raise_exception=True):
            return Response(serializer.errors, status=400)
        user = request.user
        data = serializer.validated_data
        review = ProductReview.objects.create(user=user,product=product, rating=data['rating'], text=data['text'])
        serializer = self.serializer_class(review)
        return Response(data={"message": "Create your review успешно:)", "item": serializer.data}, status=201)

    @extend_schema(
        summary="Обновление отзыва",
        description="""
        Обновление, в т.ч. частичное обновление, отзыва!
                """,
        request=BaseProductReviewSerializer,
        tags=my_tag,
    )
    def patch(self, request, product_slug):
        review = self.get_object(user=request.user, slug=product_slug)
        serializer = BaseProductReviewSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            review = set_dict_attr(review, data)
            review.save()
            serializer = self.serializer_class(review)
            return Response(data={"message": "Обновление review успешно:)", "item": serializer.data}, status=201)

    @extend_schema(
        summary="Удаление отзыва",
        description="""
        Введи slug продукта, чтобы начать процесс сокрытия/удаления отзыва!
        Чтобы скрыть отзыв, оставь поле variant_delete пустым.
        Чтобы безвозвратно удалить свой отзыв, введи YES в поле variant_delete!
                    """,
        parameters=DELETE_PARAM,
        tags=my_tag,
    )
    def delete(self, request, product_slug):
        review = self.get_object(user=request.user, slug=product_slug)
        variable_del = request.GET.get('variant_delete', '')
        if variable_del.lower()=='yes':
            review.hard_delete()
            return Response(data={"message": "Отзыв удалён безвозвратно!"}, status=200)
        review.delete()
        return Response(data={"message": "Ваш отзыв успешно скрыт!"}, status=200)


@extend_schema_view(
    get=extend_schema(
        summary="Твой скрытый отзыв на товар",
        description="Введи slug продукта, чтобы увидеть свой скрытый отзыв",
    ),
    tags=my_tag,
    delete=extend_schema(
        summary="Удалить скрытый отзыв",
        description="Введи slug продукта, чтобы безвозвратное удалить скрытый отзыв",
    ),
)
class DeletedProductReviewDetail(ProductReviewDetailView):
    http_method_names = ['get', 'delete', 'head', 'options']

    def get_object(self, user, slug, **kwargs):
        deleted_reviews = ProductReview.objects.get_deleted(user=user, product__slug=slug)
        if deleted_reviews is None:
            raise ObjectNotFound("У вас нет скрытого отзыва на данный товар")
        self.check_object_permissions(self.request, deleted_reviews)
        return deleted_reviews


@extend_schema_view(
    get=extend_schema(
        summary="Все ваши отзывы",
        description="Здесь отображаются все отзывы, написанные вами!",
        tags=my_tag,
    ),)
class ProductReviewsListView(ListAPIView):
    serializer_class = ProductReviewSerializer

    def get_queryset(self):
        return ProductReview.objects.filter(user=self.request.user)
