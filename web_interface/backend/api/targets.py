# -*- coding: utf-8 -*-
"""
目标管理API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from services.target_service import target_service
from schemas.target_schemas import (
    TargetCreate, TargetUpdate, TargetResponse, TargetList,
    TargetBatchImportRequest, TargetBatchImportResponse,
    PointTargetCreate, AreaTargetCreate, MovingTargetCreate, GridTargetCreate
)
from database.models import TargetTypeEnum

router = APIRouter()


@router.get("", response_model=TargetList)
async def list_targets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    target_type: Optional[TargetTypeEnum] = None,
    min_priority: Optional[int] = Query(None, ge=1, le=10),
    max_priority: Optional[int] = Query(None, ge=1, le=10),
    db: AsyncSession = Depends(get_db)
):
    """获取目标列表"""
    if target_type:
        targets = await target_service.get_targets_by_type(db, target_type.value)
    elif min_priority is not None and max_priority is not None:
        targets = await target_service.get_targets_by_priority(db, min_priority, max_priority)
    else:
        targets = await target_service.list_targets(db, skip=skip, limit=limit)

    return {
        "total": len(targets),
        "items": targets
    }


@router.post("", response_model=TargetResponse)
async def create_target(
    target: TargetCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建目标"""
    db_target = await target_service.create_target(db, target)
    return db_target


@router.post("/batch", response_model=TargetBatchImportResponse)
async def batch_create_targets(
    request: TargetBatchImportRequest,
    db: AsyncSession = Depends(get_db)
):
    """批量创建目标"""
    result = await target_service.create_targets_batch(db, request.targets)
    return result


@router.get("/{target_id}", response_model=TargetResponse)
async def get_target(
    target_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取目标详情"""
    target = await target_service.get_target(db, target_id)
    if not target:
        raise HTTPException(status_code=404, detail="目标不存在")
    return target


@router.put("/{target_id}", response_model=TargetResponse)
async def update_target(
    target_id: str,
    target_update: TargetUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新目标"""
    db_target = await target_service.update_target(db, target_id, target_update)
    if not db_target:
        raise HTTPException(status_code=404, detail="目标不存在")
    return db_target


@router.delete("/{target_id}")
async def delete_target(
    target_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除目标"""
    deleted = await target_service.delete_target(db, target_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="目标不存在")
    return {"message": "目标已删除"}


# ========== 特定类型目标创建端点 ==========

@router.post("/point", response_model=TargetResponse)
async def create_point_target(
    target: PointTargetCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建点目标"""
    target_data = TargetCreate(
        name=target.name,
        target_type=TargetTypeEnum.POINT,
        latitude=target.latitude,
        longitude=target.longitude,
        priority=target.priority,
        required_resolution_m=target.required_resolution_m,
        properties_json=target.properties_json
    )
    db_target = await target_service.create_target(db, target_data)
    return db_target


@router.post("/area", response_model=TargetResponse)
async def create_area_target(
    target: AreaTargetCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建区域目标"""
    import json
    polygon_json = {
        "type": "Polygon",
        "coordinates": [target.polygon],
        "decomposition_strategy": target.decomposition_strategy
    }
    target_data = TargetCreate(
        name=target.name,
        target_type=TargetTypeEnum.AREA,
        priority=target.priority,
        required_resolution_m=target.required_resolution_m,
        polygon_json=polygon_json
    )
    db_target = await target_service.create_target(db, target_data)
    return db_target


@router.post("/moving", response_model=TargetResponse)
async def create_moving_target(
    target: MovingTargetCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建动态目标"""
    import json
    target_data = TargetCreate(
        name=target.name,
        target_type=TargetTypeEnum.MOVING,
        priority=target.priority,
        required_resolution_m=target.required_resolution_m,
        path_json=target.path,
        properties_json={
            "target_subtype": target.target_subtype,
            "speed_kmh": target.speed_kmh
        }
    )
    db_target = await target_service.create_target(db, target_data)
    return db_target


@router.post("/grid", response_model=TargetResponse)
async def create_grid_target(
    target: GridTargetCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建网格目标"""
    target_data = TargetCreate(
        name=target.name,
        target_type=TargetTypeEnum.GRID,
        latitude=target.center_latitude,
        longitude=target.center_longitude,
        priority=target.priority,
        required_resolution_m=target.required_resolution_m,
        properties_json={
            "size_deg": target.size_deg,
            "grid_divisions": target.grid_divisions,
            "center_latitude": target.center_latitude,
            "center_longitude": target.center_longitude
        }
    )
    db_target = await target_service.create_target(db, target_data)
    return db_target


# ========== 地理位置查询端点 ==========

@router.get("/by-location", response_model=TargetList)
async def get_targets_by_location(
    min_lat: float = Query(..., ge=-90, le=90),
    max_lat: float = Query(..., ge=-90, le=90),
    min_lon: float = Query(..., ge=-180, le=180),
    max_lon: float = Query(..., ge=-180, le=180),
    db: AsyncSession = Depends(get_db)
):
    """根据地理位置范围获取目标"""
    targets = await target_service.get_targets_by_location(
        db, min_lat, max_lat, min_lon, max_lon
    )
    return {
        "total": len(targets),
        "items": targets
    }


# ========== 场景关联端点 ==========

@router.get("/by-scenario/{scenario_id}", response_model=TargetList)
async def get_targets_by_scenario(
    scenario_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取场景中的所有目标"""
    targets = await target_service.get_targets_by_scenario(db, scenario_id)
    return {
        "total": len(targets),
        "items": targets
    }


@router.post("/{target_id}/scenarios/{scenario_id}")
async def add_target_to_scenario(
    target_id: str,
    scenario_id: str,
    db: AsyncSession = Depends(get_db)
):
    """将目标添加到场景"""
    result = await target_service.add_target_to_scenario(db, scenario_id, target_id)
    if not result:
        raise HTTPException(status_code=400, detail="添加失败，目标或场景可能不存在")
    return {"message": "目标已添加到场景"}


@router.delete("/{target_id}/scenarios/{scenario_id}")
async def remove_target_from_scenario(
    target_id: str,
    scenario_id: str,
    db: AsyncSession = Depends(get_db)
):
    """从场景中移除目标"""
    result = await target_service.remove_target_from_scenario(db, scenario_id, target_id)
    if not result:
        raise HTTPException(status_code=404, detail="目标不在该场景中")
    return {"message": "目标已从场景移除"}
