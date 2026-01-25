from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field

from apps.profiles.serializers import ShippingAddressSerializer


class CategorySerializer(serializers.Serializer):
    name = serializers.CharField()
    slug = serializers.SlugField(read_only=True)
    image = serializers.ImageField()


class SellerShopSerializer(serializers.Serializer):
    name = serializers.CharField(source="business_name")
    slug = serializers.SlugField()
    avatar = serializers.CharField(source="user.avatar")


class ProductSerializer(serializers.Serializer):
    seller = SellerShopSerializer()
    name = serializers.CharField()
    slug = serializers.SlugField()
    desc = serializers.CharField()
    price_old = serializers.DecimalField(max_digits=10, decimal_places=2)
    price_current = serializers.DecimalField(max_digits=10, decimal_places=2)
    category = CategorySerializer()
    in_stock = serializers.IntegerField()
    image1 = serializers.ImageField()
    image2 = serializers.ImageField(required=False)
    image3 = serializers.ImageField(required=False)


class CreateProductSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)
    desc = serializers.CharField()
    price_current = serializers.DecimalField(max_digits=10, decimal_places=2)
    category_slug = serializers.SlugField()
    in_stock = serializers.IntegerField()
    image1 = serializers.ImageField()
    image2 = serializers.ImageField(required=False)
    image3 = serializers.ImageField(required=False)


class OrderItemProductSerializer(serializers.Serializer):
    seller = SellerShopSerializer()
    name = serializers.CharField()
    slug = serializers.SlugField()
    price = serializers.DecimalField(
        max_digits=10, decimal_places=2, source="price_current"
    )


class OrderItemSerializer(serializers.Serializer):
    product = OrderItemProductSerializer()
    quantity = serializers.IntegerField()
    total = serializers.DecimalField(max_digits=10, decimal_places=2, source="get_total")


class ToggleCartItemSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    quantity = serializers.IntegerField(min_value=0)


class CheckoutSerializer(serializers.Serializer):
    shipping_id = serializers.UUIDField()


class OrderSerializer(serializers.Serializer):
    tx_ref = serializers.CharField()
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    delivery_status = serializers.CharField()
    payment_status = serializers.CharField()
    date_delivered = serializers.DateTimeField()
    shipping_details = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(
        max_digits=100, decimal_places=2, source="get_cart_subtotal"
    )
    total = serializers.DecimalField(
        max_digits=100, decimal_places=2, source="get_cart_total"
    )

    @extend_schema_field(ShippingAddressSerializer)
    def get_shipping_details(self, obj):
        return ShippingAddressSerializer(obj).data