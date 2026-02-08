# -*- coding: utf-8 -*-
"""
上注动作模型

定义上注指令动作的数据结构。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class UplinkAction:
    """上注指令动作
    
    描述一次上注指令的执行，包括上注的任务列表和时间信息。
    上注动作与数传动作共用天线资源。
    
    Attributes:
        id: 上注动作标识
        satellite_id: 目标卫星ID
        station_id: 执行上注的测控站ID
        antenna_id: 使用的天线ID
        start_time: 上注开始时间 (ISO格式)
        end_time: 上注结束时间 (ISO格式)
        duration_sec: 上注持续时间 (秒)
        task_ids: 本次上注的任务ID列表
    """
    id: str
    satellite_id: str
    station_id: str
    antenna_id: str
    
    start_time: str          # ISO 格式
    end_time: str            # ISO 格式
    duration_sec: float = 0.0
    
    task_ids: List[str] = field(default_factory=list)
    
    @property
    def num_tasks(self) -> int:
        """本次上注的任务数量"""
        return len(self.task_ids)
    
    def contains_task(self, task_id: str) -> bool:
        """检查是否包含指定任务"""
        return task_id in self.task_ids
    
    def get_start_datetime(self) -> datetime:
        """获取开始时间的 datetime 对象"""
        return datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
    
    def get_end_datetime(self) -> datetime:
        """获取结束时间的 datetime 对象"""
        return datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
    
    def __repr__(self) -> str:
        return f"UplinkAction({self.id}, sat={self.satellite_id}, station={self.station_id}, {self.num_tasks} tasks)"


@dataclass
class UplinkRequest:
    """上注请求
    
    描述需要上注的任务集合，用于调度器规划上注动作。
    
    Attributes:
        satellite_id: 目标卫星ID
        task_ids: 需要上注的任务ID列表
        earliest_time: 最早可以开始上注的时间
        latest_time: 最晚需要完成上注的时间（即最早任务开始时间减去最小间隔）
        priority: 优先级 (数值越大优先级越高)
    """
    satellite_id: str
    task_ids: List[str]
    earliest_time: str
    latest_time: str
    priority: int = 1
    
    @property
    def num_tasks(self) -> int:
        return len(self.task_ids)
    
    def __repr__(self) -> str:
        return f"UplinkRequest(sat={self.satellite_id}, {self.num_tasks} tasks)"


@dataclass
class DownlinkAction:
    """数传动作
    
    描述一次数据下传的执行。支持单天线和多天线聚合模式。
    
    Attributes:
        id: 数传动作标识
        satellite_id: 卫星ID
        station_id: 地面站ID
        antenna_id: 使用的主天线ID（单天线模式）
        antenna_ids: 使用的天线ID列表（多天线聚合模式）
        start_time: 开始时间 (ISO格式)
        end_time: 结束时间 (ISO格式)
        duration_sec: 持续时间 (秒)
        data_volume_gb: 下传数据量 (GB)
        data_rate_mbps: 下传速率 (Mbps)
        is_aggregated: 是否为多天线聚合模式
    """
    id: str
    satellite_id: str
    station_id: str
    antenna_id: str  # 主天线ID，兼容单天线模式
    
    start_time: str
    end_time: str
    duration_sec: float = 0.0
    
    data_volume_gb: float = 0.0
    data_rate_mbps: float = 0.0
    
    # 多天线聚合支持
    antenna_ids: List[str] = field(default_factory=list)
    is_aggregated: bool = False
    
    def __post_init__(self):
        # 如果没有设置 antenna_ids，使用主天线
        if not self.antenna_ids and self.antenna_id:
            self.antenna_ids = [self.antenna_id]
    
    @property
    def num_antennas(self) -> int:
        """使用的天线数量"""
        return len(self.antenna_ids) if self.antenna_ids else 1
    
    def get_start_datetime(self) -> datetime:
        """获取开始时间的 datetime 对象"""
        return datetime.fromisoformat(self.start_time.replace("Z", "+00:00"))
    
    def get_end_datetime(self) -> datetime:
        """获取结束时间的 datetime 对象"""
        return datetime.fromisoformat(self.end_time.replace("Z", "+00:00"))
    
    def __repr__(self) -> str:
        if self.is_aggregated:
            return f"DownlinkAction({self.id}, sat={self.satellite_id}, {self.num_antennas} antennas, {self.data_volume_gb:.2f}GB)"
        return f"DownlinkAction({self.id}, sat={self.satellite_id}, station={self.station_id}, {self.data_volume_gb:.2f}GB)"


@dataclass
class DownlinkSegment:
    """数传分段
    
    描述分段传输中的一个数据段。
    
    Attributes:
        segment_id: 分段标识
        parent_task_id: 父任务ID（关联的成像任务）
        sequence_number: 分段序号（从1开始）
        total_segments: 总分段数
        data_volume_gb: 本段数据量 (GB)
        data_offset_gb: 数据偏移量 (GB)，从0开始
    """
    segment_id: str
    parent_task_id: str
    sequence_number: int
    total_segments: int
    data_volume_gb: float
    data_offset_gb: float = 0.0
    
    @property
    def is_first_segment(self) -> bool:
        return self.sequence_number == 1
    
    @property
    def is_last_segment(self) -> bool:
        return self.sequence_number == self.total_segments
    
    def __repr__(self) -> str:
        return f"DownlinkSegment({self.segment_id}, {self.sequence_number}/{self.total_segments}, {self.data_volume_gb:.2f}GB)"


@dataclass
class SegmentedDownlinkAction(DownlinkAction):
    """分段数传动作
    
    描述分段传输模式下的数传动作，继承自 DownlinkAction。
    
    Attributes:
        segment: 关联的分段信息
        segment_overhead_sec: 分段切换开销 (秒)
    """
    segment: Optional[DownlinkSegment] = None
    segment_overhead_sec: float = 0.0
    
    def __repr__(self) -> str:
        seg_info = f", seg {self.segment.sequence_number}/{self.segment.total_segments}" if self.segment else ""
        return f"SegmentedDownlinkAction({self.id}, sat={self.satellite_id}{seg_info}, {self.data_volume_gb:.2f}GB)"


@dataclass
class DownlinkPlan:
    """数传计划
    
    描述一个完整的数据下传计划，可能包含单个动作或多个分段动作。
    
    Attributes:
        plan_id: 计划标识
        satellite_id: 卫星ID
        task_id: 关联的成像任务ID
        total_data_gb: 总数据量 (GB)
        actions: 数传动作列表
        is_segmented: 是否为分段传输
        is_aggregated: 是否使用多天线聚合
    """
    plan_id: str
    satellite_id: str
    task_id: str
    total_data_gb: float
    actions: List[DownlinkAction] = field(default_factory=list)
    is_segmented: bool = False
    is_aggregated: bool = False
    
    @property
    def num_actions(self) -> int:
        return len(self.actions)
    
    @property
    def total_duration_sec(self) -> float:
        return sum(a.duration_sec for a in self.actions)
    
    @property
    def completed_data_gb(self) -> float:
        return sum(a.data_volume_gb for a in self.actions)
    
    @property
    def is_complete(self) -> bool:
        """数据是否全部传输完成"""
        return abs(self.completed_data_gb - self.total_data_gb) < 0.001
    
    def get_earliest_start(self) -> Optional[str]:
        """获取最早开始时间"""
        if not self.actions:
            return None
        return min(a.start_time for a in self.actions)
    
    def get_latest_end(self) -> Optional[str]:
        """获取最晚结束时间"""
        if not self.actions:
            return None
        return max(a.end_time for a in self.actions)
    
    def __repr__(self) -> str:
        mode = []
        if self.is_segmented:
            mode.append("segmented")
        if self.is_aggregated:
            mode.append("aggregated")
        mode_str = f", mode=[{','.join(mode)}]" if mode else ""
        return f"DownlinkPlan({self.plan_id}, sat={self.satellite_id}, {self.total_data_gb:.2f}GB, {self.num_actions} actions{mode_str})"

