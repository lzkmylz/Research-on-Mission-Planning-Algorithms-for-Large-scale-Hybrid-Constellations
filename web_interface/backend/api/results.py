# -*- coding: utf-8 -*-
"""
结果查询API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from services.result_service import result_service
from schemas.result_schemas import (
    PlanningResultResponse, PlanningResultList, PlanningResultDetailResponse,
    ResultComparisonRequest, ResultComparisonResponse, ResultStatisticsResponse,
    ObservationResponse, ObservationList, DownlinkPlanResponse, DownlinkPlanList,
    UplinkPlanResponse, UplinkPlanList, ConstraintViolationResponse,
    ConstraintViolationList, ResourceTimelineResponse, ResourceTimelineList,
    ResultExportRequest, ResultExportResponse
)

router = APIRouter()


@router.get("", response_model=PlanningResultList)
async def list_results(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    algorithm_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取结果列表"""
    if algorithm_type:
        results = await result_service.get_results_by_algorithm(db, algorithm_type, skip=skip, limit=limit)
    else:
        results = await result_service.list_results(db, skip=skip, limit=limit)

    return {
        "total": len(results),
        "items": results
    }


@router.get("/{result_id}", response_model=PlanningResultDetailResponse)
async def get_result(
    result_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取结果详情"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    return {
        "id": result.id,
        "task_id": result.task_id,
        "algorithm_type": result.algorithm_type,
        "scenario_name": result.scenario_name,
        "runtime_seconds": result.runtime_seconds,
        "iterations_completed": result.iterations_completed,
        "task_completion_rate": result.task_completion_rate,
        "total_value": result.total_value,
        "targets_covered": result.targets_covered,
        "targets_total": result.targets_total,
        "avg_storage_usage": result.avg_storage_usage,
        "max_storage_usage": result.max_storage_usage,
        "avg_energy_usage": result.avg_energy_usage,
        "max_energy_usage": result.max_energy_usage,
        "completion_time_hours": result.completion_time_hours,
        "is_feasible": result.is_feasible,
        "result_json": result.result_json,
        "created_at": result.created_at,
        "observations": result.observations if hasattr(result, 'observations') else [],
        "downlink_plans": result.downlink_plans if hasattr(result, 'downlink_plans') else [],
        "uplink_plans": result.uplink_plans if hasattr(result, 'uplink_plans') else [],
        "violations": result.violations if hasattr(result, 'violations') else [],
        "resource_timeline": result.resource_timeline if hasattr(result, 'resource_timeline') else []
    }


@router.get("/by-task/{task_id}", response_model=PlanningResultResponse)
async def get_result_by_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """根据任务ID获取结果"""
    result = await result_service.get_result_by_task(db, task_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")
    return result


@router.delete("/{result_id}")
async def delete_result(
    result_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除结果"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    deleted = await result_service.delete_result(db, result_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="删除失败")

    return {"message": "结果已删除"}


# ========== 观测记录端点 ==========

@router.get("/{result_id}/observations", response_model=ObservationList)
async def get_observations(
    result_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """获取观测记录列表"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    observations = result.observations if hasattr(result, 'observations') else []
    # 分页
    paginated = observations[skip:skip + limit] if observations else []

    return {
        "total": len(observations) if observations else 0,
        "items": paginated
    }


@router.get("/{result_id}/observations/by-satellite/{satellite_id}", response_model=ObservationList)
async def get_observations_by_satellite(
    result_id: str,
    satellite_id: str,
    db: AsyncSession = Depends(get_db)
):
    """根据卫星获取观测记录"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    observations = []
    if hasattr(result, 'observations') and result.observations:
        observations = [obs for obs in result.observations if obs.satellite_id == satellite_id]

    return {
        "total": len(observations),
        "items": observations
    }


@router.get("/{result_id}/observations/by-target/{target_id}", response_model=ObservationList)
async def get_observations_by_target(
    result_id: str,
    target_id: str,
    db: AsyncSession = Depends(get_db)
):
    """根据目标获取观测记录"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    observations = []
    if hasattr(result, 'observations') and result.observations:
        observations = [obs for obs in result.observations if obs.target_id == target_id]

    return {
        "total": len(observations),
        "items": observations
    }


# ========== 数传计划端点 ==========

@router.get("/{result_id}/downlinks", response_model=DownlinkPlanList)
async def get_downlink_plans(
    result_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """获取数传计划列表"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    downlinks = result.downlink_plans if hasattr(result, 'downlink_plans') else []
    paginated = downlinks[skip:skip + limit] if downlinks else []

    return {
        "total": len(downlinks) if downlinks else 0,
        "items": paginated
    }


@router.get("/{result_id}/downlinks/by-station/{station_id}", response_model=DownlinkPlanList)
async def get_downlinks_by_station(
    result_id: str,
    station_id: str,
    db: AsyncSession = Depends(get_db)
):
    """根据地面站获取数传计划"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    downlinks = []
    if hasattr(result, 'downlink_plans') and result.downlink_plans:
        downlinks = [dl for dl in result.downlink_plans if dl.station_id == station_id]

    return {
        "total": len(downlinks),
        "items": downlinks
    }


# ========== 上注计划端点 ==========

@router.get("/{result_id}/uplinks", response_model=UplinkPlanList)
async def get_uplink_plans(
    result_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
    db: AsyncSession = Depends(get_db)
):
    """获取上注计划列表"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    uplinks = result.uplink_plans if hasattr(result, 'uplink_plans') else []
    paginated = uplinks[skip:skip + limit] if uplinks else []

    return {
        "total": len(uplinks) if uplinks else 0,
        "items": paginated
    }


# ========== 约束违规端点 ==========

@router.get("/{result_id}/violations", response_model=ConstraintViolationList)
async def get_constraint_violations(
    result_id: str,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取约束违规列表"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    violations = result.violations if hasattr(result, 'violations') else []

    if severity and violations:
        violations = [v for v in violations if v.severity.value == severity]

    return {
        "total": len(violations) if violations else 0,
        "items": violations if violations else []
    }


# ========== 资源时间线端点 ==========

@router.get("/{result_id}/resource-timeline", response_model=ResourceTimelineList)
async def get_resource_timeline(
    result_id: str,
    satellite_id: Optional[str] = None,
    timeline_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取资源时间线"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    timeline = result.resource_timeline if hasattr(result, 'resource_timeline') else []

    if timeline:
        if satellite_id:
            timeline = [t for t in timeline if t.satellite_id == satellite_id]
        if timeline_type:
            timeline = [t for t in timeline if t.timeline_type == timeline_type]

    return {
        "total": len(timeline) if timeline else 0,
        "items": timeline if timeline else []
    }


# ========== 结果比较端点 ==========

@router.post("/compare", response_model=ResultComparisonResponse)
async def compare_results(
    request: ResultComparisonRequest,
    db: AsyncSession = Depends(get_db)
):
    """比较多个结果"""
    comparison = await result_service.compare_results(db, request)

    return {
        "results": comparison["results"],
        "comparisons": comparison["comparisons"],
        "overall_best_id": comparison["overall_best_id"]
    }


# ========== 结果统计端点 ==========

@router.get("/{result_id}/statistics", response_model=ResultStatisticsResponse)
async def get_result_statistics(
    result_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取结果统计信息"""
    stats = await result_service.get_result_statistics(db, result_id)
    if not stats:
        raise HTTPException(status_code=404, detail="结果不存在")

    return stats


# ========== 最优结果端点 ==========

@router.get("/top/{metric}", response_model=PlanningResultList)
async def get_top_results(
    metric: str = Path(..., description="排序指标"),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """获取最优结果"""
    results = await result_service.get_top_results(db, metric=metric, limit=limit)
    return {
        "total": len(results),
        "items": results
    }


# ========== 按场景查询端点 ==========

@router.get("/by-scenario/{scenario_name}", response_model=PlanningResultList)
async def get_results_by_scenario(
    scenario_name: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """根据场景名称获取结果"""
    results = await result_service.get_results_by_scenario(db, scenario_name, skip=skip, limit=limit)
    return {
        "total": len(results),
        "items": results
    }


# ========== 导出端点 ==========

@router.post("/{result_id}/export", response_model=ResultExportResponse)
async def export_result(
    result_id: str,
    request: ResultExportRequest,
    db: AsyncSession = Depends(get_db)
):
    """导出结果"""
    result = await result_service.get_result(db, result_id)
    if not result:
        raise HTTPException(status_code=404, detail="结果不存在")

    # 这里应该实现实际的导出逻辑
    # 目前返回模拟数据
    from datetime import datetime, timedelta

    return {
        "result_id": result_id,
        "format": request.format,
        "download_url": f"/api/results/{result_id}/download?format={request.format}",
        "expires_at": datetime.now() + timedelta(hours=24)
    }
