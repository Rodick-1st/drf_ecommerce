from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

PROFILE_PARAM_EXAMPLE = [
    OpenApiParameter(
        name="slug",
        description="Уникальный слаг,который есть у каждого товара",
        required=True,
        type=OpenApiTypes.STR,
    ),


]