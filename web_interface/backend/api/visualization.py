# -*- coding: utf-8 -*-
"""
可视化数据API
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from services.visualization_service import visualization_service
from schemas.visualization_schemas import (
    SatellitePosition, GroundTrack, CoverageData,
    ObservationVisualization, VisualizationData
)

router = APIRouter()


@router.get("/satellites/{scenario_id}", response_model=List[SatellitePosition])
async def get_satellite_positions(
    scenario_id: str,
    timestamp: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取卫星位置数据

    - **scenario_id**: 场景ID
    - **timestamp**: 指定时间戳（可选，默认为当前时间）
    """
    positions = await visualization_service.get_satellite_positions(
        db, scenario_id, timestamp
    )
    return positions


@router.get("/ground-tracks/{scenario_id}", response_model=List[GroundTrack])
async def get_ground_tracks(
    scenario_id: str,
    duration_minutes: int = Query(90, ge=1, le=1440),
    db: AsyncSession = Depends(get_db)
):
    """获取卫星地面轨迹

    - **scenario_id**: 场景ID
    - **duration_minutes**: 轨迹持续时间（分钟），默认90分钟
    """
    tracks = await visualization_service.get_ground_tracks(
        db, scenario_id, duration_minutes
    )
    return tracks


@router.get("/coverage/{scenario_id}", response_model=List[CoverageData])
async def get_coverage_data(
    scenario_id: str,
    timestamp: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取卫星覆盖数据

    - **scenario_id**: 场景ID
    - **timestamp**: 指定时间戳（可选，默认为当前时间）
    """
    coverage = await visualization_service.get_coverage_data(
        db, scenario_id, timestamp
    )
    return coverage


@router.get("/observations/{result_id}", response_model=List[ObservationVisualization])
async def get_observation_visualization(
    result_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取观测可视化数据

    - **result_id**: 规划结果ID
    """
    observations = await visualization_service.get_observation_visualization(
        db, result_id
    )
    return observations


@router.get("/full/{scenario_id}", response_model=VisualizationData)
async def get_full_visualization_data(
    scenario_id: str,
    result_id: Optional[str] = None,
    timestamp: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取完整可视化数据

    包含卫星位置、地面轨迹、覆盖区域和观测数据。

    - **scenario_id**: 场景ID
    - **result_id**: 规划结果ID（可选，用于显示观测数据）
    - **timestamp**: 指定时间戳（可选，默认为当前时间）
    """
    data = await visualization_service.get_full_visualization_data(
        db, scenario_id, result_id, timestamp
    )
    return data


@router.get("/timeline/observations/{result_id}")
async def get_observation_timeline(
    result_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取观测时间线数据

    - **result_id**: 规划结果ID
    """
    timeline = await visualization_service.get_observation_timeline(db, result_id)
    return {
        "result_id": result_id,
        "timeline": timeline,
        "total": len(timeline)
    }


@router.get("/timeline/utilization/{result_id}")
async def get_satellite_utilization_timeline(
    result_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取卫星利用率时间线

    - **result_id**: 规划结果ID
    """
    utilization = await visualization_service.get_satellite_utilization_timeline(
        db, result_id
    )
    return utilization


# ========== 实时数据流端点（用于前端轮询） ==========

@router.get("/realtime/{scenario_id}")
async def get_realtime_visualization_data(
    scenario_id: str,
    include_satellites: bool = True,
    include_coverage: bool = True,
    include_ground_tracks: bool = False,
    db: AsyncSession = Depends(get_db)
):
    """获取实时可视化数据（用于前端轮询）

    - **scenario_id**: 场景ID
    - **include_satellites**: 是否包含卫星位置
    - **include_coverage**: 是否包含覆盖区域
    - **include_ground_tracks**: 是否包含地面轨迹
    """
    timestamp = datetime.now()

    response = {
        "scenario_id": scenario_id,
        "timestamp": timestamp.isoformat(),
        "satellites": [],
        "coverage": [],
        "ground_tracks": []
    }

    if include_satellites:
        response["satellites"] = await visualization_service.get_satellite_positions(
            db, scenario_id, timestamp
        )

    if include_coverage:
        response["coverage"] = await visualization_service.get_coverage_data(
            db, scenario_id, timestamp
        )

    if include_ground_tracks:
        response["ground_tracks"] = await visualization_service.get_ground_tracks(
            db, scenario_id, duration_minutes=90
        )

    return response


# ========== 数据聚合端点 ==========

@router.get("/aggregate/coverage-stats/{scenario_id}")
async def get_coverage_statistics(
    scenario_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取覆盖统计信息"""
    coverage = await visualization_service.get_coverage_data(db, scenario_id)

    # 计算统计信息
    total_footprint_area = 0
    satellite_count = len(coverage)

    for cov in coverage:
        # 简化的覆盖面积计算（基于多边形顶点）
        if cov.footprint:
            # 这里应该使用更精确的面积计算
            total_footprint_area += len(cov.footprint) * 100  # 简化的估算

    return {
        "scenario_id": scenario_id,
        "satellite_count": satellite_count,
        "total_footprint_area_km2": total_footprint_area,
        "coverage_regions": [
            {
                "satellite_id": c.satellite_id,
                "center_lat": c.center_lat,
                "center_lon": c.center_lon
            }
            for c in coverage
        ]
    }


@router.get("/aggregate/observation-heatmap/{result_id}")
async def get_observation_heatmap(
    result_id: str,
    grid_size: float = Query(5.0, ge=1.0, le=30.0),
    db: AsyncSession = Depends(get_db)
):
    """获取观测热力图数据

    - **result_id**: 规划结果ID
    - **grid_size**: 网格大小（度），默认5度
    """
    observations = await visualization_service.get_observation_visualization(
        db, result_id
    )

    # 构建热力图网格
    heatmap = {}
    for obs in observations:
        # 计算网格坐标
        grid_lat = round(obs.target_lat / grid_size) * grid_size
        grid_lon = round(obs.target_lon / grid_size) * grid_size
        key = f"{grid_lat},{grid_lon}"

        if key not in heatmap:
            heatmap[key] = {
                "lat": grid_lat,
                "lon": grid_lon,
                "count": 0,
                "observations": []
            }

        heatmap[key]["count"] += 1
        heatmap[key]["observations"].append(obs.observation_id)

    return {
        "result_id": result_id,
        "grid_size": grid_size,
        "heatmap": list(heatmap.values()),
        "total_observations": len(observations)
    }


@router.get("/aggregate/priority-distribution/{result_id}")
async def get_priority_distribution(
    result_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取观测优先级分布"""
    observations = await visualization_service.get_observation_visualization(
        db, result_id
    )

    # 按优先级分组
    distribution = {}
    for obs in observations:
        priority = obs.priority
        if priority not in distribution:
            distribution[priority] = {
                "priority": priority,
                "count": 0,
                "color": obs.color
            }
        distribution[priority]["count"] += 1

    return {
        "result_id": result_id,
        "distribution": list(distribution.values()),
        "total_observations": len(observations)
    }
