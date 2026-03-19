"""
审计日志通用工具（极简版本）
app/core/audit/utils.py
"""
import json
import logging
from typing import Optional, Dict, Any, TypedDict
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Request
from app.core.auth import CurrentUser
# from app.modules.audit.service import AuditService

logger = logging.getLogger(__name__)

#
# class AuditLogParams(TypedDict, total=False):
#     """审计日志参数字典类型（用于类型提示）"""
#     db: AsyncSession
#     audit_service: AuditService
#     current_user: CurrentUser
#     request: Request
#     module: str
#     operation_type: str
#     business_id: str
#     operation_content: Dict[str, Any]
#     operation_result: str
#     error_msg: Optional[str]
#
#
# def init_audit_log(
#     db: AsyncSession,
#     audit_service: AuditService,
#     current_user: CurrentUser,
#     request: Request,
#     business_id: str,
#     operation: str,
#     module: str = "user",
#     operation_type: str = "UPDATE"
# ) -> AuditLogParams:
#     """
#     初始化审计日志基础参数（极简调用）
#     :param db: 数据库会话
#     :param audit_service: 审计服务
#     :param current_user: 当前用户
#     :param request: 请求对象
#     :param business_id: 业务ID（如用户ID）
#     :param operation: 操作类型（如 reset_password, update_user）
#     :param module: 业务模块，默认 user
#     :param operation_type: 操作分类，默认 UPDATE
#     :return: 包含基础参数的字典，可解包传给 record_audit_log
#     """
#     return {
#         "db": db,
#         "audit_service": audit_service,
#         "current_user": current_user,
#         "request": request,
#         "module": module,
#         "operation_type": operation_type,
#         "business_id": business_id,
#         "operation_content": {
#             "user_id": business_id,
#             "operation": operation
#         }
#     }
#
#
# async def record_audit_log(
#     db: AsyncSession,
#     audit_service: AuditService,
#     current_user: CurrentUser,
#     request: Request,
#     module: str,
#     operation_type: str,
#     business_id: str,
#     operation_content: Dict[str, Any],
#     operation_result: str = "SUCCESS",
#     error_msg: Optional[str] = None
# ) -> None:
#     """
#     极简审计日志记录函数（真正写入）
#     """
#     try:
#         # 空值保护
#         if not audit_service or not current_user:
#             logger.error("审计服务或当前用户为空，跳过审计日志记录")
#             return
#
#         log_context = getattr(request.state, "log_context", None)
#
#         await audit_service.record_audit_log(
#             db=db,
#             operator_id=current_user.id,
#             operator_name=current_user.username,
#             log_context=log_context,
#             module=module,
#             operation_type=operation_type,
#             business_id=business_id,
#             operation_content=json.dumps(operation_content, ensure_ascii=False),
#             operation_result=operation_result,
#             error_msg=error_msg
#         )
#     except Exception as e:
#         logger.error(f"审计日志记录失败: {e}", exc_info=True)


# 通用操作内容生成工具函数
def generate_operation_content(data: Dict[str, Any], ensure_ascii: bool = False, indent: int = None) -> str:
    """
    通用操作内容JSON序列化工具
    :param data: 要序列化的数据
    :param ensure_ascii: 是否确保ASCII（默认False，支持中文）
    :param indent: 缩进（默认None，紧凑格式）
    :return: 序列化后的字符串
    """
    try:
        return json.dumps(data, ensure_ascii=ensure_ascii, indent=indent, default=str)
    except Exception as e:
        logger.warning(f"操作内容序列化失败: {e}")
        return str(data)
