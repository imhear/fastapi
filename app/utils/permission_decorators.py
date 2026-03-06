from functools import wraps
from typing import Callable, Optional, Dict, Any, List

# 全局权限注册表
_permission_registry: Dict[str, Dict] = {}


def permission(code: str, name: str, description: Optional[str] = None, category: str = "api"):
    """
    权限声明装饰器，仅添加元数据，不包装函数
    """
    def decorator(func: Callable) -> Callable:
        if not hasattr(func, '__api_permissions__'):
            func.__api_permissions__ = []
        perm_data = {
            'code': code,
            'name': name,
            'description': description,
            'category': category,
            'endpoint': f"{func.__module__}.{func.__qualname__}"
        }
        func.__api_permissions__.append(perm_data)
        _permission_registry[code] = perm_data
        return func
    return decorator


def get_permission_registry() -> Dict[str, Dict]:
    return _permission_registry.copy()


def get_endpoint_permissions(func: Callable) -> List[Dict]:
    return getattr(func, '__api_permissions__', [])