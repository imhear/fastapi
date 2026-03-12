"""
统一API响应模型
app/core/responses.py
"""
from typing import TypeVar, Generic, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from fastapi import HTTPException, status

T = TypeVar('T')


class ApiResponse(BaseModel, Generic[T]):
    """API统一响应格式"""
    code: str = Field(default="00000", description="响应代码")
    data: Optional[T] = Field(default=None, description="响应数据")
    msg: str = Field(default="操作成功", description="响应消息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间戳")

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d %H:%M:%S')
        }

    @classmethod
    def success(cls, data: T = None, msg: str = "操作成功") -> 'ApiResponse[T]':
        """成功响应快捷方法"""
        return cls(code="00000", data=data, msg=msg)

    @classmethod
    def fail(cls, data: T = None, msg: str = "操作失败") -> 'ApiResponse[T]':
        """失败响应快捷方法"""
        return cls(code="10001", data=data, msg=msg)

    # @classmethod
    # def error(cls, code: str, msg: str, data: Any = None) -> 'ApiResponse':
    #     """错误响应快捷方法"""
    #     return cls(code=code, msg=msg, data=data)


class ErrorResponse(BaseModel):
    """错误响应模型"""
    code: str = Field(..., description="错误代码")
    msg: str = Field(..., description="错误消息")
    details: Optional[Any] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.now)


# 常用响应代码
class ResponseCode:
    SUCCESS = "00000"
    VALIDATION_ERROR = "10001"
    AUTH_ERROR = "20001"
    PERMISSION_DENIED = "20003"
    NOT_FOUND = "30001"
    INTERNAL_ERROR = "50000"

# 分页返回模型
# class PageResponse(BaseModel, Generic[T]):
#     total: int = 0
#     page: int = 1
#     page_size: int = 10
#     list: Optional[list[T]] = []
#
# class ApiPageResponse(ApiResponse[PageResponse[T]], Generic[T]):
#     @classmethod
#     def success(
#         cls,
#         total: int,
#         page: int,
#         page_size: int,
#         list: list[T],
#         msg: str = "操作成功"
#     ):
#         page_data = PageResponse(total=total, page=page, page_size=page_size, list=list)
#         return cls(code="00000", msg=msg, data=page_data)

# 业务异常基类
class BusinessException(HTTPException):
    def __init__(self, code: str, msg: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        super().__init__(status_code=status_code, detail=msg)

# 资源不存在
class ResourceNotFound(BusinessException):
    def __init__(self, msg: str = "资源不存在"):
        super().__init__(code="40400", msg=msg, status_code=status.HTTP_404_NOT_FOUND)

# 参数错误
class BadRequest(BusinessException):
    def __init__(self, msg: str = "参数错误"):
        super().__init__(code="40000", msg=msg)

# 权限不足
class PermissionDenied(BusinessException):
    def __init__(self, msg: str = "权限不足"):
        super().__init__(code="40300", msg=msg, status_code=status.HTTP_403_FORBIDDEN)

# 认证失败
class AuthFailed(BusinessException):
    def __init__(self, msg: str = "认证失败"):
        super().__init__(code="40100", msg=msg, status_code=status.HTTP_401_UNAUTHORIZED)

# 数据已存在
class DataExists(BusinessException):
    def __init__(self, msg: str = "数据已存在"):
        super().__init__(code="40001", msg=msg)