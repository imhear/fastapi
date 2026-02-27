# from fastapi import Depends, HTTPException, status
# from fastapi.security import OAuth2PasswordBearer
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.core.database import get_async_db as get_db
# from app.modules.user.repository import UserRepository
# from app.modules.user.models import SysUser
#
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/login/access-token")
#
#
# async def get_current_user(
#     token: str = Depends(oauth2_scheme),
#     db: AsyncSession = Depends(get_db),
# ) -> SysUser:
#     # 这里应该解析 token 获取用户 ID，并查询用户
#     # 为简化，假设 token 就是用户 ID（实际需解码）
#     user_id = token  # 伪代码
#     repo = UserRepository()
#     user = await repo.get_by_id(db, user_id)
#     if not user:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
#     return user