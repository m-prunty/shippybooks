"""Tests for health endpoint logic."""

from __future__ import annotations

import threading
import time

import shippybooks.api.endpoints.health as health_module
from shippybooks.main import create_app


class DummyResponse:
    def __init__(self) -> None:
        self.status_code = 200


def _request(app):
    async def receive():
        return {"type": "http.request"}

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/health",
        "headers": [],
        "query_string": b"",
        "app": app,
    }
    from starlette.requests import Request

    return Request(scope, receive)


def test_live_health_ok():
    body = health_module.health_live()
    assert body.status == "ok"
    assert body.check == "live"
    assert body.service == "shippybooks-api"
    assert body.version
    assert body.timestamp
    assert body.checks is None


def test_ready_health_ok_schema():
    app = create_app()
    req = _request(app)
    resp = DummyResponse()
    body = health_module.health_ready(req, resp)
    assert resp.status_code == 200
    assert body.status in {"ok", "degraded"}
    assert body.check == "ready"
    assert body.service == "shippybooks-api"
    assert isinstance(body.duration_ms, float)
    assert body.checks is not None
    names = {c.name for c in body.checks}
    assert {"database", "config", "event_store", "notification_stream"} <= names
    for check in body.checks:
        assert check.status in {"ok", "degraded", "unhealthy"}
        assert isinstance(check.required, bool)
        assert isinstance(check.duration_ms, float)


def test_aggregate_health_verbose_false():
    app = create_app()
    req = _request(app)
    resp = DummyResponse()
    body = health_module.health(req, resp, verbose=False, deep=False)
    assert resp.status_code == 200
    assert body.check == "health"
    assert body.checks is None


def test_probe_timeout_does_not_wait_for_stuck_check():
    probe_started = threading.Event()
    release = threading.Event()

    def stuck_probe() -> None:
        probe_started.set()
        release.wait()

    def release_probe() -> None:
        probe_started.wait()
        time.sleep(0.2)
        release.set()

    releaser = threading.Thread(target=release_probe)
    releaser.start()

    try:
        started = time.perf_counter()
        result, error = health_module._run_with_timeout(
            stuck_probe, timeout_s=0.01
        )
        elapsed = time.perf_counter() - started
    finally:
        release.set()
        releaser.join(timeout=1)

    assert result is None
    assert error == "timed out"
    assert elapsed < 0.15


def test_ready_unhealthy_when_database_check_fails(monkeypatch):
    def bad_db_check(timeout_s: float = 0.5):
        return health_module.CheckResult(
            name="database",
            status="unhealthy",
            required=True,
            duration_ms=1.0,
            message="ping timed out",
        )

    monkeypatch.setattr(health_module, "_check_database", bad_db_check)
    app = create_app()
    req = _request(app)
    resp = DummyResponse()
    body = health_module.health_ready(req, resp)
    assert resp.status_code == 503
    assert body.status == "unhealthy"
    assert body.checks is not None
    db = next(c for c in body.checks if c.name == "database")
    assert db.status == "unhealthy"
    assert db.required is True
