# -*- coding: utf-8 -*-
"""
结果相关Pydantic Schema
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from database.models import SeverityEnum


# ========== 规划结果主Schema ==========

class PlanningResultBase(BaseModel):
    """规划结果基础Schema"""
    task_id: str


class PlanningResultCreate(PlanningResultBase):
    """创建规划结果请求"""
    algorithm_type: Optional[str] = None
    scenario_name: Optional[str] = None
    runtime_seconds: Optional[float] = None
    iterations_completed: Optional[int] = None
    task_completion_rate: Optional[float] = None
    total_value: Optional[float] = None
    targets_covered: Optional[int] = None
    targets_total: Optional[int] = None
    avg_storage_usage: Optional[float] = None
    max_storage_usage: Optional[float] = None
    avg_energy_usage: Optional[float] = None
    max_energy_usage: Optional[float] = None
    completion_time_hours: Optional[float] = None
    is_feasible: Optional[bool] = True
    result_json: Optional[Dict[str, Any]] = None


class PlanningResultUpdate(BaseModel):
    """更新规划结果请求"""
    runtime_seconds: Optional[float] = None
    iterations_completed: Optional[int] = None
    task_completion_rate: Optional[float] = None
    total_value: Optional[float] = None
    targets_covered: Optional[int] = None
    targets_total: Optional[int] = None
    avg_storage_usage: Optional[float] = None
    max_storage_usage: Optional[float] = None
    avg_energy_usage: Optional[float] = None
    max_energy_usage: Optional[float] = None
    completion_time_hours: Optional[float] = None
    is_feasible: Optional[bool] = None
    result_json: Optional[Dict[str, Any]] = None


class PlanningResultResponse(PlanningResultBase):
    """规划结果响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    algorithm_type: Optional[str] = None
    scenario_name: Optional[str] = None
    runtime_seconds: Optional[float] = None
    iterations_completed: Optional[int] = None
    task_completion_rate: Optional[float] = None
    total_value: Optional[float] = None
    targets_covered: Optional[int] = None
    targets_total: Optional[int] = None
    avg_storage_usage: Optional[float] = None
    max_storage_usage: Optional[float] = None
    avg_energy_usage: Optional[float] = None
    max_energy_usage: Optional[float] = None
    completion_time_hours: Optional[float] = None
    is_feasible: bool
    result_json: Optional[Dict[str, Any]] = None
    created_at: datetime


class PlanningResultList(BaseModel):
    """规划结果列表响应"""
    total: int
    items: List[PlanningResultResponse]


# ========== 观测记录Schema ==========

class ObservationBase(BaseModel):
    """观测记录基础Schema"""
    result_id: str
    target_id: str
    satellite_id: str
    satellite_type: Optional[str] = None
    observation_time: datetime
    duration_sec: Optional[int] = None
    elevation_deg: Optional[float] = None
    off_nadir_deg: Optional[float] = None
    data_volume_gb: Optional[float] = None
    imaging_mode: Optional[str] = None
    target_latitude: Optional[float] = None
    target_longitude: Optional[float] = None
    target_priority: Optional[int] = None
    required_uplink: bool = False


class ObservationCreate(ObservationBase):
    """创建观测记录请求"""
    pass


class ObservationUpdate(BaseModel):
    """更新观测记录请求"""
    duration_sec: Optional[int] = None
    elevation_deg: Optional[float] = None
    off_nadir_deg: Optional[float] = None
    data_volume_gb: Optional[float] = None
    imaging_mode: Optional[str] = None
    required_uplink: Optional[bool] = None


class ObservationResponse(ObservationBase):
    """观测记录响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class ObservationList(BaseModel):
    """观测记录列表响应"""
    total: int
    items: List[ObservationResponse]


# ========== 数传计划Schema ==========

class DownlinkPlanBase(BaseModel):
    """数传计划基础Schema"""
    result_id: str
    satellite_id: str
    task_id: Optional[str] = None
    station_id: str
    station_name: Optional[str] = None
    station_latitude: Optional[float] = None
    station_longitude: Optional[float] = None
    antenna_id: Optional[str] = None
    start_time: datetime
    end_time: datetime
    duration_sec: Optional[float] = None
    data_volume_gb: Optional[float] = None
    data_rate_mbps: Optional[float] = None
    is_segmented: bool = False
    is_aggregated: bool = False
    segment_number: Optional[int] = None
    total_segments: Optional[int] = None


class DownlinkPlanCreate(DownlinkPlanBase):
    """创建数传计划请求"""
    pass


class DownlinkPlanUpdate(BaseModel):
    """更新数传计划请求"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_sec: Optional[float] = None
    data_volume_gb: Optional[float] = None
    data_rate_mbps: Optional[float] = None


class DownlinkPlanResponse(DownlinkPlanBase):
    """数传计划响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class DownlinkPlanList(BaseModel):
    """数传计划列表响应"""
    total: int
    items: List[DownlinkPlanResponse]


# ========== 上注计划Schema ==========

class UplinkPlanBase(BaseModel):
    """上注计划基础Schema"""
    result_id: str
    satellite_id: str
    station_id: str
    station_name: Optional[str] = None
    antenna_id: Optional[str] = None
    start_time: datetime
    end_time: datetime
    duration_sec: Optional[float] = None
    num_tasks: Optional[int] = None
    task_ids_json: Optional[List[str]] = None


class UplinkPlanCreate(UplinkPlanBase):
    """创建上注计划请求"""
    pass


class UplinkPlanUpdate(BaseModel):
    """更新上注计划请求"""
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_sec: Optional[float] = None
    num_tasks: Optional[int] = None
    task_ids_json: Optional[List[str]] = None


class UplinkPlanResponse(UplinkPlanBase):
    """上注计划响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class UplinkPlanList(BaseModel):
    """上注计划列表响应"""
    total: int
    items: List[UplinkPlanResponse]


# ========== 约束违规Schema ==========

class ConstraintViolationBase(BaseModel):
    """约束违规基础Schema"""
    result_id: str
    constraint_type: str
    severity: SeverityEnum
    message: str
    action1_id: Optional[str] = None
    action2_id: Optional[str] = None
    required_gap: Optional[float] = None
    actual_gap: Optional[float] = None


class ConstraintViolationCreate(ConstraintViolationBase):
    """创建约束违规记录请求"""
    pass


class ConstraintViolationResponse(ConstraintViolationBase):
    """约束违规响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class ConstraintViolationList(BaseModel):
    """约束违规列表响应"""
    total: int
    items: List[ConstraintViolationResponse]


# ========== 资源时间线Schema ==========

class ResourceTimelineBase(BaseModel):
    """资源时间线基础Schema"""
    result_id: str
    satellite_id: str
    timeline_type: str  # storage, energy, payload
    event_time: datetime
    event_type: str
    value: float
    value_max: Optional[float] = None
    metadata_json: Optional[Dict[str, Any]] = None


class ResourceTimelineCreate(ResourceTimelineBase):
    """创建资源时间线请求"""
    pass


class ResourceTimelineResponse(ResourceTimelineBase):
    """资源时间线响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class ResourceTimelineList(BaseModel):
    """资源时间线列表响应"""
    total: int
    items: List[ResourceTimelineResponse]


# ========== 完整结果详情Schema ==========

class PlanningResultDetailResponse(PlanningResultResponse):
    """包含详细信息的规划结果响应"""
    observations: List[ObservationResponse] = []
    downlink_plans: List[DownlinkPlanResponse] = []
    uplink_plans: List[UplinkPlanResponse] = []
    violations: List[ConstraintViolationResponse] = []
    resource_timeline: List[ResourceTimelineResponse] = []


# ========== 结果比较Schema ==========

class ResultComparisonRequest(BaseModel):
    """结果比较请求"""
    result_ids: List[str]
    metrics: Optional[List[str]] = None  # 指定要比较的指标


class ResultComparisonMetric(BaseModel):
    """结果比较指标"""
    metric_name: str
    values: Dict[str, float]  # result_id -> value
    best_result_id: Optional[str] = None


class ResultComparisonResponse(BaseModel):
    """结果比较响应"""
    results: List[PlanningResultResponse]
    comparisons: List[ResultComparisonMetric]
    overall_best_id: Optional[str] = None


# ========== 结果导出Schema ==========

class ResultExportRequest(BaseModel):
    """结果导出请求"""
    result_id: str
    format: str  # json, csv, excel
    include_observations: bool = True
    include_downlinks: bool = True
    include_uplinks: bool = True
    include_violations: bool = True


class ResultExportResponse(BaseModel):
    """结果导出响应"""
    result_id: str
    format: str
    download_url: str
    expires_at: datetime


# ========== 结果统计Schema ==========

class ResultStatisticsResponse(BaseModel):
    """结果统计响应"""
    result_id: str
    total_observations: int
    total_downlinks: int
    total_uplinks: int
    total_violations: int
    critical_violations: int
    warning_violations: int
    observation_coverage_percent: float
    total_data_volume_gb: float
    avg_observation_duration_sec: float
    satellite_utilization: Dict[str, float]  # satellite_id -> utilization
    ground_station_utilization: Dict[str, float]  # station_id -> utilization
