# -*- coding: utf-8 -*-
"""
场景相关Pydantic Schema
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime


# ========== 场景Schema ==========

class ScenarioBase(BaseModel):
    """场景基础Schema"""
    name: str
    constellation_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    configuration_json: Optional[Dict[str, Any]] = None


class ScenarioCreate(ScenarioBase):
    """创建场景请求"""
    target_ids: Optional[List[str]] = None  # 可选：同时关联目标


class ScenarioUpdate(BaseModel):
    """更新场景请求"""
    name: Optional[str] = None
    constellation_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    description: Optional[str] = None
    configuration_json: Optional[Dict[str, Any]] = None


class ScenarioResponse(ScenarioBase):
    """场景响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class ScenarioList(BaseModel):
    """场景列表响应"""
    total: int
    items: List[ScenarioResponse]


# ========== 场景-目标关联Schema ==========

class ScenarioTargetBase(BaseModel):
    """场景目标关联基础Schema"""
    scenario_id: str
    target_id: str


class ScenarioTargetCreate(ScenarioTargetBase):
    """创建场景目标关联请求"""
    pass


class ScenarioTargetResponse(ScenarioTargetBase):
    """场景目标关联响应"""
    model_config = ConfigDict(from_attributes=True)


class ScenarioTargetList(BaseModel):
    """场景目标关联列表响应"""
    total: int
    items: List[ScenarioTargetResponse]


# ========== 批量操作Schema ==========

class ScenarioBatchAddTargetsRequest(BaseModel):
    """批量添加目标到场景请求"""
    target_ids: List[str]


class ScenarioBatchRemoveTargetsRequest(BaseModel):
    """批量从场景移除目标请求"""
    target_ids: List[str]


class ScenarioBatchTargetsResponse(BaseModel):
    """批量操作目标响应"""
    success_count: int
    failed_count: int
    errors: List[Dict[str, Any]] = []


# ========== 场景配置Schema ==========

class ScenarioConfigurationBase(BaseModel):
    """场景配置基础Schema"""
    time_step_seconds: Optional[int] = 60
    min_observation_duration_sec: Optional[int] = 10
    max_observation_duration_sec: Optional[int] = 300
    cloud_coverage_threshold: Optional[float] = 0.3
    enable_cloud_constraint: Optional[bool] = True
    enable_storage_constraint: Optional[bool] = True
    enable_energy_constraint: Optional[bool] = True
    enable_transition_constraint: Optional[bool] = True


class ScenarioConfigurationCreate(ScenarioConfigurationBase):
    """创建场景配置请求"""
    pass


class ScenarioConfigurationUpdate(ScenarioConfigurationBase):
    """更新场景配置请求"""
    pass


class ScenarioConfigurationResponse(ScenarioConfigurationBase):
    """场景配置响应"""
    model_config = ConfigDict(from_attributes=True)


# ========== 完整场景详情Schema ==========

class ScenarioDetailResponse(ScenarioResponse):
    """包含完整信息的场景响应"""
    constellation: Optional[Dict[str, Any]] = None
    targets: List[Dict[str, Any]] = []
    target_count: int = 0
    tasks: List[Dict[str, Any]] = []
    configuration: Optional[ScenarioConfigurationResponse] = None


# ========== 场景复制Schema ==========

class ScenarioCloneRequest(BaseModel):
    """复制场景请求"""
    new_name: Optional[str] = None
    copy_targets: bool = True
    copy_configuration: bool = True


class ScenarioCloneResponse(BaseModel):
    """复制场景响应"""
    original_id: str
    new_id: str
    new_name: str
    target_count: int
