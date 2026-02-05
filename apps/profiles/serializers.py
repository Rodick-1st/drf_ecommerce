from rest_framework import serializers

from apps.profiles.models import RATING_CHOICES


class ProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=25)
    last_name = serializers.CharField(max_length=25)
    email = serializers.EmailField(read_only=True)
    avatar = serializers.ImageField(required=False)
    account_type = serializers.CharField(read_only=True)


class ShippingAddressSerializer(serializers.Serializer):
    id = serializers.UUIDField(read_only=True)
    full_name = serializers.CharField(max_length=255)
    email = serializers.EmailField()
    phone = serializers.CharField(max_length=12)
    address = serializers.CharField(max_length=1000)
    city = serializers.CharField(max_length=100)
    country = serializers.CharField(max_length=200)
    zipcode = serializers.CharField(max_length=6)


class ProductReviewSerializer(serializers.Serializer):
    user = ProfileSerializer(read_only=True)
    product = serializers.SlugField()
    rating = serializers.ChoiceField(choices=RATING_CHOICES)
    text = serializers.CharField()

    def validate_rating(self, value):
        if value not in [1, 2, 3, 4, 5]:
            raise serializers.ValidationError("Rating must be between 1 and 5")
        return value