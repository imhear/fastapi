<<<<<<< HEAD
=======
# app/main.py
from app.core.middleware import RequestIDMiddleware
>>>>>>> develop
from fastapi import FastAPI
from app.core.config import settings
from app.di.container import Container
from app.modules.user.api import router as user_router
from app.modules.role.api import router as role_router
<<<<<<< HEAD
=======
from app.modules.auth.api import router as auth_router
>>>>>>> develop


def create_app() -> FastAPI:
    container = Container()
    container.wire(modules=[
        "app.modules.user.api",
        "app.modules.role.api",
<<<<<<< HEAD
=======
        "app.modules.auth.api",
>>>>>>> develop
        "app.composers.user_detail",
    ])

    app = FastAPI(title=settings.PROJECT_NAME)
    app.container = container  # 可选，便于其他位置访问

    app.include_router(user_router, prefix="/api/v1")
    app.include_router(role_router, prefix="/api/v1")
<<<<<<< HEAD
=======
    app.include_router(auth_router, prefix="/api/v1")

    # 注册request_id中间件
    app.add_middleware(RequestIDMiddleware)

    # 日志处理器生命周期管理
    @app.on_event("startup")
    async def startup():
        log_svc = container.log_service()
        log_svc.processor.start()

    @app.on_event("shutdown")
    async def shutdown():
        log_svc = container.log_service()
        await log_svc.processor.stop()
>>>>>>> develop

    return app


app = create_app()