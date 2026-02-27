# app/main.py
from fastapi import FastAPI
from app.core.config import settings
from app.di.container import Container
from app.modules.user.api import router as user_router
from app.modules.role.api import router as role_router
from app.modules.auth.api import router as auth_router


def create_app() -> FastAPI:
    container = Container()
    container.wire(modules=[
        "app.modules.user.api",
        "app.modules.role.api",
        "app.modules.auth.api",
        "app.composers.user_detail",
    ])

    app = FastAPI(title=settings.PROJECT_NAME)
    app.container = container  # 可选，便于其他位置访问

    app.include_router(user_router, prefix="/api/v1")
    app.include_router(role_router, prefix="/api/v1")
    app.include_router(auth_router, prefix="/api/v1")

    return app


app = create_app()