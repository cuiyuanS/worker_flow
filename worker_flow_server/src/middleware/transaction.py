import traceback
from collections.abc import Callable

from fastapi import Request, Response
from pydantic import ValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .global_ctx import g
from src.helper.response import json_response
from src.schema.base import convert_errors
from src.helper.logs import web_logger


async def transaction_init():
    from src import mongodb_client
    g.session = await mongodb_client.start_session()
    g.session.start_transaction()


async def transaction_rollback():
    try:
        if hasattr(g, "session"):
            await g.session.abort_transaction()
    except:
        pass


async def transaction_commit():
    try:
        if hasattr(g, "session"):
            await g.session.commit_transaction()
    except:
        pass


async def transaction_close():
    if hasattr(g, 'session'):
        await g.session.end_session()


async def session_dispatch(
        request: Request,
        call_next: Callable,
) -> Response:
    await transaction_init()
    try:
        response = await call_next(request)
        await transaction_commit()
    except ValidationError as e:
        errors = convert_errors(e)
        for i in errors:
            i.pop("url")
        return json_response(err=str(errors))
    except Exception as e:
        await transaction_rollback()
        traceback_str = traceback.format_exc()
        web_logger.error(traceback_str)
        return json_response(err=str(e))
    finally:
        await transaction_close()
    return response


class TransactionMiddware(BaseHTTPMiddleware):  # noqa
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app, session_dispatch)
