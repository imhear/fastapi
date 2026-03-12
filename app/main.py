"""
项目主入口文件
app/main.py
上次更新：2026/3/12
"""
from fastapi import FastAPI
from app.config.config import settings

from app.core.middleware.log_middleware import AccessLogMiddleware
from app.core.exception.handler import global_exception_handler
from app.api.v1.endpoints import user, auth


def create_app() -> FastAPI:

    app = FastAPI(title=settings.PROJECT_NAME, version="1.0")

    # 注册中间件
    app.add_middleware(AccessLogMiddleware)

    # 注册异常处理器
    app.add_exception_handler(Exception, global_exception_handler)

    # 注册路由
    app.include_router(user.router, prefix="/api/v1")
    app.include_router(auth.router, prefix="/api/v1")

    return app


app = create_app()


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