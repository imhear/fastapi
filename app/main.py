"""
项目主入口文件
app/main.py
上次更新：2026/3/23
"""
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html
from pathlib import Path

# ========== 新增：初始化结构化日志 ==========
from app.core.logging import configure_structlog
configure_structlog()

from app.config.config import settings

from app.core.middleware.context_middleware import ContextMiddleware
from app.core.middleware.log_middleware import AccessLogMiddleware
from app.core.middleware.audit_middleware import BizAuditLogMiddleware
from app.core.exception.handler import global_exception_handler
from app.api.v1.endpoints import user, auth


def create_app() -> FastAPI:
    # 禁用默认的 Swagger UI 和 ReDoc
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0",
        docs_url=None,  # 禁用默认 /docs
        redoc_url=None  # 禁用默认 /redoc
    )

    # 1. 注册请求上下文中间件,ContextMiddleware 必须是第一个注册的中间件
    app.add_middleware(ContextMiddleware)

    # 2. 注册系统访问日志中间件
    app.add_middleware(AccessLogMiddleware)

    # 3. 业务审计日志中间件（新增）
    app.add_middleware(BizAuditLogMiddleware)

    # 4. 注册全局异常处理器
    app.add_exception_handler(Exception, global_exception_handler)

    # 注册路由
    app.include_router(user.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")

    # 挂载 Swagger UI 静态文件
    static_dir = Path(__file__).parent / "api" / "static" / "swagger-ui"
    if not static_dir.exists():
        raise RuntimeError(f"Swagger UI 静态文件目录不存在: {static_dir}，请手动创建并放置资源文件")
    app.mount(
        "/static/swagger-ui",
        StaticFiles(directory=str(static_dir)),
        name="swagger_static"
    )

    # 自定义 Swagger UI 路由
    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        return get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=f"{app.title} - Swagger UI",
            swagger_js_url="/static/swagger-ui/swagger-ui-bundle.js",
            swagger_css_url="/static/swagger-ui/swagger-ui.css",
            swagger_favicon_url="/static/swagger-ui/favicon.png",
            # 如果未来需要 OAuth2 重定向，可添加以下参数
            # oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        )

    # （可选）OAuth2 重定向路由（如需 OAuth2 认证可取消注释）
    @app.get("/docs/oauth2-redirect", include_in_schema=False)
    async def swagger_ui_redirect():
        return get_swagger_ui_oauth2_redirect_html()

    return app


app = create_app()

# 以下测试代码保留不变
from pydantic import BaseModel
class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}


@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    return {"item_name": item.name, "item_id": item_id}