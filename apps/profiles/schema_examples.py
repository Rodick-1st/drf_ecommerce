from drf_spectacular.utils import OpenApiParameter, OpenApiTypes


DELETE_PARAM = [

    OpenApiParameter(
        name="variant_delete",
        description="Хотите безвозвратно удалить отзыв? Если да, введите yes",
        required=False,
        type=OpenApiTypes.STR,
    ),
]

