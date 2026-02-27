from app.utils.permission_decorators import permission
from app.utils.permission_checker import permission_checker
from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from typing import List
from app.di.container import Container
from app.modules.role.schemas import RoleCreate, RoleUpdate, RoleResponse
from app.modules.role.service import RoleService
from app.core.exceptions import ResourceNotFound, BadRequest

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/options")
@inject
async def get_role_options(
    role_service: RoleService = Depends(Provide[Container.role_container.role_service]),
):
    return await role_service.get_role_options()


@router.get("/", response_model=List[RoleResponse])
@permission(code="role:read", name="查看角色列表", description="允许查看角色列表")
@inject
async def list_roles(
    role_service: RoleService = Depends(Provide[Container.role_container.role_service]),
    _=Depends(permission_checker("role:read"))
):
    return await role_service.list_roles()


@router.get("/{role_id}", response_model=RoleResponse)
@inject
async def get_role(
    role_id: str,
    role_service: RoleService = Depends(Provide[Container.role_container.role_service]),
):
    try:
        return await role_service.get_role_by_id(role_id)
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/", response_model=RoleResponse)
@inject
async def create_role(
    role_in: RoleCreate,
    role_service: RoleService = Depends(Provide[Container.role_container.role_service]),
):
    try:
        return await role_service.create_role(role_in)
    except BadRequest as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{role_id}", response_model=RoleResponse)
@inject
async def update_role(
    role_id: str,
    role_update: RoleUpdate,
    role_service: RoleService = Depends(Provide[Container.role_container.role_service]),
):
    try:
        return await role_service.update_role(role_id, role_update)
    except (ResourceNotFound, BadRequest) as e:
        raise HTTPException(status_code=404 if isinstance(e, ResourceNotFound) else 400, detail=str(e))


@router.delete("/{role_id}")
@inject
async def delete_role(
    role_id: str,
    role_service: RoleService = Depends(Provide[Container.role_container.role_service]),
):
    try:
        await role_service.delete_role(role_id)
        return {"message": "Role deleted"}
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))