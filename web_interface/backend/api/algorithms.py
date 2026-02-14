# -*- coding: utf-8 -*-
"""
算法配置API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from services.algorithm_service import algorithm_service
from schemas.algorithm_schemas import (
    AlgorithmConfigCreate, AlgorithmConfigUpdate, AlgorithmConfigResponse,
    AlgorithmConfigList, GAConfigCreate, TabuConfigCreate, SAConfigCreate,
    ACOConfigCreate, AlgorithmComparisonRequest, AlgorithmComparisonResponse
)
from database.models import AlgorithmTypeEnum

router = APIRouter()


@router.get("", response_model=AlgorithmConfigList)
async def list_algorithm_configs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    algorithm_type: Optional[AlgorithmTypeEnum] = None,
    is_preset: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取算法配置列表"""
    if algorithm_type or is_preset is not None:
        configs = await algorithm_service.search_configs(
            db,
            algorithm_type=algorithm_type.value if algorithm_type else None,
            is_preset=is_preset,
            skip=skip,
            limit=limit
        )
    else:
        configs = await algorithm_service.list_configs(db, skip=skip, limit=limit)

    return {
        "total": len(configs),
        "items": configs
    }


@router.post("", response_model=AlgorithmConfigResponse)
async def create_algorithm_config(
    config: AlgorithmConfigCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建算法配置"""
    db_config = await algorithm_service.create_config(db, config)
    return db_config


@router.get("/{config_id}", response_model=AlgorithmConfigResponse)
async def get_algorithm_config(
    config_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取算法配置详情"""
    config = await algorithm_service.get_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="算法配置不存在")
    return config


@router.put("/{config_id}", response_model=AlgorithmConfigResponse)
async def update_algorithm_config(
    config_id: str,
    config_update: AlgorithmConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新算法配置"""
    db_config = await algorithm_service.update_config(db, config_id, config_update)
    if not db_config:
        raise HTTPException(status_code=404, detail="算法配置不存在")
    return db_config


@router.delete("/{config_id}")
async def delete_algorithm_config(
    config_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除算法配置"""
    config = await algorithm_service.get_config(db, config_id)
    if not config:
        raise HTTPException(status_code=404, detail="算法配置不存在")

    # 不允许删除预设配置
    if config.is_preset:
        raise HTTPException(status_code=403, detail="不能删除预设配置")

    deleted = await algorithm_service.delete_config(db, config_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="删除失败")

    return {"message": "算法配置已删除"}


# ========== 预设配置管理 ==========

@router.get("/presets", response_model=AlgorithmConfigList)
async def list_preset_configs(
    db: AsyncSession = Depends(get_db)
):
    """获取所有预设配置"""
    presets = await algorithm_service.list_presets(db)
    return {
        "total": len(presets),
        "items": presets
    }


@router.post("/presets/init")
async def initialize_preset_configs(
    db: AsyncSession = Depends(get_db)
):
    """初始化默认预设配置"""
    default_presets = await algorithm_service.get_default_presets()
    created_count = 0
    errors = []

    for preset in default_presets:
        try:
            # 检查是否已存在
            existing = await algorithm_service.get_config_by_name(db, preset["name"])
            if not existing:
                await algorithm_service.create_preset(
                    db,
                    name=preset["name"],
                    algorithm_type=preset["algorithm_type"],
                    config=preset["config"],
                    description=preset["description"]
                )
                created_count += 1
        except Exception as e:
            errors.append({
                "name": preset["name"],
                "error": str(e)
            })

    return {
        "message": f"已创建 {created_count} 个预设配置",
        "created_count": created_count,
        "errors": errors
    }


# ========== 按类型查询 ==========

@router.get("/by-type/{algorithm_type}", response_model=AlgorithmConfigList)
async def get_configs_by_type(
    algorithm_type: AlgorithmTypeEnum,
    db: AsyncSession = Depends(get_db)
):
    """根据算法类型获取配置"""
    configs = await algorithm_service.get_configs_by_type(db, algorithm_type.value)
    return {
        "total": len(configs),
        "items": configs
    }


# ========== 特定算法配置创建端点 ==========

@router.post("/ga", response_model=AlgorithmConfigResponse)
async def create_ga_config(
    name: str,
    ga_config: GAConfigCreate,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """创建遗传算法配置"""
    config_data = AlgorithmConfigCreate(
        name=name,
        algorithm_type=AlgorithmTypeEnum.GA,
        description=description,
        config_json=ga_config.model_dump()
    )
    db_config = await algorithm_service.create_config(db, config_data)
    return db_config


@router.post("/tabu", response_model=AlgorithmConfigResponse)
async def create_tabu_config(
    name: str,
    tabu_config: TabuConfigCreate,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """创建禁忌搜索配置"""
    config_data = AlgorithmConfigCreate(
        name=name,
        algorithm_type=AlgorithmTypeEnum.TABU,
        description=description,
        config_json=tabu_config.model_dump()
    )
    db_config = await algorithm_service.create_config(db, config_data)
    return db_config


@router.post("/sa", response_model=AlgorithmConfigResponse)
async def create_sa_config(
    name: str,
    sa_config: SAConfigCreate,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """创建模拟退火配置"""
    config_data = AlgorithmConfigCreate(
        name=name,
        algorithm_type=AlgorithmTypeEnum.SA,
        description=description,
        config_json=sa_config.model_dump()
    )
    db_config = await algorithm_service.create_config(db, config_data)
    return db_config


@router.post("/aco", response_model=AlgorithmConfigResponse)
async def create_aco_config(
    name: str,
    aco_config: ACOConfigCreate,
    description: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """创建蚁群算法配置"""
    config_data = AlgorithmConfigCreate(
        name=name,
        algorithm_type=AlgorithmTypeEnum.ACO,
        description=description,
        config_json=aco_config.model_dump()
    )
    db_config = await algorithm_service.create_config(db, config_data)
    return db_config


# ========== 算法比较 ==========

@router.post("/compare", response_model=AlgorithmComparisonResponse)
async def compare_algorithms(
    request: AlgorithmComparisonRequest,
    db: AsyncSession = Depends(get_db)
):
    """比较多个算法配置的性能"""
    # 这里应该实际运行算法比较
    # 目前返回模拟数据
    results = []

    for config_id in request.algorithm_config_ids:
        config = await algorithm_service.get_config(db, config_id)
        if config:
            # 模拟比较结果
            import random
            results.append({
                "algorithm_config_id": config_id,
                "algorithm_type": config.algorithm_type.value if hasattr(config.algorithm_type, 'value') else str(config.algorithm_type),
                "avg_completion_rate": random.uniform(0.7, 0.95),
                "avg_runtime_seconds": random.uniform(30, 300),
                "avg_total_value": random.uniform(1000, 5000),
                "best_value": random.uniform(4000, 6000),
                "worst_value": random.uniform(500, 2000),
                "std_deviation": random.uniform(100, 500)
            })

    # 找出最优算法（按平均完成率）
    best_algorithm_id = None
    if results:
        best = max(results, key=lambda x: x["avg_completion_rate"])
        best_algorithm_id = best["algorithm_config_id"]

    return {
        "scenario_id": request.scenario_id,
        "run_count": request.run_count,
        "results": results,
        "best_algorithm_id": best_algorithm_id
    }
