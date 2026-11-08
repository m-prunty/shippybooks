"""CQRS Notification System — application factory."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import books_router, notifications_router, orders_router
from .bootstrap import build_app_state
from .db import Base, BookORM, OrderItemORM, OrderORM, engine


def create_app() -> FastAPI:
    """Construct and wire the FastAPI application."""

    app = FastAPI(title="CQRS Notification System")
    app.state.app_state = build_app_state()

    app.include_router(books_router, prefix="/api/v1")
    app.include_router(orders_router, prefix="/api/v1")
    app.include_router(notifications_router, prefix="/api/v1")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://mprunty.com",
            "https://www.mprunty.com",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def _create_tables() -> None:
        # Ensure ORM metadata is loaded before create_all.
        _ = (BookORM, OrderORM, OrderItemORM)
        Base.metadata.create_all(bind=engine)

    return app


# Module-level instance required by uvicorn's string reference with reload=True
app = create_app()


def main() -> None:
    """Start the uvicorn server."""
    import uvicorn

    uvicorn.run("shippybooks.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
