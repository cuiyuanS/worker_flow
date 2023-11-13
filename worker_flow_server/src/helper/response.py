import json
from datetime import datetime
from typing import Union, Any

from fastapi.responses import Response, JSONResponse
from fastapi import status


class JSONDumpResponse(JSONResponse):

    def render(self, content: Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
            default=self.parse
        ).encode("utf-8")

    def parse(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M')
        raise TypeError("Object of type '%s' is not JSON serializable" % type(obj).__name__)


def json_response(data: Any = "", err: str = "", status_code=200) -> JSONDumpResponse:
    res = {"err": err, "data": data}
    return JSONDumpResponse(content=res, status_code=status_code)


def server_json_response(*, code=200, data: Union[list, dict, str], message="Success") -> Response:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': code,
            'message': message,
            'data': data,
        }
    )


def resp_400(*, data: str = None, message: str = "BAD REQUEST") -> Response:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'code': 400,
            'message': message,
            'data': data,
        }
    )


def resp_500(*, message: str = "Internal Server Error") -> Response:
    from src.helper.logs import web_logger
    web_logger.exception(message)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            'code': 500,
            'message': message,
        }
    )
