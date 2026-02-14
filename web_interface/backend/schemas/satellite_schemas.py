# -*- coding: utf-8 -*-
"""
卫星相关Pydantic Schema

注意：卫星模板和星座相关schema在constellation_schemas.py中定义
此文件主要包含卫星运行时的观测能力和状态相关schema
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from database.models import SatelliteTypeEnum


# ========== 卫星能力Schema ==========

class SatelliteCapabilityBase(BaseModel):
    """卫星能力基础Schema"""
    satellite_id: str
    max_roll_deg: float
    max_pitch_deg: float
    min_roll_deg: Optional[float] = None
    min_pitch_deg: Optional[float] = None
    max_slew_rate_deg_per_sec: Optional[float] = None


class SatelliteCapabilityCreate(SatelliteCapabilityBase):
    """创建卫星能力请求"""
    pass


class SatelliteCapabilityUpdate(BaseModel):
    """更新卫星能力请求"""
    max_roll_deg: Optional[float] = None
    max_pitch_deg: Optional[float] = None
    min_roll_deg: Optional[float] = None
    min_pitch_deg: Optional[float] = None
    max_slew_rate_deg_per_sec: Optional[float] = None


class SatelliteCapabilityResponse(SatelliteCapabilityBase):
    """卫星能力响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


# ========== 卫星资源Schema ==========

class SatelliteResourceBase(BaseModel):
    """卫星资源基础Schema"""
    satellite_id: str
    storage_capacity_gb: float
    power_capacity_wh: float
    initial_storage_gb: Optional[float] = 0.0
    initial_power_wh: Optional[float] = None


class SatelliteResourceCreate(SatelliteResourceBase):
    """创建卫星资源请求"""
    pass


class SatelliteResourceUpdate(BaseModel):
    """更新卫星资源请求"""
    storage_capacity_gb: Optional[float] = None
    power_capacity_wh: Optional[float] = None
    initial_storage_gb: Optional[float] = None
    initial_power_wh: Optional[float] = None


class SatelliteResourceResponse(SatelliteResourceBase):
    """卫星资源响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


# ========== 卫星状态Schema ==========

class SatelliteStatusBase(BaseModel):
    """卫星状态基础Schema"""
    satellite_id: str
    current_storage_gb: float
    current_power_wh: float
    last_update_time: datetime
    is_available: bool = True


class SatelliteStatusCreate(SatelliteStatusBase):
    """创建卫星状态请求"""
    pass


class SatelliteStatusUpdate(BaseModel):
    """更新卫星状态请求"""
    current_storage_gb: Optional[float] = None
    current_power_wh: Optional[float] = None
    last_update_time: Optional[datetime] = None
    is_available: Optional[bool] = None


class SatelliteStatusResponse(SatelliteStatusBase):
    """卫星状态响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


# ========== 成像模式Schema ==========

class ImagingModeBase(BaseModel):
    """成像模式基础Schema"""
    name: str
    mode_type: str  # strip, stare, area, spotlight, stripmap, sliding_spotlight, scanSAR
    resolution_m: float
    data_rate_mbps: float
    power_consumption_w: float
    compression_ratio: Optional[float] = None
    max_duration_sec: Optional[float] = None


class ImagingModeCreate(ImagingModeBase):
    """创建成像模式请求"""
    pass


class ImagingModeUpdate(BaseModel):
    """更新成像模式请求"""
    name: Optional[str] = None
    mode_type: Optional[str] = None
    resolution_m: Optional[float] = None
    data_rate_mbps: Optional[float] = None
    power_consumption_w: Optional[float] = None
    compression_ratio: Optional[float] = None
    max_duration_sec: Optional[float] = None


class ImagingModeResponse(ImagingModeBase):
    """成像模式响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class ImagingModeList(BaseModel):
    """成像模式列表响应"""
    total: int
    items: List[ImagingModeResponse]


# ========== 完整卫星信息Schema ==========

class SatelliteInfoResponse(BaseModel):
    """完整卫星信息响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    sat_type: SatelliteTypeEnum
    altitude_km: float
    inclination_deg: float
    capabilities: Optional[SatelliteCapabilityResponse] = None
    resources: Optional[SatelliteResourceResponse] = None
    imaging_modes: List[ImagingModeResponse] = []
