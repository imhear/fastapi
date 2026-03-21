"""
日志模块服务层
app/core/log/service.py
"""
import asyncio
import json
import re
import logging
import urllib
import uuid
from typing import Dict, Any, Tuple, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dataclasses import AuditContext
from app.core.log.context import LogContext
from app.config.config import settings

from app.modules.audit.models import SysAccessLog, SysErrorLog, BizAuditLog

# 配置日志
# logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


class LogService:
    """统一日志服务（无状态设计）（使用延迟导入）"""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def record_access_log(self, session: AsyncSession, log_context: LogContext) -> None:
        """异步记录系统访问日志"""
        try:
            common_fields = self._extract_common_fields(log_context)
            query_json, body_str = self._extract_request_params(log_context)

            # 从log_context直接获取，不再依赖序列化字典
            http_status = log_context.http_status or 500
            execution_time = log_context.execution_time or 0

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
        try:
            common_fields = self._extract_common_fields(log_context)
            query_json, body_str = self._extract_request_params(log_context)

            # 错误信息脱敏（企业级合规）使用简单脱敏函数处理错误信息
            error_msg = _simple_desensitize(error_msg)
            error_stack = _simple_desensitize(error_stack)

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
        except Exception as e:
            logger.error(f"记录错误日志失败: {e}", exc_info=True)
            raise


    """业务审计服务（与业务同事务）"""
    async def record_audit_log(
        self,
        db: AsyncSession,
        log_context: LogContext,  # 复用上下文
        audit_context: AuditContext,
    ) -> None:
        """记录业务审计日志（独立会话，手动提交）"""
        try:
            common_fields = self._extract_common_fields(log_context)

            # 操作内容序列化+脱敏（企业级合规）
            operation_content = audit_context.operation_content or {}
            operation_content_str = json.dumps(
                operation_content,
                ensure_ascii=False,
                default=str  # 兼容非序列化类型
            )
            operation_content_str = _simple_desensitize(operation_content_str)

            log = BizAuditLog(
                **common_fields,
                module=audit_context.module or "",
                operation_type=audit_context.operation_type or "",
                business_id=audit_context.business_id or "",
                operation_content=operation_content_str,
                operation_result=audit_context.operation_result or "FAILURE",
                error_msg=_simple_desensitize(audit_context.error_msg),
            )
            db.add(log)
        except Exception as e:
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
            "request_uri": _simple_desensitize(log_dict.get("request_uri", "")),
            "request_method": log_dict.get("request_method", "").upper(),  # 统一大写（GET/POST）
            "handler": log_dict.get("handler", ""),
            "ip": log_dict.get("ip", ""),
            "user_agent": _simple_desensitize(log_dict.get("user_agent", "")),
            "operator_id": operator_id,
            "operator_name": _simple_desensitize(operator_name),
        }

    # 优化2：增强请求参数提取（增加脱敏+None处理）
    def _extract_request_params(self, log_context: Optional[LogContext]) -> Tuple[str, str]:
        """
        提取并序列化请求参数（企业级健壮版）
        :param log_context: 日志上下文对象
        :return: (序列化的query参数, 脱敏后的body)
        """
        if not log_context or not log_context.request_params:
            return "{}", ""

        # 直接从log_context获取原始数据（避免序列化问题）
        query_params = log_context.request_params.query_params or {}
        raw_body = log_context.request_params.body or ""
        content_type = log_context.content_type or ""  # 获取content_type

        # 序列化query参数（无脱敏，仅格式化）
        query_json = json.dumps(query_params, ensure_ascii=False, default=str)
        # 核心修复：传递content_type给脱敏函数
        body_str = _desensitize_sensitive_data(raw_body, content_type)

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

def _desensitize_value(field: str, value: Any) -> Any:
    """完全对齐老版本：根据字段名对单个值进行脱敏"""
    # 如果值不是字符串，先转换为字符串（例如数字手机号）
    if not isinstance(value, str):
        value = str(value)

    # 获取该字段的脱敏规则
    rule = settings.SENSITIVE_FIELD_RULES.get(field)
    if rule:
        try:
            return rule(value)
        except Exception as e:
            logging.warning(f"字段 {field} 脱敏失败: {e}")
            return settings.LOG_SENSITIVE_MASK
    else:
        # 无特定规则，使用默认掩码
        return settings.LOG_SENSITIVE_MASK

# 核心修改：增强版脱敏函数（统一所有脱敏逻辑）
def _desensitize_sensitive_data(data: str, content_type: str = "") -> str:
    """
    统一脱敏函数：支持JSON、表单、纯文本格式
    :param data: 原始数据字符串
    :param content_type: 请求Content-Type
    :return: 脱敏后的字符串
    """
    # 1. 确保输入为字符串
    if isinstance(data, bytes):
        body_str = data.decode("utf-8", errors="ignore")
    elif isinstance(data, str):
        body_str = data
    else:
        # 其他类型转为字符串
        body_str = str(data)

    if not body_str:
        return ""

    try:
        # JSON格式处理
        if "application/json" in content_type:
            json_data = json.loads(body_str)
            for field in settings.SENSITIVE_FIELDS:
                if field in json_data:
                    json_data[field] = _desensitize_value(field, json_data[field])
            return json.dumps(json_data, ensure_ascii=False)

        # 表单格式处理
        elif "application/x-www-form-urlencoded" in content_type:
            # 解析表单数据（先解码URL编码）
            # 表单提交的application/x-www-form-urlencoded格式会自动将中文转为URL编码（百分号形式），但日志中必须还原为原生中文（否则可读性为0）。
            body_str_decoded = urllib.parse.unquote(body_str)  # URL解码
            parsed_data = urllib.parse.parse_qs(body_str_decoded)
            # 脱敏敏感字段
            for field in settings.SENSITIVE_FIELDS:
                if field in parsed_data:
                    parsed_data[field] = [
                        _desensitize_value(field, v) for v in parsed_data[field]
                    ]
            # 重新拼接时无需URL编码（日志存储原生字符串）
            # 手动拼接为 key=value&key=value 格式，避免自动URL编码
            body_parts = []
            for key, values in parsed_data.items():
                for val in values:
                    body_parts.append(f"{key}={val}")
            return "&".join(body_parts)

        # 通用正则脱敏（其他格式）
        else:
            result = body_str
            for field in settings.SENSITIVE_FIELDS:
                pattern = rf'({field})=[^&]*'
                replacement = rf'\1={settings.LOG_SENSITIVE_MASK}'
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            # 限制长度，防止超大请求体
            return result[:settings.LOG_BODY_MAX_LENGTH]

    except Exception as e:
        logger.warning(f"数据脱敏失败: {e}")
        # 保底脱敏
        result = data[:settings.LOG_BODY_MAX_LENGTH]
        return re.sub(r'(password|pwd|new_password|token|secret)=[^&]*', r'\1=***', result, flags=re.IGNORECASE)

def _simple_desensitize(data: str) -> str:
    """简单脱敏函数（用于URI、UA等）"""
    if not isinstance(data, str):
        return data
    # 手机号脱敏
    data = re.sub(r'(\d{3})\d{4}(\d{4})', r'\1****\2', data)
    # 密码/token脱敏
    data = re.sub(r'(password|token|secret|key)=[^\s&;]+', r'\1=***', data)
    # 身份证脱敏
    data = re.sub(r'(\d{6})\d{8}(\d{4})', r'\1********\2', data)
    return data