from abc import ABC, abstractmethod
from typing import Set

class AbstractPermissionService(ABC):
    @abstractmethod
    async def get_user_permissions(self, user_id: str) -> Set[str]:
        """获取用户拥有的所有权限代码"""
        pass

    @abstractmethod
    async def check_user_permission(self, user_id: str, required_perm: str) -> bool:
        """检查用户是否拥有指定权限（支持通配符）"""
        pass