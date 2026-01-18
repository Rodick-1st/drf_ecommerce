from uuid import UUID
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.views import APIView
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema


from apps.common.utils import set_dict_attr
from apps.profiles.models import ShippingAddress
from apps.profiles.serializers import ProfileSerializer, ShippingAddressSerializer

tags = ["Profiles"]


class ProfileView(APIView):
    serializer_class = ProfileSerializer

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

    def get_object(self, user, shipping_id):
        try:
            shipping_uuid = UUID(shipping_id)
        except ValueError as exc:
            raise ValidationError({"message": "Invalid shipping id UUID format"}) from exc

        shipping_address = ShippingAddress.objects.get_or_none(user=user, id=shipping_uuid)
        if shipping_address is None:
            raise NotFound(detail={"message": "Shipping Address does not exist!"}, code=404)

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