# -*- coding: utf-8 -*-
"""
地面站相关Pydantic Schema
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime


# ========== 地面站Schema ==========

class GroundStationBase(BaseModel):
    """地面站基础Schema"""
    name: str
    latitude: float
    longitude: float
    altitude_m: Optional[float] = 0.0
    min_elevation_deg: Optional[float] = 5.0
    max_data_rate_mbps: Optional[float] = None
    antenna_count: Optional[int] = 1


class GroundStationCreate(GroundStationBase):
    """创建地面站请求"""
    pass


class GroundStationUpdate(BaseModel):
    """更新地面站请求"""
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    altitude_m: Optional[float] = None
    min_elevation_deg: Optional[float] = None
    max_data_rate_mbps: Optional[float] = None
    antenna_count: Optional[int] = None


class GroundStationResponse(GroundStationBase):
    """地面站响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class GroundStationList(BaseModel):
    """地面站列表响应"""
    total: int
    items: List[GroundStationResponse]


# ========== 天线Schema ==========

class AntennaBase(BaseModel):
    """天线基础Schema"""
    ground_station_id: str
    antenna_id: str
    name: Optional[str] = None
    max_data_rate_mbps: Optional[float] = None
    frequency_band: Optional[str] = None  # S, X, Ka, etc.
    is_available: bool = True


class AntennaCreate(AntennaBase):
    """创建天线请求"""
    pass


class AntennaUpdate(BaseModel):
    """更新天线请求"""
    name: Optional[str] = None
    max_data_rate_mbps: Optional[float] = None
    frequency_band: Optional[str] = None
    is_available: Optional[bool] = None


class AntennaResponse(AntennaBase):
    """天线响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class AntennaList(BaseModel):
    """天线列表响应"""
    total: int
    items: List[AntennaResponse]


# ========== 地面站可用时间窗口Schema ==========

class StationVisibilityWindowBase(BaseModel):
    """地面站可见窗口基础Schema"""
    ground_station_id: str
    satellite_id: str
    start_time: datetime
    end_time: datetime
    max_elevation_deg: Optional[float] = None


class StationVisibilityWindowCreate(StationVisibilityWindowBase):
    """创建地面站可见窗口请求"""
    pass


class StationVisibilityWindowResponse(StationVisibilityWindowBase):
    """地面站可见窗口响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    duration_sec: Optional[float] = None


class StationVisibilityWindowList(BaseModel):
    """地面站可见窗口列表响应"""
    total: int
    items: List[StationVisibilityWindowResponse]


# ========== 完整地面站信息Schema ==========

class GroundStationWithAntennasResponse(GroundStationResponse):
    """包含天线的地面站响应"""
    antennas: List[AntennaResponse] = []
    visibility_windows: List[StationVisibilityWindowResponse] = []
