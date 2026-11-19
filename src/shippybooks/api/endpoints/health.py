"""Health endpoints for liveness, readiness, and diagnostics."""

from __future__ import annotations

import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import datetime, timezone
from importlib.metadata import PackageNotFoundError, version as pkg_version
from typing import Any, Literal, TypeVar

from fastapi import APIRouter, Query, Request, Response
from pydantic import BaseModel
from sqlalchemy import text

from ...db.session import engine
from ...settings import settings

router = APIRouter()

CheckStatus = Literal["ok", "degraded", "unhealthy"]
T = TypeVar("T")


class CheckResult(BaseModel):
    name: str
    status: CheckStatus
    required: bool
    duration_ms: float
    message: str | None = None
    data: dict[str, Any] | None = None


class HealthResponse(BaseModel):
    status: CheckStatus
    check: Literal["live", "ready", "health"]
    service: str
    version: str
    timestamp: str
    duration_ms: float | None = None
    checks: list[CheckResult] | None = None


def _utc_now() -> str:
    timestamp = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    return timestamp.replace("+00:00", "Z")


def _service_name() -> str:
    return "shippybooks-api"


def _service_version() -> str:
    try:
        return pkg_version("shippybooks")
    except PackageNotFoundError:
        return "0.1.0"


def _run_with_timeout(
    fn: Callable[[], T], timeout_s: float
) -> tuple[T | None, str | None]:
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fn)
    try:
        return future.result(timeout=timeout_s), None
    except FuturesTimeoutError:
        return None, "timed out"
    except Exception:
        return None, "check failed"
    finally:
        # Do not wait for a stuck probe after the readiness deadline expires.
        executor.shutdown(wait=False, cancel_futures=True)


def _check_database(timeout_s: float = 0.5) -> CheckResult:
    start = time.perf_counter()

    def ping() -> None:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

    _, err = _run_with_timeout(ping, timeout_s)
    duration_ms = (time.perf_counter() - start) * 1000
    if err is None:
        return CheckResult(
            name="database",
            status="ok",
            required=True,
            duration_ms=round(duration_ms, 3),
            message="connection and ping succeeded",
        )
    message = "ping timed out" if err == "timed out" else "database check failed"
    return CheckResult(
        name="database",
        status="unhealthy",
        required=True,
        duration_ms=round(duration_ms, 3),
        message=message,
    )


def _check_config() -> CheckResult:
    start = time.perf_counter()
    # Validate required runtime config is loadable/present without exposing values.
    ok = bool(getattr(settings, "database_url", None)) and bool(
        getattr(settings, "environment", None)
    )
    duration_ms = (time.perf_counter() - start) * 1000
    if ok:
        return CheckResult(
            name="config",
            status="ok",
            required=True,
            duration_ms=round(duration_ms, 3),
            message="required configuration loaded",
        )
    return CheckResult(
        name="config",
        status="unhealthy",
        required=True,
        duration_ms=round(duration_ms, 3),
        message="required configuration missing",
    )


def _check_event_store(request: Request) -> CheckResult:
    start = time.perf_counter()
    app_state = getattr(request.app.state, "app_state", None)
    # Command/event flow depends on initialized handlers/bus wiring at runtime.
    ok = (
        app_state is not None
        and getattr(app_state, "cmd_handler", None) is not None
        and getattr(app_state, "query_handler", None) is not None
    )
    duration_ms = (time.perf_counter() - start) * 1000
    if ok:
        return CheckResult(
            name="event_store",
            status="ok",
            required=True,
            duration_ms=round(duration_ms, 3),
            message="command/event handlers initialized",
        )
    return CheckResult(
        name="event_store",
        status="unhealthy",
        required=True,
        duration_ms=round(duration_ms, 3),
        message="command/event handlers unavailable",
    )


def _check_notification_stream(request: Request) -> CheckResult:
    start = time.perf_counter()
    app_state = getattr(request.app.state, "app_state", None)
    store = (
        getattr(app_state, "notification_store", None)
        if app_state is not None
        else None
    )
    ok = store is not None and hasattr(store, "append") and hasattr(store, "since")
    duration_ms = (time.perf_counter() - start) * 1000
    if ok:
        return CheckResult(
            name="notification_stream",
            status="ok",
            required=False,
            duration_ms=round(duration_ms, 3),
            message="notification subsystem initialized",
        )
    return CheckResult(
        name="notification_stream",
        status="degraded",
        required=False,
        duration_ms=round(duration_ms, 3),
        message="notification subsystem unavailable",
    )


def _aggregate_status(checks: list[CheckResult]) -> CheckStatus:
    if any(c.required and c.status == "unhealthy" for c in checks):
        return "unhealthy"
    if any(c.status in ("degraded", "unhealthy") for c in checks):
        return "degraded"
    return "ok"


def _evaluate(
    request: Request, mode: Literal["ready", "health"], deep: bool = False
) -> tuple[HealthResponse, int]:
    start = time.perf_counter()
    db_timeout = 2.0 if deep else 0.5
    checks = [
        _check_database(timeout_s=db_timeout),
        _check_config(),
        _check_event_store(request),
        _check_notification_stream(request),
    ]
    status = _aggregate_status(checks)
    duration_ms = (time.perf_counter() - start) * 1000
    body = HealthResponse(
        status=status,
        check=mode,
        service=_service_name(),
        version=_service_version(),
        timestamp=_utc_now(),
        duration_ms=round(duration_ms, 3),
        checks=checks,
    )
    http_status = 503 if status == "unhealthy" else 200
    return body, http_status


@router.get("/health/live", response_model=HealthResponse)
def health_live() -> HealthResponse:
    return HealthResponse(
        status="ok",
        check="live",
        service=_service_name(),
        version=_service_version(),
        timestamp=_utc_now(),
    )


@router.get("/health/ready", response_model=HealthResponse)
def health_ready(request: Request, response: Response) -> HealthResponse:
    body, status_code = _evaluate(request, mode="ready", deep=False)
    response.status_code = status_code
    return body


@router.get("/health", response_model=HealthResponse)
def health(
    request: Request,
    response: Response,
    verbose: bool = Query(True),
    deep: bool = Query(False),
) -> HealthResponse:
    body, status_code = _evaluate(request, mode="health", deep=deep)
    response.status_code = status_code
    if not verbose:
        return body.model_copy(update={"checks": None})
    return body
