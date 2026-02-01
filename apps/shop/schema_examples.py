from drf_spectacular.utils import OpenApiParameter, OpenApiTypes


PRODUCT_PARAM_EXAMPLE = [
    OpenApiParameter(
        name="max_price",
        description="Filter products by MAX current price",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="min_price",
        description="Filter products by MIN current price",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="in_stock",
        description="Filter products by stock",
        required=False,
        type=OpenApiTypes.INT,
    ),
    OpenApiParameter(
        name="created_at",
        description="Filter products by date created",
        required=False,
        type=OpenApiTypes.DATE,
    ),
]