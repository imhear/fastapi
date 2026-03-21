"""
日志模块服务层
app/core/log/service.py
"""
import asyncio
import json
import logging
import uuid
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dataclasses import AuditContext
from app.core.log.context import LogContext

from app.modules.audit.models import SysAccessLog, SysErrorLog, BizAuditLog

# 配置日志
# logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


# 新增：敏感字段脱敏工具函数（企业级必备）
def _desensitize_sensitive_data(data: str) -> str:
    """脱敏敏感字段（密码、token、手机号等）"""
    if not isinstance(data, str):
        return data
    import re
    # 手机号脱敏
    data = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', data)
    # 密码/token脱敏
    data = re.sub(r'(password|token|secret|key)=[^\s&;]+', r'\1=***', data)
    # 身份证脱敏
    data = re.sub(r'(\d{6})\d{8}(\d{4})', r'\1********\2', data)
    return data


class LogService:
    """统一日志服务（无状态设计）（使用延迟导入）"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def record_access_log(self, session: AsyncSession, log_context: LogContext) -> None:
        """异步记录系统访问日志"""
        # 运行时导入，避免循环依赖
        # from app.modules.audit.models import SysAccessLog

        try:
            common_fields = self._extract_common_fields(log_context)
            query_json, body_str = self._extract_request_params(log_context)

            # 从log_dict中获取http_status/execution_time（兼容非直接属性场景）
            log_dict = self._safe_serialize(log_context)
            http_status = log_dict.get("http_status", 500)
            execution_time = log_dict.get("execution_time", 0)

            log = SysAccessLog(
                **common_fields,
                request_params=query_json,
                request_body=body_str,
                http_status=http_status,
                execution_time=execution_time,
            )
            session.add(log)
            # """接收LogContext，统一转换为数据库模型"""
            # # 安全解析上下文
            # log_dict = self._safe_serialize(log_context)
            #
            # # 关键修复：更健壮的 operator_id 提取逻辑
            # operator_id = None
            # operator_name = None
            # user_context = log_dict.get("user_context")
            # if user_context and isinstance(user_context, dict):
            #     operator_id = user_context.get("id")
            #     operator_name = user_context.get("username")
            # # # 兼容旧格式
            # # elif user_context and hasattr(user_context, "id"):
            # #     operator_id = user_context.id
            #
            #
            # # 关键修复：None 安全检查
            # request_params = log_dict.get("request_params", {})
            # query_params = request_params.get("query_params", {}) if isinstance(request_params, dict) else {}
            # body = request_params.get("body", "") if isinstance(request_params, dict) else ""
            #
            # log = SysAccessLog(
            #     request_id=log_dict.get("request_id", ""),
            #     request_uri=log_dict.get("request_uri", ""),
            #     request_method=log_dict.get("request_method", ""),
            #     # request_params=json.dumps(query_params),
            #     # 核心修改：ensure_ascii=False 保留中文，indent可选（美化格式）
            #     request_params=json.dumps(query_params, ensure_ascii=False),
            #     request_body=body,
            #     http_status=log_dict.get("http_status", 500),
            #     execution_time=log_dict.get("execution_time", 0),
            #     ip=log_dict.get("ip", ""),
            #     user_agent=log_dict.get("user_agent", ""),
            #     operator_id=operator_id,  # 使用提取的 operator_id
            #     operator_name=operator_name,
            #     handler=log_dict.get("handler", "")
            # )
            # session.add(log)
        except Exception as e:
            logger.error(f"记录访问日志失败: {e}", exc_info=True)
            raise


    async def record_error_log(
        self,
        session: AsyncSession,
        log_context: LogContext,
        error_code: str,
        error_msg: str,
        error_stack: str,
    ) -> None:
        """异步记录错误日志"""
        # 运行时导入
        # from app.modules.audit.models import SysErrorLog

        try:
            common_fields = self._extract_common_fields(log_context)
            query_json, body_str = self._extract_request_params(log_context)

            # 错误信息脱敏（企业级合规）
            error_msg = _desensitize_sensitive_data(error_msg)
            error_stack = _desensitize_sensitive_data(error_stack)

            log = SysErrorLog(
                **common_fields,
                request_params=query_json,
                request_body=body_str,
                error_code=error_code,
                error_msg=error_msg,
                error_stack=error_stack,
            )
            # 保留脱敏逻辑
            if hasattr(log, 'set_error_stack'):
                log.set_error_stack(error_stack)
            session.add(log)
            # """错误日志复用同一上下文"""
            # log_dict = self._safe_serialize(log_context)
            #
            # # 关键修复：更健壮的 operator_id 提取逻辑
            # operator_id = None
            # operator_name = None
            # user_context = log_dict.get("user_context")
            # if user_context and isinstance(user_context, dict):
            #     operator_id = user_context.get("id")
            #     operator_name = user_context.get("username")
            # # elif user_context and hasattr(user_context, "id"):
            # #     operator_id = user_context.id
            #
            #
            # # 关键修复：None 安全检查
            # request_params = log_dict.get("request_params", {})
            # query_params = request_params.get("query_params", {}) if isinstance(request_params, dict) else {}
            # body = request_params.get("body", "") if isinstance(request_params, dict) else ""
            #
            # log = SysErrorLog(
            #     request_id=log_dict.get("request_id", ""),
            #     request_uri=log_dict.get("request_uri", ""),
            #     request_method=log_dict.get("request_method", ""),
            #     # 核心修改：ensure_ascii=False 保留中文，indent可选（美化格式）
            #     request_params=json.dumps(query_params, ensure_ascii=False),
            #     request_body=body,
            #     ip=log_dict.get("ip", ""),
            #     user_agent=log_dict.get("user_agent", ""),
            #     operator_id=operator_id,  # 使用提取的 operator_id
            #     operator_name=operator_name,
            #     handler=log_dict.get("handler", ""),
            #     error_code=error_code,
            #     error_msg=error_msg,
            #     error_stack=error_stack
            # )
            # # 脱敏处理
            # if hasattr(log, 'set_error_stack'):
            #     log.set_error_stack(error_stack)
            # session.add(log)
        except Exception as e:
            logger.error(f"记录错误日志失败: {e}", exc_info=True)
            raise


    """业务审计服务（与业务同事务）"""
    async def record_audit_log(
        self,
        db: AsyncSession,
        # operator_id: int,
        # operator_name: str,
        log_context: LogContext,  # 复用上下文
        audit_context: AuditContext,
        # module: str,
        # operation_type: str,
        # business_id: str,
        # operation_content: str,
        # operation_result: str = "SUCCESS",
        # error_msg: Optional[str] = None,
    ) -> None:
        """记录业务审计日志（独立会话，手动提交）"""
        # 运行时导入
        # from app.modules import BizAuditLog

        try:
            common_fields = self._extract_common_fields(log_context)

            # 操作内容序列化+脱敏（企业级合规）
            operation_content = audit_context.operation_content or {}
            operation_content_str = json.dumps(
                operation_content,
                ensure_ascii=False,
                default=str  # 兼容非序列化类型
            )
            operation_content_str = _desensitize_sensitive_data(operation_content_str)

            log = BizAuditLog(
                **common_fields,
                module=audit_context.module or "",
                operation_type=audit_context.operation_type or "",
                business_id=audit_context.business_id or "",
                operation_content=operation_content_str,
                operation_result=audit_context.operation_result or "FAILURE",
                error_msg=_desensitize_sensitive_data(audit_context.error_msg),
            )
            db.add(log)
            # """错误日志复用同一上下文"""
            # """接收LogContext，统一转换为数据库模型"""
            # # 安全解析上下文
            # log_dict = self._safe_serialize(log_context)
            # ip = log_dict.get("ip", "")
            # request_id = log_dict.get("request_id", "")
            # user_agent = log_dict.get("user_agent", "")
            # # 将 operation_content 字典转换为 JSON 字符串
            # operation_content_str = json.dumps(audit_context.operation_content, ensure_ascii=False)
            #
            # # 关键修复：更健壮的 operator_id 提取逻辑
            # operator_id = None
            # operator_name = None
            # user_context = log_dict.get("user_context")
            # if user_context and isinstance(user_context, dict):
            #     operator_id = user_context.get("id")
            #     operator_name = user_context.get("username")
            #
            # log = BizAuditLog(
            #     operator_id=operator_id,
            #     operator_name=operator_name,
            #     module=audit_context.module,
            #     operation_type=audit_context.operation_type,
            #     business_id=audit_context.business_id,
            #     operation_content=operation_content_str,
            #     operation_result=audit_context.operation_result,
            #     error_msg=audit_context.error_msg,
            #     ip=ip,
            #     request_id=request_id,
            #     user_agent=user_agent,
            #     request_uri=log_dict.get("request_uri", ""),
            #     request_method=log_dict.get("request_method", ""),
            #     handler=log_dict.get("handler", "")
            # )
            # db.add(log)
            # # 移除：不再依赖业务事务提交，由中间件手动commit
        except Exception as e:
            # 仅记录错误，不抛异常
            logger.error(f"业务审计日志记录失败: {e}", exc_info=True)
            raise  # 抛出异常，让中间件处理回滚

    # 优化1：增强通用字段提取（增加None处理+默认值+脱敏）
    def _extract_common_fields(self, log_context: Optional[LogContext]) -> Dict[str, Any]:
        """
        从 LogContext 提取通用字段（企业级健壮版）
        :param log_context: 日志上下文对象（允许为None）
        :return: 通用字段字典
        """
        # 极端场景处理：log_context为None时返回默认值
        if log_context is None:
            default_request_id = str(uuid.uuid4())
            return {
                "request_id": default_request_id,
                "request_uri": "",
                "request_method": "",
                "handler": "",
                "ip": "",
                "user_agent": "",
                "operator_id": None,
                "operator_name": "",
            }

        log_dict = self._safe_serialize(log_context)

        # 提取用户信息（增加多层兼容）
        operator_id = None
        operator_name = ""
        user_context = log_dict.get("user_context", {})
        if isinstance(user_context, dict):
            operator_id = user_context.get("id")
            operator_name = user_context.get("username", "")
        # 兼容对象类型的user_context（企业级多场景适配）
        elif hasattr(user_context, "id"):
            operator_id = getattr(user_context, "id", None)
            operator_name = getattr(user_context, "username", "")

        # 统一默认值管理（企业级规范）
        return {
            "request_id": log_dict.get("request_id", str(uuid.uuid4())),  # 空值填充默认UUID
            "request_uri": _desensitize_sensitive_data(log_dict.get("request_uri", "")),
            "request_method": log_dict.get("request_method", "").upper(),  # 统一大写（GET/POST）
            "handler": log_dict.get("handler", ""),
            "ip": log_dict.get("ip", ""),
            "user_agent": _desensitize_sensitive_data(log_dict.get("user_agent", "")),
            "operator_id": operator_id,
            "operator_name": _desensitize_sensitive_data(operator_name),
        }

    # 优化2：增强请求参数提取（增加脱敏+None处理）
    def _extract_request_params(self, log_context: Optional[LogContext]) -> Tuple[str, str]:
        """
        提取并序列化请求参数（企业级健壮版）
        :param log_context: 日志上下文对象
        :return: (序列化的query参数, 脱敏后的body)
        """
        log_dict = self._safe_serialize(log_context)
        request_params = log_dict.get("request_params", {})

        # 多层None安全检查
        query_params = request_params.get("query_params", {}) if isinstance(request_params, dict) else {}
        body = request_params.get("body", "") if isinstance(request_params, dict) else ""

        # 序列化+脱敏（企业级合规要求）
        query_json = json.dumps(query_params, ensure_ascii=False, default=str)
        body_str = _desensitize_sensitive_data(body)

        return query_json, body_str

    @staticmethod
    def _safe_serialize(obj) -> Dict[str, Any]:
        """安全序列化对象"""
        if obj is None:
            return {}
        # 处理 dataclass 对象
        if hasattr(obj, '__dict__'):
            result = obj.__dict__.copy()
            # 递归序列化嵌套对象
            for key, value in result.items():
                if hasattr(value, '__dict__'):
                    result[key] = value.__dict__.copy()
                elif isinstance(value, (list, tuple)):
                    result[key] = [v.__dict__ if hasattr(v, '__dict__') else v for v in value]
            return result
        # 处理字典
        elif isinstance(obj, dict):
            return obj.copy()
        # 处理其他类型（返回空字典）
        return {}


    # @staticmethod
    # def generate_request_id() -> str:
    #     """生成request_id（工具方法，无状态）"""
    #     return str(uuid.uuid4())