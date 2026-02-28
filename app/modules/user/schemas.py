from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List


class UserBase(BaseModel):
    username: str
    nickname: Optional[str] = None
    email: Optional[str] = None


class UserCreate(UserBase):
    password: str


# class UserUpdate(BaseModel):
#     nickname: Optional[str] = None
#     email: Optional[str] = None

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True  # 替换原来的orm_mode
        populate_by_name = True

class UserUpdate(BaseSchema):
    """
    更新用户请求模型 - 支持前端格式
    """
    # 用户基本信息
    username: Optional[str] = Field(None, description="用户名", min_length=3, max_length=50, example="zhangsan")
    nickname: Optional[str] = Field(None, description="用户昵称", min_length=2, max_length=50, example="张三")

    # 个人信息
    gender: Optional[int] = Field(None, description="性别(1-男 2-女 0-保密)", ge=0, le=2, example=1)
    mobile: Optional[str] = Field(None, description="手机号", pattern=r"^1[3-9]\d{9}$", example="13888888888")
    email: Optional[str] = Field(None, description="邮箱", example="user@example.com")
    avatar: Optional[str] = Field(None, description="头像URL", example="https://example.com/avatar.jpg")

    # 组织信息
    dept_id: Optional[str] = Field(None, description="部门ID", alias="deptId",
                                   example="22222222-2222-2222-2222-222222222222")
    status: Optional[int] = Field(None, description="状态(1-正常 0-禁用)", ge=0, le=1, example=1)
    version: Optional[int] = Field(None, description="乐观锁版本号", ge=0, le=9999, example=1)

    # 角色信息（前端格式：roleIds）
    role_ids: Optional[List[str]] = Field(None, description="角色ID列表", alias="roleIds")

    model_config = ConfigDict(
        populate_by_name=True,  # 支持别名
        json_schema_extra={
            "example": {
                "nickname": "新昵称",
                "gender": 1,
                "mobile": "13888888888",
                "email": "new@example.com",
                "deptId": "22222222-2222-2222-2222-222222222222",
                "status": 1,
                "roleIds": ["55555555-5555-5555-5555-555555555555"]
            }
        }
    )


class UserResponse(UserBase):
    id: UUID

    class Config:
        from_attributes = True


class UserProfileResponse(BaseModel):
    id: UUID
    username: str
    nickname: Optional[str]
    email: Optional[str]
    roles: list[str] = []