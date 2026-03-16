"""
日志上下文（封装通用参数）
app/core/log/context.py
"""
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
from fastapi import Request
from app.core.dataclasses import UserContext
import urllib.parse  # 新增：解析表单数据
import re  # 新增：正则处理

@dataclass
class RequestParams:
    """请求参数封装（解决参数采集不完整问题）"""
    path_params: Dict[str, Any]  # 路径参数：/reset-password/{id}
    query_params: Dict[str, Any] # 查询参数：?new_password=123
    body: Optional[str] = None   # 请求体（脱敏后）


@dataclass
class LogContext:
    """日志上下文（企业级完整封装）"""
    # 核心标识
    request_id: str
    # 请求基础信息
    request_uri: str
    request_method: str
    ip: Optional[str] = ""  # 改为空字符串而非 None
    user_agent: Optional[str] = ""
    handler: Optional[str] = ""
    # 完整请求参数
    request_params: Optional[RequestParams] = None
    # 响应信息（访问日志专用）
    http_status: Optional[int] = 500  # 改为 500 而非 None
    execution_time: Optional[int] = 0
    # 用户上下文
    user_context: Optional[UserContext] = None

    @classmethod
    async def from_request(cls, request: Request) -> "LogContext":
        """从Request生成完整上下文（异步读取请求体）"""
        # 1. 提取基础信息
        user_context = getattr(request.state, "user_context", None)
        # 2. 提取所有请求参数
        path_params = dict(request.path_params)
        query_params = dict(request.query_params)
        # 3. 读取并脱敏请求体
        body = None
        if hasattr(request, "_body"):
            body_bytes = request._body
        else:
            body_bytes = await request.body()
        if body_bytes:
            # body = cls._desensitize_body(body_bytes)
            body = cls._desensitize_body(body_bytes, request.headers.get("content-type", ""))

        return cls(
            request_id=getattr(request.state, "request_id", ""),
            user_context=user_context,
            request_uri=str(request.url.path),
            request_method=request.method,
            ip=request.client.host if request.client else "",
            user_agent=request.headers.get("user-agent", ""),
            handler=getattr(request.state, "handler", ""),
            request_params=RequestParams(
                path_params=path_params,
                query_params=query_params,
                body=body
            )
        )

    @staticmethod
    def _desensitize_body(body: bytes, content_type: str = "") -> str:
        """
        增强版脱敏逻辑：支持JSON、表单、纯文本格式
        :param body: 原始请求体字节
        :param content_type: 请求Content-Type头
        :return: 脱敏后的字符串
        """
        from app.config.config import settings  # 导入配置

        try:
            # 转换为字符串（处理编码）
            body_str = body.decode("utf-8", errors="ignore")

            # JSON格式处理（优先级最高）
            if "application/json" in content_type:
                import json
                data = json.loads(body_str)
                for field in settings.SENSITIVE_FIELDS:
                    if field in data:
                        data[field] = settings.LOG_SENSITIVE_MASK
                return json.dumps(data)

            # 2. 表单格式处理（application/x-www-form-urlencoded）
            elif "application/x-www-form-urlencoded" in content_type:
                # 解析表单数据
                parsed_data = urllib.parse.parse_qs(body_str)
                # 脱敏敏感字段
                for field in settings.SENSITIVE_FIELDS:
                    if field in parsed_data:
                        parsed_data[field] = [settings.LOG_SENSITIVE_MASK]
                # 重新拼接为表单字符串
                return urllib.parse.urlencode(parsed_data, doseq=True)

            # 3. 纯文本/其他格式：使用正则脱敏
            else:
                # 正则匹配常见的密码模式进行脱敏
                result = body_str
                for field in settings.SENSITIVE_FIELDS:
                    pattern = rf'({field})=[^&]*'
                    replacement = rf'\1={settings.LOG_SENSITIVE_MASK}'
                    result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
                # 限制长度，防止超大请求体
                return result[:settings.LOG_BODY_MAX_LENGTH]

        except Exception as e:
            # 任何异常都返回脱敏后的基础字符串
            import logging
            logging.warning(f"请求体脱敏失败: {e}")
            # 保底脱敏：替换所有密码相关字段
            body_str = body.decode("utf-8", errors="ignore")[:settings.LOG_BODY_MAX_LENGTH]
            return re.sub(r'(password|pwd)=[^&]*', r'\1=***', body_str, flags=re.IGNORECASE)

    # @staticmethod
    # def _desensitize_body(body: bytes) -> str:
    #     """统一脱敏逻辑（复用并优化）"""
    #     try:
    #         import json
    #         data = json.loads(body)
    #         sensitive_fields = ["password", "token", "secret", "mobile", "id_card"]
    #         for field in sensitive_fields:
    #             if field in data:
    #                 data[field] = "***"
    #         return json.dumps(data)
    #     except Exception:
    #         return body.decode("utf-8", errors="ignore")[:1024]  # 限制长度

    def to_dict(self) -> Dict[str, Any]:
        """转为字典，供日志服务层使用"""
        return asdict(self)


# 关键：确保导出 RequestParams 类
__all__ = ["LogContext", "RequestParams", "generate_request_id"]

def generate_request_id() -> str:
    """生成全局唯一request_id"""
    import uuid
    return str(uuid.uuid4())