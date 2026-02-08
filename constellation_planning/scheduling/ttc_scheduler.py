# -*- coding: utf-8 -*-
"""
测控数传调度器

统一调度上注指令和数据下传动作，避免天线资源冲突。
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..models.antenna import Antenna
from ..models.ttc_station import TTCStation
from ..models.uplink import UplinkAction, UplinkRequest, DownlinkAction
from ..models.observation import ObservationWindow


def parse_time(time_str: str) -> datetime:
    """解析ISO格式时间字符串"""
    return datetime.fromisoformat(time_str.replace("Z", "+00:00"))


def format_time(dt: datetime) -> str:
    """格式化为ISO时间字符串"""
    return dt.isoformat().replace("+00:00", "Z")


@dataclass
class UplinkScheduleResult:
    """上注调度结果"""
    success: bool
    uplink_action: Optional[UplinkAction] = None
    message: str = ""


@dataclass
class DownlinkScheduleResult:
    """数传调度结果"""
    success: bool
    downlink_action: Optional[DownlinkAction] = None
    message: str = ""


@dataclass
class ScheduleSlot:
    """调度时隙"""
    antenna_id: str
    start_time: datetime
    end_time: datetime
    action_id: str
    action_type: str  # "uplink" | "downlink"
    satellite_id: str


class TTCActionScheduler:
    """测控数传动作调度器
    
    统一调度上注指令和数据下传动作，确保：
    1. 天线资源不冲突
    2. 满足转换时间约束
    3. 上注优先于数传（必要时）
    """
    
    def __init__(
        self,
        stations: List[TTCStation],
        min_gap_after_uplink_sec: float = 60.0
    ):
        """
        Args:
            stations: 测控数传站列表
            min_gap_after_uplink_sec: 上注完成后到任务开始的最小间隔
        """
        self.stations = {s.id: s for s in stations}
        self.min_gap_after_uplink_sec = min_gap_after_uplink_sec
        
        # 调度状态
        self._scheduled_slots: Dict[str, List[ScheduleSlot]] = {}  # antenna_id -> slots
        self._action_counter = 0
    
    def _generate_action_id(self, prefix: str) -> str:
        """生成唯一的动作ID"""
        self._action_counter += 1
        return f"{prefix}_{self._action_counter:04d}"
    
    def _get_antenna_slots(self, antenna_id: str) -> List[ScheduleSlot]:
        """获取天线已调度的时隙"""
        if antenna_id not in self._scheduled_slots:
            self._scheduled_slots[antenna_id] = []
        return self._scheduled_slots[antenna_id]
    
    def _is_slot_available(
        self,
        antenna: Antenna,
        start_time: datetime,
        end_time: datetime,
        satellite_id: str
    ) -> Tuple[bool, str]:
        """检查时隙是否可用
        
        Returns:
            (是否可用, 原因说明)
        """
        # 检查天线可用时间
        if not antenna.is_available_during(
            format_time(start_time), format_time(end_time)
        ):
            return False, "天线在该时段不可用"
        
        slots = self._get_antenna_slots(antenna.id)
        
        for slot in slots:
            # 检查时间重叠
            if not (end_time <= slot.start_time or start_time >= slot.end_time):
                return False, f"与已调度动作{slot.action_id}时间冲突"
            
            # 检查转换时间
            if slot.satellite_id != satellite_id:
                switch_time = timedelta(seconds=antenna.satellite_switch_time)
                
                # 如果新动作在已有动作之后
                if start_time >= slot.end_time:
                    required_start = slot.end_time + switch_time
                    if start_time < required_start:
                        return False, f"卫星切换时间不足"
                
                # 如果新动作在已有动作之前
                if end_time <= slot.start_time:
                    required_end = slot.start_time - switch_time
                    if end_time > required_end:
                        return False, f"卫星切换时间不足"
        
        return True, "可用"
    
    def _add_slot(self, slot: ScheduleSlot) -> None:
        """添加调度时隙"""
        slots = self._get_antenna_slots(slot.antenna_id)
        slots.append(slot)
        # 保持按开始时间排序
        slots.sort(key=lambda s: s.start_time)
    
    def schedule_uplink(
        self,
        request: UplinkRequest,
        visibility_windows: List[Tuple[str, str, str, str]]  # (station_id, antenna_id, start, end)
    ) -> UplinkScheduleResult:
        """调度上注动作
        
        Args:
            request: 上注请求
            visibility_windows: 可见性窗口列表
            
        Returns:
            调度结果
        """
        # 计算所需上注时长
        for station_id, antenna_id, win_start_str, win_end_str in visibility_windows:
            station = self.stations.get(station_id)
            if station is None:
                continue
            
            antenna = station.get_antenna(antenna_id)
            if antenna is None:
                continue
            
            # 计算上注时长
            uplink_duration = station.calculate_uplink_duration(request.num_tasks)
            
            win_start = parse_time(win_start_str)
            win_end = parse_time(win_end_str)
            latest_deadline = parse_time(request.latest_time)
            
            # 尝试在窗口内找到合适的时隙
            # 策略：尽早完成上注
            earliest_start = max(win_start, parse_time(request.earliest_time))
            required_end = earliest_start + timedelta(seconds=uplink_duration)
            
            # 检查是否能在截止时间前完成
            if required_end > latest_deadline:
                continue
            
            # 检查是否在窗口内
            if required_end > win_end:
                continue
            
            # 检查时隙可用性
            available, reason = self._is_slot_available(
                antenna, earliest_start, required_end, request.satellite_id
            )
            
            if available:
                action_id = self._generate_action_id("UL")
                
                uplink_action = UplinkAction(
                    id=action_id,
                    satellite_id=request.satellite_id,
                    station_id=station_id,
                    antenna_id=antenna_id,
                    start_time=format_time(earliest_start),
                    end_time=format_time(required_end),
                    duration_sec=uplink_duration,
                    task_ids=request.task_ids,
                )
                
                # 添加时隙
                self._add_slot(ScheduleSlot(
                    antenna_id=antenna_id,
                    start_time=earliest_start,
                    end_time=required_end,
                    action_id=action_id,
                    action_type="uplink",
                    satellite_id=request.satellite_id,
                ))
                
                return UplinkScheduleResult(
                    success=True,
                    uplink_action=uplink_action,
                    message=f"成功调度到{station.name} {antenna.name}"
                )
        
        return UplinkScheduleResult(
            success=False,
            message="无法找到可用的上注窗口"
        )
    
    def schedule_downlink(
        self,
        satellite_id: str,
        data_volume_gb: float,
        visibility_windows: List[Tuple[str, str, str, str, float]],  # (station_id, antenna_id, start, end, rate_mbps)
        earliest_time: Optional[str] = None
    ) -> DownlinkScheduleResult:
        """调度数传动作
        
        Args:
            satellite_id: 卫星ID
            data_volume_gb: 需要下传的数据量(GB)
            visibility_windows: 可见性窗口列表
            earliest_time: 最早开始时间（可选）
            
        Returns:
            调度结果
        """
        earliest_dt = parse_time(earliest_time) if earliest_time else None
        
        for station_id, antenna_id, win_start_str, win_end_str, rate_mbps in visibility_windows:
            station = self.stations.get(station_id)
            if station is None:
                continue
            
            antenna = station.get_antenna(antenna_id)
            if antenna is None:
                continue
            
            # 实际速率取天线和卫星能力的较小值
            actual_rate = min(rate_mbps, antenna.max_data_rate_mbps)
            
            # 计算所需时长
            duration_sec = (data_volume_gb * 8 * 1024) / actual_rate
            
            win_start = parse_time(win_start_str)
            win_end = parse_time(win_end_str)
            
            # 确定开始时间
            start_time = win_start
            if earliest_dt and earliest_dt > start_time:
                start_time = earliest_dt
            
            required_end = start_time + timedelta(seconds=duration_sec)
            
            # 检查是否在窗口内
            if required_end > win_end:
                continue
            
            # 检查时隙可用性
            available, reason = self._is_slot_available(
                antenna, start_time, required_end, satellite_id
            )
            
            if available:
                action_id = self._generate_action_id("DL")
                
                downlink_action = DownlinkAction(
                    id=action_id,
                    satellite_id=satellite_id,
                    station_id=station_id,
                    antenna_id=antenna_id,
                    start_time=format_time(start_time),
                    end_time=format_time(required_end),
                    duration_sec=duration_sec,
                    data_volume_gb=data_volume_gb,
                    data_rate_mbps=actual_rate,
                )
                
                # 添加时隙
                self._add_slot(ScheduleSlot(
                    antenna_id=antenna_id,
                    start_time=start_time,
                    end_time=required_end,
                    action_id=action_id,
                    action_type="downlink",
                    satellite_id=satellite_id,
                ))
                
                return DownlinkScheduleResult(
                    success=True,
                    downlink_action=downlink_action,
                    message=f"成功调度到{station.name} {antenna.name}"
                )
        
        return DownlinkScheduleResult(
            success=False,
            message="无法找到可用的数传窗口"
        )
    
    def get_scheduled_actions(self) -> Tuple[List[UplinkAction], List[DownlinkAction]]:
        """获取所有已调度的动作
        
        Returns:
            (上注动作列表, 数传动作列表)
        """
        # 此方法需要额外的状态跟踪，暂时返回空
        # 实际实现时应该维护已调度的动作列表
        return [], []
    
    def clear_schedule(self) -> None:
        """清空调度状态"""
        self._scheduled_slots.clear()
        self._action_counter = 0
    
    def get_antenna_utilization(self, antenna_id: str) -> float:
        """获取天线利用率
        
        Returns:
            利用率（0-1）
        """
        slots = self._get_antenna_slots(antenna_id)
        if not slots:
            return 0.0
        
        total_used = sum(
            (slot.end_time - slot.start_time).total_seconds()
            for slot in slots
        )
        
        # 计算时间跨度
        min_time = min(slot.start_time for slot in slots)
        max_time = max(slot.end_time for slot in slots)
        span = (max_time - min_time).total_seconds()
        
        if span <= 0:
            return 0.0
        
        return total_used / span
