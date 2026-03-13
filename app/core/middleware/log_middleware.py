"""
系统访问日志中间件
app/core/middleware/log_middleware.py
"""
import logging
import time
import json
import re
from typing import Optional

from app.core.database import create_log_session
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.container import Container
from app.config.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class AccessLogMiddleware(BaseHTTPMiddleware):
    """系统访问日志中间件（显式管理session）"""
    async def dispatch(self, request: Request, call_next) -> Response:
        # 1. 生成request_id
        request_id = Container.log_service().generate_request_id()
        request.state.request_id = request_id

        # 2. 记录请求体（脱敏）
        request_body = None
        if settings.LOG_RECORD_BODY and request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                # 重置body供后续使用
                request._body = body
                if len(body) < settings.LOG_MAX_BODY_SIZE:
                    request_body = self._desensitize_body(body)
            except Exception:
                request_body = "无法解析的请求体"

        # 3. 记录开始时间
        start_time = time.perf_counter()
        response = None
        status_code = 500  # 默认状态码，异常时使用

        try:
            # 4. 执行请求
            response = await call_next(request)
            status_code = response.status_code
            return response
        finally:
            # 5.计算耗时
            execution_time = int((time.perf_counter() - start_time) * 1000)
            handler = self._get_handler_name(request)
            request.state.handler = handler
            # 日志中间件中operator_id的最终优化版
            try:
                operator_id = request.state.user_context.id if (
                        hasattr(request.state, "user_context") and request.state.user_context
                ) else None
            except Exception:
                operator_id = None

            # 6.构建日志数据（即使异常也尽量获取上下文）
            log_data = {
                "request_id": request_id,
                "request_uri": str(request.url.path),
                "request_method": request.method,
                "request_params": json.dumps(dict(request.query_params)),
                "request_body": request_body,
                "http_status": status_code,
                "execution_time": execution_time,
                "ip": request.client.host if request.client else "",
                "user_agent": request.headers.get("user-agent", ""),
                "operator_id": operator_id,  # 关键修改：读取user_context而非user ORM实例
                "handler": handler
            }

            # 7.异步记录日志（独立try块，不影响主流程）
            log_session: AsyncSession = None
            try:
                log_session = await create_log_session()  # 显式创建日志会话
                log_service = Container.log_service()
                await log_service.record_access_log(log_session, log_data)
                await log_session.commit()  # 3. 手动提交事务
            except Exception as e:
                # 异常时回滚
                if log_session and not log_session.is_active:
                    await log_session.rollback()
                logger.error(f"记录访问日志失败: {e}", exc_info=True)
            finally:
                # 最终确保关闭session
                if log_session and not log_session.is_active:
                    await log_session.close()


    def _desensitize_body(self, body: bytes) -> Optional[str]:
        """请求体脱敏"""
        try:
            data = json.loads(body)
            # 脱敏敏感字段
            sensitive_fields = ["password", "token", "secret", "mobile", "id_card"]
            for field in sensitive_fields:
                if field in data:
                    data[field] = "***"
            return json.dumps(data)
        except Exception:
            return body.decode("utf-8", errors="ignore")[:settings.LOG_MAX_BODY_SIZE]

    def _get_handler_name(self, request: Request) -> str:
        """稳定获取处理器名称"""
        endpoint = request.scope.get("endpoint")
        if not endpoint:
            return ""
        if hasattr(endpoint, "__name__"):
            return endpoint.__name__
        elif hasattr(endpoint, "__func__"):
            return f"{endpoint.__self__.__class__.__name__}.{endpoint.__func__.__name__}"
        return str(endpoint)