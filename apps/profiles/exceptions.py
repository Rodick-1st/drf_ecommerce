from rest_framework.exceptions import APIException


class ObjectNotFound(APIException):
    status_code = 404
    default_detail = 'Объект не найден'
    default_code = 'object_not_found'

    def __init__(self, detail=None, model_name=None):
        if detail is None and model_name:
            detail = f"{model_name} не найден"
        super().__init__(detail=detail)