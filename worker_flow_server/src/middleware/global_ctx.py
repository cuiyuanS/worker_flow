from collections.abc import Awaitable, Callable
from contextvars import ContextVar, copy_context
from typing import Any

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class Globals:
    __slots__ = ("_vars", "_defaults")

    _vars: dict[str, ContextVar]
    _defaults: dict[str, Any]

    def __init__(self) -> None:
        object.__setattr__(self, '_vars', {})
        object.__setattr__(self, '_defaults', {})

    def set_default(self, name: str, default: Any) -> None:
        """Set a default value for a variable."""

        # Ignore if default is already set and is the same value
        if (
                name in self._defaults
                and default is self._defaults[name]
        ):
            return

        # Ensure we don't have a value set already - the default will have
        # no effect then
        if name in self._vars:
            raise RuntimeError(
                f"Cannot set default as variable {name} was already set",
            )

        # Set the default already!
        self._defaults[name] = default

    def _get_default_value(self, name: str) -> Any:
        """Get the default value for a variable."""

        default = self._defaults.get(name, None)

        return default() if callable(default) else default

    def _ensure_var(self, name: str) -> None:
        """Ensure a ContextVar exists for a variable."""

        if name not in self._vars:
            default = self._get_default_value(name)
            self._vars[name] = ContextVar(f"globals:{name}", default=default)

    def __getattr__(self, name: str) -> Any:
        """Get the value of a variable."""

        self._ensure_var(name)
        return self._vars[name].get()

    def __setattr__(self, name: str, value: Any) -> None:
        """Set the value of a variable."""

        self._ensure_var(name)
        self._vars[name].set(value)


async def globals_middleware_dispatch(
        request: Request,
        call_next: Callable,
) -> Response:
    ctx = copy_context()

    def _call_next() -> Awaitable[Response]:
        return call_next(request)

    return await ctx.run(_call_next)


class GlobalsMiddleware(BaseHTTPMiddleware):  # noqa
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app, globals_middleware_dispatch)


g = Globals()


async def set_globals(
        request: Request,
        call_next: Callable,
) -> Response:
    g.client_ip = request.headers.get("X-Forwarded-For") or request.client.host
    response = await call_next(request)
    return response


class SetGlobalsMiddleware(BaseHTTPMiddleware):  # noqa
    def __init__(self, app: ASGIApp) -> None:
        super().__init__(app, set_globals)
