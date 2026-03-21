# app/core/audit/decorator.py
import logging
from functools import wraps
from typing import Callable, Any, Dict, Optional

from fastapi import Request
from app.core.dataclasses import AuditContext

logger = logging.getLogger(__name__)


def audit_log(
    module: str,
    operation_type: str,
    get_business_id: Callable[..., str],
    get_operation_content: Callable[..., Dict[str, Any]],
):
    """
    业务审计日志装饰器
    :param module: 模块名（如 'user'）
    :param operation_type: 操作类型（如 'UPDATE'）
    :param get_business_id: 从 kwargs 中提取业务ID的函数，返回字符串
    :param get_operation_content: 从 kwargs 中提取操作内容的函数，返回字典
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # 1. 提取 request 对象（必须存在）
            request: Request = kwargs.get("request")
            if not request:
                # 如果未找到 request，尝试从位置参数中找（兼容非标准用法）
                for arg in args:
                    if isinstance(arg, Request):
                        request = arg
                        break
            if not request:
                logger.error("audit_log 装饰器找不到 request 对象")
                return await func(*args, **kwargs)

            # 2. 提取业务信息
            try:
                business_id = get_business_id(**kwargs)
            except Exception as e:
                logger.error(f"提取业务ID失败: {e}", exc_info=True)
                business_id = "unknown"

            try:
                operation_content = get_operation_content(**kwargs)
            except Exception as e:
                logger.error(f"生成操作内容失败: {e}", exc_info=True)
                operation_content = {"error": "无法生成操作内容"}

            # 3. 初始化审计上下文（结果未知，先设为 None）
            request.state.audit_context = AuditContext(
                module=module,
                operation_type=operation_type,
                business_id=business_id,
                operation_content=operation_content,
                operation_result=None,   # 稍后设置
                error_msg=None
            )

            # 4. 执行业务逻辑并捕获异常
            try:
                result = await func(*args, **kwargs)
                # 成功：设置结果
                request.state.audit_context.operation_result = "SUCCESS"
                return result
            except Exception as e:
                # 失败：设置结果和错误信息
                request.state.audit_context.operation_result = "FAILURE"
                request.state.audit_context.error_msg = str(e)
                raise   # 重新抛出，保持原有异常处理
        return wrapper
    return decorator