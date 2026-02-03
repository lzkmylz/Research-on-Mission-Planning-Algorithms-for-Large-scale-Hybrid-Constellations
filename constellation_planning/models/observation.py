# -*- coding: utf-8 -*-
"""
观测机会与成像任务模型
"""

from dataclasses import dataclass, field
from typing import Optional, List, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .target import Target


class ObservationStatus(Enum):
    """观测状态"""
    AVAILABLE = "available"     # 可用
    SCHEDULED = "scheduled"     # 已规划
    EXECUTED = "executed"       # 已执行
    FAILED = "failed"           # 失败（云遮挡等）
    SKIPPED = "skipped"         # 跳过


@dataclass
class ObservationWindow:
    """
    观测机会窗口
    表示卫星对某目标的一次可见性窗口
    """
    id: str
    satellite_id: str
    target_id: str
    sensor_id: str
    
    # 时间窗口
    start_time: str           # ISO 格式
    end_time: str
    duration_sec: float = 0.0
    
    # 几何参数
    off_nadir_deg: float = 0.0      # 离轴角
    sun_elevation_deg: float = 45.0  # 太阳高度角
    incidence_deg: float = 0.0       # 入射角 (SAR)
    
    # 可行性
    is_feasible: bool = True         # 是否满足基本约束
    cloud_cover: float = 0.0         # 云覆盖率 (0-1)
    
    # 成像数据量
    data_volume_gb: float = 0.0
    
    # 状态
    status: ObservationStatus = ObservationStatus.AVAILABLE
    
    def __repr__(self) -> str:
        return f"ObservationWindow({self.id}, sat={self.satellite_id}, target={self.target_id})"


@dataclass
class ImagingTask:
    """
    成像任务
    表示规划结果中的一次具体成像任务
    """
    id: str
    observation_window_id: str
    satellite_id: str
    target_id: str
    sensor_id: str
    
    # 执行时间
    imaging_time: str         # 实际成像时间点
    
    # 机动信息
    roll_angle_deg: float = 0.0
    pitch_angle_deg: float = 0.0
    
    # 成像参数
    imaging_mode: str = ""
    duration_sec: float = 0.0
    
    # 数据信息
    data_volume_gb: float = 0.0
    
    # 优先级/价值
    priority: float = 1.0
    value: float = 1.0        # 成像价值（考虑优先级、质量等）
    
    def __repr__(self) -> str:
        return f"ImagingTask({self.id}, sat={self.satellite_id}, target={self.target_id})"


@dataclass
class PlanningResult:
    """规划结果"""
    tasks: List[ImagingTask] = field(default_factory=list)
    
    # 评价指标
    total_value: float = 0.0
    coverage_rate: float = 0.0
    num_targets_covered: int = 0
    num_observations_used: int = 0
    
    # 约束满足情况
    storage_constraint_satisfied: bool = True
    energy_constraint_satisfied: bool = True
    timing_constraint_satisfied: bool = True
    
    def add_task(self, task: ImagingTask) -> None:
        """添加任务"""
        self.tasks.append(task)
        self.total_value += task.value
        self.num_observations_used += 1
