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
from app.core.log.context import LogContext, RequestParams
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.container import Container
from app.config.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

class AccessLogMiddleware(BaseHTTPMiddleware):
    """系统访问日志中间件（显式管理session）"""
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()  # 记录开始时间
        response = None
        status_code = 500  # 默认状态码

        try:
            # 预读取请求体并存储（供后续使用）
            if settings.LOG_RECORD_BODY and request.method in ["POST", "PUT", "PATCH"]:
                body = await request.body()
                request._body = body  # 存储原始body供后续使用

            response = await call_next(request)  # 执行请求
            status_code = response.status_code  # 获取实际状态码
            return response
        except Exception as e:
            # 捕获所有异常，确保finally块能正确处理
            logger.error(f"请求处理异常: {e}", exc_info=True)
            raise  # 重新抛出异常，让异常处理器处理
        finally:
            # 1. 获取预生成的LogContext
            log_context = getattr(request.state, "log_context", None)
            if not log_context:
                return  # 无上下文时直接返回，避免后续报错

            # 2. 强制更新用户上下文（确保获取最新值）
            user_context = getattr(request.state, "user_context", None)
            if user_context:
                log_context.user_context = user_context

            # 3. 补充日志信息
            log_context.execution_time = int((time.perf_counter() - start_time) * 1000)
            log_context.handler = self._get_handler_name(request)

            # 安全获取状态码
            if response is not None and hasattr(response, 'status_code'):
                log_context.http_status = response.status_code
            else:
                log_context.http_status = status_code

            # 4. 统一采集所有请求参数（解决原request_body为空的问题）
            # 读取预存储的body并脱敏
            body = None
            if hasattr(request, "_body") and request._body:
                body = LogContext._desensitize_body(request._body)

            # 安全创建 RequestParams
            try:
                log_context.request_params = RequestParams(
                    path_params=dict(request.path_params),
                    query_params=dict(request.query_params),
                    body=body  # 使用脱敏后的body
                )
            except Exception as e:
                logger.warning(f"创建RequestParams失败: {e}")
                log_context.request_params = RequestParams(
                    path_params={},
                    query_params={},
                    body=body
                )

            # 5.异步记录日志（独立try块，不影响主流程）
            log_session: AsyncSession = None
            try:
                log_session = await create_log_session()  # 显式创建日志会话
                log_service = Container.log_service()
                # 日志服务层接收LogContext
                await log_service.record_access_log(log_session, log_context)
                await log_session.commit()  # 3. 手动提交事务
            except Exception as e:
                # 异常时回滚
                if log_session and log_session.is_active:
                    await log_session.rollback()
                logger.error(f"记录访问日志失败: {e}", exc_info=True)
            finally:
                # 最终确保关闭session
                if log_session:
                    try:
                        await log_session.close()
                    except Exception as e:
                        logger.warning(f"关闭session失败: {e}")


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