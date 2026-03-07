# app/core/middleware.py
import logging
import uuid
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.exceptions import BusinessException
from app.core.responses import ApiResponse

logger = logging.getLogger(__name__)

class RequestIDMiddleware(BaseHTTPMiddleware):
    """全局中间件：为每个请求生成唯一request_id，用于链路追踪"""
    async def dispatch(self, request: Request, call_next):
        # 生成request_id（优先使用客户端传入的X-Request-ID，无则生成）
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id
        # 响应头返回request_id，方便客户端关联
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response

# 全局异常捕获（带日志）
class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            return await call_next(request)
        except BusinessException as e:
            # 记录业务异常日志（含request_id）
            logger.warning(
                f"[RequestID: {request.state.request_id}] "
                f"业务异常: {e.code} - {e.detail}"
            )
            return JSONResponse(
                status_code=e.status_code,
                content=ApiResponse.fail(code=e.code, msg=e.detail).dict()
            )
        except Exception as e:
            # 记录未捕获异常（含堆栈）
            logger.exception(
                f"[RequestID: {request.state.request_id}] "
                f"服务器未捕获异常: {str(e)}"
            )
            return JSONResponse(
                status_code=500,
                content=ApiResponse.fail(code="50000", msg=f"服务器错误：{str(e)}").dict()
            )