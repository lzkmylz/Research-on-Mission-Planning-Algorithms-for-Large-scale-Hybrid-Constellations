# -*- coding: utf-8 -*-
"""
规划任务相关Pydantic Schema
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from datetime import datetime

from database.models import TaskStatusEnum


# ========== 规划任务Schema ==========

class PlanningTaskBase(BaseModel):
    """规划任务基础Schema"""
    scenario_id: str
    algorithm_config_id: str


class PlanningTaskCreate(PlanningTaskBase):
    """创建规划任务请求"""
    pass


class PlanningTaskUpdate(BaseModel):
    """更新规划任务请求"""
    status: Optional[TaskStatusEnum] = None
    progress_pct: Optional[int] = None
    current_iteration: Optional[int] = None
    best_value: Optional[float] = None
    error_message: Optional[str] = None


class PlanningTaskResponse(PlanningTaskBase):
    """规划任务响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: TaskStatusEnum
    progress_pct: int
    current_iteration: int
    best_value: Optional[float] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime


class PlanningTaskList(BaseModel):
    """规划任务列表响应"""
    total: int
    items: List[PlanningTaskResponse]


# ========== 任务状态更新Schema ==========

class TaskStatusUpdateRequest(BaseModel):
    """任务状态更新请求"""
    status: TaskStatusEnum
    progress_pct: Optional[int] = None
    current_iteration: Optional[int] = None
    best_value: Optional[float] = None
    error_message: Optional[str] = None


class TaskProgressUpdateRequest(BaseModel):
    """任务进度更新请求"""
    progress_pct: int
    current_iteration: int
    best_value: Optional[float] = None


# ========== 任务控制Schema ==========

class TaskControlRequest(BaseModel):
    """任务控制请求"""
    action: str  # cancel, pause, resume


class TaskControlResponse(BaseModel):
    """任务控制响应"""
    task_id: str
    action: str
    success: bool
    message: str
    new_status: Optional[TaskStatusEnum] = None


# ========== 任务查询Schema ==========

class TaskFilterRequest(BaseModel):
    """任务过滤请求"""
    status: Optional[TaskStatusEnum] = None
    scenario_id: Optional[str] = None
    algorithm_type: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None


class TaskStatisticsResponse(BaseModel):
    """任务统计响应"""
    total_count: int
    pending_count: int
    running_count: int
    completed_count: int
    failed_count: int
    avg_runtime_seconds: Optional[float] = None
    avg_completion_rate: Optional[float] = None


# ========== 批量任务Schema ==========

class BatchTaskCreateRequest(BaseModel):
    """批量创建任务请求"""
    scenario_id: str
    algorithm_config_ids: List[str]


class BatchTaskCreateResponse(BaseModel):
    """批量创建任务响应"""
    created_count: int
    task_ids: List[str]
    errors: List[Dict[str, Any]] = []


class BatchTaskControlRequest(BaseModel):
    """批量任务控制请求"""
    task_ids: List[str]
    action: str  # cancel, delete


class BatchTaskControlResponse(BaseModel):
    """批量任务控制响应"""
    success_count: int
    failed_count: int
    errors: List[Dict[str, Any]] = []


# ========== 任务详情Schema ==========

class PlanningTaskDetailResponse(PlanningTaskResponse):
    """包含详细信息的规划任务响应"""
    scenario: Optional[Dict[str, Any]] = None
    algorithm_config: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
    logs: List[Dict[str, Any]] = []


# ========== 任务日志Schema ==========

class TaskLogBase(BaseModel):
    """任务日志基础Schema"""
    task_id: str
    log_level: str  # INFO, WARNING, ERROR, DEBUG
    message: str
    metadata_json: Optional[Dict[str, Any]] = None


class TaskLogCreate(TaskLogBase):
    """创建任务日志请求"""
    pass


class TaskLogResponse(TaskLogBase):
    """任务日志响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class TaskLogList(BaseModel):
    """任务日志列表响应"""
    total: int
    items: List[TaskLogResponse]
