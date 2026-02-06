from drf_spectacular.utils import OpenApiParameter, OpenApiTypes

PROFILE_PARAM_EXAMPLE = [
    OpenApiParameter(
        name="slug",
        description="Уникальный слаг,который есть у каждого товара",
        required=True,
        type=OpenApiTypes.STR,
    ),
]
DELETE_PARAM = [
    OpenApiParameter(
        name="slug",
        description="Уникальный слаг,который есть у каждого товара",
        required=True,
        type=OpenApiTypes.STR,
    ),
    OpenApiParameter(
        name="var_delete",
        description="Хотите безвозвратно удалить отзыв? Если да, введите yes",
        required=False,
        type=OpenApiTypes.STR,
    ),
]