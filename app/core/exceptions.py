from fastapi import HTTPException, status

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