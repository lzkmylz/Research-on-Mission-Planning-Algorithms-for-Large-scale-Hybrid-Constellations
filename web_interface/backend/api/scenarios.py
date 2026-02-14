# -*- coding: utf-8 -*-
"""
场景管理API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from services.scenario_service import scenario_service
from schemas.scenario_schemas import (
    ScenarioCreate, ScenarioUpdate, ScenarioResponse, ScenarioList,
    ScenarioDetailResponse, ScenarioCloneRequest, ScenarioCloneResponse,
    ScenarioBatchAddTargetsRequest, ScenarioBatchRemoveTargetsRequest,
    ScenarioBatchTargetsResponse
)

router = APIRouter()


@router.get("", response_model=ScenarioList)
async def list_scenarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    constellation_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取场景列表"""
    if constellation_id:
        scenarios = await scenario_service.get_scenarios_by_constellation(db, constellation_id)
    else:
        scenarios = await scenario_service.list_scenarios(db, skip=skip, limit=limit)

    return {
        "total": len(scenarios),
        "items": scenarios
    }


@router.post("", response_model=ScenarioResponse)
async def create_scenario(
    scenario: ScenarioCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建场景"""
    db_scenario = await scenario_service.create_scenario(db, scenario)
    return db_scenario


@router.get("/{scenario_id}", response_model=ScenarioDetailResponse)
async def get_scenario(
    scenario_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取场景详情"""
    scenario = await scenario_service.get_scenario_with_constellation(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")

    # 构建详细响应
    target_count = await scenario_service.get_target_count(db, scenario_id)

    return {
        "id": scenario.id,
        "name": scenario.name,
        "constellation_id": scenario.constellation_id,
        "start_time": scenario.start_time,
        "end_time": scenario.end_time,
        "description": scenario.description,
        "configuration_json": scenario.configuration_json,
        "created_at": scenario.created_at,
        "constellation": scenario.constellation if hasattr(scenario, 'constellation') else None,
        "targets": [t.target for t in scenario.targets] if hasattr(scenario, 'targets') else [],
        "target_count": target_count,
        "tasks": [],
        "configuration": scenario.configuration_json
    }


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: str,
    scenario_update: ScenarioUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新场景"""
    db_scenario = await scenario_service.update_scenario(db, scenario_id, scenario_update)
    if not db_scenario:
        raise HTTPException(status_code=404, detail="场景不存在")
    return db_scenario


@router.delete("/{scenario_id}")
async def delete_scenario(
    scenario_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除场景"""
    deleted = await scenario_service.delete_scenario(db, scenario_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="场景不存在")
    return {"message": "场景已删除"}


# ========== 场景复制 ==========

@router.post("/{scenario_id}/clone", response_model=ScenarioCloneResponse)
async def clone_scenario(
    scenario_id: str,
    request: ScenarioCloneRequest,
    db: AsyncSession = Depends(get_db)
):
    """复制场景"""
    original = await scenario_service.get_scenario(db, scenario_id)
    if not original:
        raise HTTPException(status_code=404, detail="原场景不存在")

    new_scenario = await scenario_service.clone_scenario(
        db, scenario_id, request.new_name
    )
    if not new_scenario:
        raise HTTPException(status_code=500, detail="场景复制失败")

    target_count = await scenario_service.get_target_count(db, new_scenario.id)

    return {
        "original_id": scenario_id,
        "new_id": new_scenario.id,
        "new_name": new_scenario.name,
        "target_count": target_count
    }


# ========== 场景目标管理 ==========

@router.post("/{scenario_id}/targets", response_model=ScenarioBatchTargetsResponse)
async def add_targets_to_scenario(
    scenario_id: str,
    request: ScenarioBatchAddTargetsRequest,
    db: AsyncSession = Depends(get_db)
):
    """批量添加目标到场景"""
    scenario = await scenario_service.get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")

    success_count = 0
    errors = []

    for target_id in request.target_ids:
        try:
            await scenario_service.add_target_to_scenario(db, scenario_id, target_id)
            success_count += 1
        except Exception as e:
            errors.append({
                "target_id": target_id,
                "error": str(e)
            })

    return {
        "success_count": success_count,
        "failed_count": len(errors),
        "errors": errors
    }


@router.delete("/{scenario_id}/targets", response_model=ScenarioBatchTargetsResponse)
async def remove_targets_from_scenario(
    scenario_id: str,
    request: ScenarioBatchRemoveTargetsRequest,
    db: AsyncSession = Depends(get_db)
):
    """批量从场景移除目标"""
    scenario = await scenario_service.get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")

    success_count = 0
    errors = []

    for target_id in request.target_ids:
        try:
            result = await scenario_service.remove_target_from_scenario(db, scenario_id, target_id)
            if result:
                success_count += 1
            else:
                errors.append({
                    "target_id": target_id,
                    "error": "目标不在该场景中"
                })
        except Exception as e:
            errors.append({
                "target_id": target_id,
                "error": str(e)
            })

    return {
        "success_count": success_count,
        "failed_count": len(errors),
        "errors": errors
    }


@router.get("/{scenario_id}/targets/count")
async def get_scenario_target_count(
    scenario_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取场景中的目标数量"""
    scenario = await scenario_service.get_scenario(db, scenario_id)
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")

    count = await scenario_service.get_target_count(db, scenario_id)
    return {"scenario_id": scenario_id, "target_count": count}


# ========== 按名称查询 ==========

@router.get("/by-name/{name}", response_model=ScenarioResponse)
async def get_scenario_by_name(
    name: str,
    db: AsyncSession = Depends(get_db)
):
    """根据名称获取场景"""
    scenario = await scenario_service.get_scenario_by_name(db, name)
    if not scenario:
        raise HTTPException(status_code=404, detail="场景不存在")
    return scenario
