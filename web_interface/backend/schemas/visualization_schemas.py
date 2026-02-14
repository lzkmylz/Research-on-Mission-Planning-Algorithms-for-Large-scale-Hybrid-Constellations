# -*- coding: utf-8 -*-
"""
可视化数据相关Schema
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime


class SatellitePosition(BaseModel):
    """卫星位置"""
    satellite_id: str
    name: Optional[str] = None
    latitude: float
    longitude: float
    altitude_km: float
    timestamp: datetime


class GroundTrack(BaseModel):
    """地面轨迹"""
    satellite_id: str
    name: Optional[str] = None
    points: List[Dict[str, float]]  # [{lat, lon, alt, time}, ...]


class CoverageData(BaseModel):
    """覆盖数据"""
    satellite_id: str
    footprint: List[Dict[str, float]]  # 覆盖区域多边形
    center_lat: float
    center_lon: float
    start_time: datetime
    end_time: datetime


class ObservationVisualization(BaseModel):
    """观测可视化数据"""
    observation_id: str
    target_id: str
    target_name: str
    satellite_id: str
    target_lat: float
    target_lon: float
    observation_time: datetime
    duration_sec: int
    priority: int
    color: Optional[str] = None  # 根据优先级显示不同颜色


class VisualizationData(BaseModel):
    """完整可视化数据"""
    scenario_id: str
    timestamp: datetime
    satellites: List[SatellitePosition]
    ground_tracks: Optional[List[GroundTrack]] = None
    coverage: Optional[List[CoverageData]] = None
    observations: Optional[List[ObservationVisualization]] = None
    ground_stations: Optional[List[Dict[str, Any]]] = None
