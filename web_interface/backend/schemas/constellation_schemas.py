# -*- coding: utf-8 -*-
"""
星座相关Pydantic Schema
"""

from typing import Optional, List, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from database.models import SatelliteTypeEnum


# ========== 卫星模板Schema ==========

class SatelliteTemplateBase(BaseModel):
    """卫星模板基础Schema"""
    name: str
    sat_type: SatelliteTypeEnum
    altitude_km: float
    inclination_deg: float
    max_roll_deg: Optional[float] = None
    max_pitch_deg: Optional[float] = None
    storage_capacity_gb: Optional[float] = None
    power_capacity_wh: Optional[float] = None


class SatelliteTemplateCreate(SatelliteTemplateBase):
    """创建卫星模板请求"""
    pass


class SatelliteTemplateUpdate(BaseModel):
    """更新卫星模板请求"""
    name: Optional[str] = None
    sat_type: Optional[SatelliteTypeEnum] = None
    altitude_km: Optional[float] = None
    inclination_deg: Optional[float] = None
    max_roll_deg: Optional[float] = None
    max_pitch_deg: Optional[float] = None
    storage_capacity_gb: Optional[float] = None
    power_capacity_wh: Optional[float] = None


class SatelliteTemplateResponse(SatelliteTemplateBase):
    """卫星模板响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime


class SatelliteTemplateList(BaseModel):
    """卫星模板列表响应"""
    total: int
    items: List[SatelliteTemplateResponse]


# ========== 星座Schema ==========

class ConstellationBase(BaseModel):
    """星座基础Schema"""
    name: str
    description: Optional[str] = None
    walker_planes: Optional[int] = None
    walker_sats_per_plane: Optional[int] = None
    walker_altitude_km: Optional[float] = None
    walker_inclination_deg: Optional[float] = None
    configuration_json: Optional[dict] = None


class ConstellationCreate(ConstellationBase):
    """创建星座请求"""
    pass


class ConstellationUpdate(BaseModel):
    """更新星座请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    walker_planes: Optional[int] = None
    walker_sats_per_plane: Optional[int] = None
    walker_altitude_km: Optional[float] = None
    walker_inclination_deg: Optional[float] = None
    configuration_json: Optional[dict] = None


class ConstellationResponse(ConstellationBase):
    """星座响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime
    updated_at: datetime


class ConstellationList(BaseModel):
    """星座列表响应"""
    total: int
    items: List[ConstellationResponse]


# ========== 星座-卫星关联Schema ==========

class ConstellationSatelliteBase(BaseModel):
    """星座卫星关联基础Schema"""
    constellation_id: str
    satellite_template_id: str
    plane_number: Optional[int] = None
    sat_number_in_plane: Optional[int] = None


class ConstellationSatelliteCreate(ConstellationSatelliteBase):
    """创建星座卫星关联请求"""
    pass


class ConstellationSatelliteUpdate(BaseModel):
    """更新星座卫星关联请求"""
    plane_number: Optional[int] = None
    sat_number_in_plane: Optional[int] = None


class ConstellationSatelliteResponse(ConstellationSatelliteBase):
    """星座卫星关联响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class ConstellationSatelliteList(BaseModel):
    """星座卫星关联列表响应"""
    total: int
    items: List[ConstellationSatelliteResponse]


# ========== 详细响应（包含关系） ==========

class ConstellationWithSatellitesResponse(ConstellationResponse):
    """包含卫星详情的星座响应"""
    satellites: List[ConstellationSatelliteResponse] = []
