# -*- coding: utf-8 -*-
"""
目标相关Pydantic Schema
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from database.models import TargetTypeEnum


# ========== 目标Schema ==========

class TargetBase(BaseModel):
    """目标基础Schema"""
    name: str
    target_type: TargetTypeEnum
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    priority: Optional[int] = 5
    required_resolution_m: Optional[float] = None
    polygon_json: Optional[Dict[str, Any]] = None  # 区域目标的多边形
    path_json: Optional[List[Dict[str, Any]]] = None  # 动态目标的路径
    properties_json: Optional[Dict[str, Any]] = None  # 其他属性


class TargetCreate(TargetBase):
    """创建目标请求"""
    pass


class TargetUpdate(BaseModel):
    """更新目标请求"""
    name: Optional[str] = None
    target_type: Optional[TargetTypeEnum] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    priority: Optional[int] = None
    required_resolution_m: Optional[float] = None
    polygon_json: Optional[Dict[str, Any]] = None
    path_json: Optional[List[Dict[str, Any]]] = None
    properties_json: Optional[Dict[str, Any]] = None


class TargetResponse(TargetBase):
    """目标响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class TargetList(BaseModel):
    """目标列表响应"""
    total: int
    items: List[TargetResponse]


# ========== 点目标专用Schema ==========

class PointTargetCreate(BaseModel):
    """创建点目标请求"""
    name: str
    latitude: float
    longitude: float
    priority: Optional[int] = 5
    required_resolution_m: Optional[float] = None
    properties_json: Optional[Dict[str, Any]] = None


class PointTargetResponse(TargetResponse):
    """点目标响应"""
    pass


# ========== 网格目标专用Schema ==========

class GridTargetCreate(BaseModel):
    """创建网格目标请求"""
    name: str
    center_latitude: float
    center_longitude: float
    size_deg: Optional[float] = 0.1
    grid_divisions: Optional[int] = 4
    priority: Optional[int] = 5
    required_resolution_m: Optional[float] = None


class GridTargetResponse(TargetResponse):
    """网格目标响应"""
    center_latitude: float
    center_longitude: float
    size_deg: float
    grid_divisions: int


# ========== 区域目标专用Schema ==========

class AreaTargetCreate(BaseModel):
    """创建区域目标请求"""
    name: str
    polygon: List[List[float]]  # [[lat, lon], [lat, lon], ...]
    priority: Optional[int] = 5
    required_resolution_m: Optional[float] = None
    decomposition_strategy: Optional[str] = "grid"  # grid, strip, adaptive


class AreaTargetResponse(TargetResponse):
    """区域目标响应"""
    polygon: List[List[float]]
    area_km2: Optional[float] = None


# ========== 动态目标专用Schema ==========

class MovingTargetCreate(BaseModel):
    """创建动态目标请求"""
    name: str
    target_subtype: str  # vehicle, ship, aircraft
    path: List[Dict[str, Any]]  # [{"time": "2024-01-01T00:00:00Z", "lat": x, "lon": y}, ...]
    priority: Optional[int] = 5
    required_resolution_m: Optional[float] = None
    speed_kmh: Optional[float] = None


class MovingTargetResponse(TargetResponse):
    """动态目标响应"""
    target_subtype: str
    speed_kmh: Optional[float] = None
    path: List[Dict[str, Any]]


# ========== 目标分组Schema ==========

class TargetGroupBase(BaseModel):
    """目标分组基础Schema"""
    name: str
    description: Optional[str] = None
    target_ids: List[str]


class TargetGroupCreate(TargetGroupBase):
    """创建目标分组请求"""
    pass


class TargetGroupUpdate(BaseModel):
    """更新目标分组请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    target_ids: Optional[List[str]] = None


class TargetGroupResponse(TargetGroupBase):
    """目标分组响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class TargetGroupList(BaseModel):
    """目标分组列表响应"""
    total: int
    items: List[TargetGroupResponse]


# ========== 目标集导入Schema ==========

class TargetBatchImportItem(BaseModel):
    """批量导入目标项"""
    name: str
    target_type: TargetTypeEnum
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    priority: Optional[int] = 5
    required_resolution_m: Optional[float] = None
    polygon_json: Optional[Dict[str, Any]] = None
    path_json: Optional[List[Dict[str, Any]]] = None
    properties_json: Optional[Dict[str, Any]] = None


class TargetBatchImportRequest(BaseModel):
    """批量导入目标请求"""
    targets: List[TargetBatchImportItem]


class TargetBatchImportResponse(BaseModel):
    """批量导入目标响应"""
    success_count: int
    failed_count: int
    errors: List[Dict[str, Any]] = []
    created_ids: List[str] = []
