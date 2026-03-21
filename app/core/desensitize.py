# app/core/security/desensitize.py
import json
import re
import urllib.parse
import logging
from typing import Any, Union, Optional
from app.config.config import settings

logger = logging.getLogger(__name__)

# 预编译正则表达式（性能优化）
_MOBILE_PATTERN = re.compile(r'(\d{3})\d{4}(\d{4})')
_IDCARD_PATTERN = re.compile(r'(\d{6})\d{8}(\d{4})')
# 敏感字段正则（动态构建）
_SENSITIVE_PATTERNS = {}

def _get_sensitive_pattern(field: str) -> re.Pattern:
    """获取或编译敏感字段的正则表达式"""
    if field not in _SENSITIVE_PATTERNS:
        pattern = rf'({field})=[^&]*'
        _SENSITIVE_PATTERNS[field] = re.compile(pattern, re.IGNORECASE)
    return _SENSITIVE_PATTERNS[field]

def desensitize_by_field(field: str, value: Any, scene: str = "storage") -> str:
    """
    根据字段名脱敏单个值
    :param field: 字段名
    :param value: 原始值
    :param scene: 场景（storage/display/log）
    :return: 脱敏后的字符串
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        value = str(value)

    # 场景化特殊处理（展示场景保留更多信息）
    if scene == "display":
        if field == "mobile" and len(value) >= 11:
            return value[:6] + "****" + value[-2:]
        elif field == "email" and "@" in value:
            return value[:3] + "***" + value[value.find('@'):]

    # 使用配置的规则
    rule = settings.SENSITIVE_FIELD_RULES.get(field)
    if rule:
        try:
            return rule(value)
        except Exception as e:
            logger.warning(f"字段 {field} 脱敏失败: {e}")
            return settings.LOG_SENSITIVE_MASK

    # 如果在敏感字段列表中，直接返回掩码
    if field in settings.SENSITIVE_FIELDS:
        return settings.LOG_SENSITIVE_MASK

    return value

def desensitize_body(data: Union[str, bytes], content_type: str = "", scene: str = "storage") -> str:
    """
    脱敏请求体（支持JSON、表单、纯文本）
    :param data: 原始数据（字符串或字节）
    :param content_type: Content-Type
    :param scene: 场景
    :return: 脱敏后的字符串
    """
    if not data:
        return ""

    # 转为字符串
    if isinstance(data, bytes):
        body_str = data.decode("utf-8", errors="ignore")
    else:
        body_str = str(data)

    try:
        # JSON格式
        if "application/json" in content_type:
            json_data = json.loads(body_str)
            for field in settings.SENSITIVE_FIELDS:
                if field in json_data:
                    json_data[field] = desensitize_by_field(field, json_data[field], scene)
            return json.dumps(json_data, ensure_ascii=False)

        # 表单格式
        elif "application/x-www-form-urlencoded" in content_type:
            body_str_decoded = urllib.parse.unquote(body_str)
            parsed = urllib.parse.parse_qs(body_str_decoded)
            for field in settings.SENSITIVE_FIELDS:
                if field in parsed:
                    parsed[field] = [desensitize_by_field(field, v, scene) for v in parsed[field]]
            # 重新拼接
            parts = []
            for key, values in parsed.items():
                for val in values:
                    parts.append(f"{key}={val}")
            return "&".join(parts)

        # 其他格式：使用正则脱敏
        else:
            result = body_str
            for field in settings.SENSITIVE_FIELDS:
                pattern = _get_sensitive_pattern(field)
                result = pattern.sub(rf'\1={settings.LOG_SENSITIVE_MASK}', result)
            # 手机号/身份证额外脱敏
            result = _MOBILE_PATTERN.sub(r'\1****\2', result)
            result = _IDCARD_PATTERN.sub(r'\1********\2', result)
            return result[:settings.LOG_BODY_MAX_LENGTH]

    except Exception as e:
        logger.warning(f"请求体脱敏失败: {e}")
        # 保底脱敏
        result = body_str[:settings.LOG_BODY_MAX_LENGTH]
        return re.sub(r'(password|pwd|new_password|token|secret)=[^&]*', r'\1=***', result, flags=re.IGNORECASE)

def desensitize_text(text: str, scene: str = "storage") -> str:
    """
    脱敏通用文本（URI、User-Agent、错误信息等）
    :param text: 原始文本
    :param scene: 场景
    :return: 脱敏后的字符串
    """
    if not isinstance(text, str):
        return str(text)

    result = text
    for field in settings.SENSITIVE_FIELDS:
        pattern = _get_sensitive_pattern(field)
        result = pattern.sub(rf'\1={settings.LOG_SENSITIVE_MASK}', result)
    # 手机号/身份证脱敏
    result = _MOBILE_PATTERN.sub(r'\1****\2', result)
    result = _IDCARD_PATTERN.sub(r'\1********\2', result)
    return result

# # 兼容旧函数名（可选）
# def _simple_desensitize(text: str) -> str:
#     return desensitize_text(text)