# -*- coding: utf-8 -*-
"""
高级数传调度器

支持多天线聚合和分段传输的数传调度能力。
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from ..models.antenna import Antenna
from ..models.ttc_station import TTCStation
from ..models.uplink import (
    DownlinkAction, 
    DownlinkSegment, 
    SegmentedDownlinkAction,
    DownlinkPlan,
)
from ..models.satellite_type import SatelliteTypeConfig


def parse_time(time_str: str) -> datetime:
    """解析ISO格式时间字符串"""
    return datetime.fromisoformat(time_str.replace("Z", "+00:00"))


def format_time(dt: datetime) -> str:
    """格式化为ISO时间字符串"""
    return dt.isoformat().replace("+00:00", "Z")


@dataclass
class AggregatedDownlinkResult:
    """多天线聚合数传调度结果"""
    success: bool
    downlink_action: Optional[DownlinkAction] = None
    antenna_ids: List[str] = field(default_factory=list)
    aggregated_rate_mbps: float = 0.0
    message: str = ""


@dataclass
class SegmentedDownlinkResult:
    """分段数传调度结果"""
    success: bool
    plan: Optional[DownlinkPlan] = None
    actions: List[SegmentedDownlinkAction] = field(default_factory=list)
    total_overhead_sec: float = 0.0
    message: str = ""


class AdvancedDownlinkScheduler:
    """高级数传调度器
    
    支持以下高级能力：
    1. 多天线聚合 - 使用同一站点的多个天线并行下传，速率叠加
    2. 分段传输 - 将数据分段，跨站/跨天线依次传输
    """
    
    def __init__(
        self,
        stations: List[TTCStation],
        default_segment_overhead_sec: float = 2.0
    ):
        """
        Args:
            stations: 测控数传站列表
            default_segment_overhead_sec: 默认分段切换开销(秒)
        """
        self.stations = {s.id: s for s in stations}
        self.default_segment_overhead_sec = default_segment_overhead_sec
        
        # 调度状态
        self._scheduled_slots: Dict[str, List[Tuple[datetime, datetime, str]]] = {}  # antenna_id -> [(start, end, action_id)]
        self._action_counter = 0
        self._plan_counter = 0
    
    def _generate_action_id(self, prefix: str) -> str:
        """生成唯一的动作ID"""
        self._action_counter += 1
        return f"{prefix}_{self._action_counter:04d}"
    
    def _generate_plan_id(self) -> str:
        """生成唯一的计划ID"""
        self._plan_counter += 1
        return f"PLAN_{self._plan_counter:04d}"
    
    def _is_antenna_available(
        self,
        antenna: Antenna,
        start_time: datetime,
        end_time: datetime
    ) -> bool:
        """检查天线在指定时段是否可用"""
        # 检查天线自身可用时间
        if not antenna.is_available_during(format_time(start_time), format_time(end_time)):
            return False
        
        # 检查是否与已调度动作冲突
        slots = self._scheduled_slots.get(antenna.id, [])
        for slot_start, slot_end, _ in slots:
            if not (end_time <= slot_start or start_time >= slot_end):
                return False
        
        return True
    
    def _add_slot(self, antenna_id: str, start: datetime, end: datetime, action_id: str):
        """添加调度时隙"""
        if antenna_id not in self._scheduled_slots:
            self._scheduled_slots[antenna_id] = []
        self._scheduled_slots[antenna_id].append((start, end, action_id))
        self._scheduled_slots[antenna_id].sort(key=lambda x: x[0])
    
    def schedule_aggregated_downlink(
        self,
        satellite_id: str,
        data_volume_gb: float,
        station_id: str,
        start_time: str,
        end_time: str,
        satellite_type: Optional[SatelliteTypeConfig] = None,
        max_antennas: int = 4
    ) -> AggregatedDownlinkResult:
        """调度多天线聚合数传
        
        尝试使用同一站点的多个天线并行下传，速率叠加。
        
        Args:
            satellite_id: 卫星ID
            data_volume_gb: 需要下传的数据量(GB)
            station_id: 地面站ID
            start_time: 可见性窗口开始时间
            end_time: 可见性窗口结束时间
            satellite_type: 卫星型号配置（用于检查是否支持多天线聚合）
            max_antennas: 最大使用天线数
            
        Returns:
            聚合数传调度结果
        """
        # 检查卫星是否支持多天线聚合
        if satellite_type and not satellite_type.multi_antenna_capable:
            return AggregatedDownlinkResult(
                success=False,
                message="卫星不支持多天线聚合"
            )
        
        station = self.stations.get(station_id)
        if station is None:
            return AggregatedDownlinkResult(
                success=False,
                message=f"站点{station_id}不存在"
            )
        
        start_dt = parse_time(start_time)
        end_dt = parse_time(end_time)
        window_duration = (end_dt - start_dt).total_seconds()
        
        # 查找可用天线
        available_antennas = []
        for antenna in station.antennas:
            if self._is_antenna_available(antenna, start_dt, end_dt):
                available_antennas.append(antenna)
        
        if not available_antennas:
            return AggregatedDownlinkResult(
                success=False,
                message="无可用天线"
            )
        
        # 按速率排序，优先使用高速率天线
        available_antennas.sort(key=lambda a: a.max_data_rate_mbps, reverse=True)
        
        # 选择天线并计算聚合速率
        selected_antennas = []
        aggregated_rate = 0.0
        
        for antenna in available_antennas[:max_antennas]:
            selected_antennas.append(antenna)
            aggregated_rate += antenna.max_data_rate_mbps
            
            # 检查速率是否足够
            required_duration = (data_volume_gb * 8 * 1024) / aggregated_rate
            if required_duration <= window_duration:
                break
        
        # 计算实际所需时长
        actual_duration = (data_volume_gb * 8 * 1024) / aggregated_rate
        
        if actual_duration > window_duration:
            return AggregatedDownlinkResult(
                success=False,
                message=f"聚合速率{aggregated_rate:.0f}Mbps仍不足以在窗口内完成传输"
            )
        
        # 创建聚合数传动作
        action_id = self._generate_action_id("ADL")
        actual_end = start_dt + timedelta(seconds=actual_duration)
        
        antenna_ids = [a.id for a in selected_antennas]
        
        downlink_action = DownlinkAction(
            id=action_id,
            satellite_id=satellite_id,
            station_id=station_id,
            antenna_id=antenna_ids[0],  # 主天线
            antenna_ids=antenna_ids,
            start_time=format_time(start_dt),
            end_time=format_time(actual_end),
            duration_sec=actual_duration,
            data_volume_gb=data_volume_gb,
            data_rate_mbps=aggregated_rate,
            is_aggregated=True,
        )
        
        # 为所有使用的天线添加时隙
        for antenna_id in antenna_ids:
            self._add_slot(antenna_id, start_dt, actual_end, action_id)
        
        return AggregatedDownlinkResult(
            success=True,
            downlink_action=downlink_action,
            antenna_ids=antenna_ids,
            aggregated_rate_mbps=aggregated_rate,
            message=f"使用{len(antenna_ids)}个天线，聚合速率{aggregated_rate:.0f}Mbps"
        )
    
    def plan_segmented_downlink(
        self,
        satellite_id: str,
        task_id: str,
        data_volume_gb: float,
        visibility_windows: List[Tuple[str, str, str, str, float]],  # (station_id, antenna_id, start, end, rate_mbps)
        satellite_type: Optional[SatelliteTypeConfig] = None,
        max_segments: int = 10
    ) -> SegmentedDownlinkResult:
        """规划分段数传
        
        将数据分段，跨站/跨天线依次传输。
        
        Args:
            satellite_id: 卫星ID
            task_id: 关联的成像任务ID
            data_volume_gb: 总数据量(GB)
            visibility_windows: 可见性窗口列表
            satellite_type: 卫星型号配置
            max_segments: 最大分段数
            
        Returns:
            分段数传调度结果
        """
        # 检查卫星是否支持分段传输
        if satellite_type and not satellite_type.segmented_downlink_capable:
            return SegmentedDownlinkResult(
                success=False,
                message="卫星不支持分段传输"
            )
        
        # 获取分段开销
        segment_overhead = self.default_segment_overhead_sec
        if satellite_type:
            segment_overhead = satellite_type.segment_overhead_sec
        
        # 分析可用窗口
        available_windows = []
        for station_id, antenna_id, start_str, end_str, rate_mbps in visibility_windows:
            station = self.stations.get(station_id)
            if station is None:
                continue
            
            antenna = station.get_antenna(antenna_id)
            if antenna is None:
                continue
            
            start_dt = parse_time(start_str)
            end_dt = parse_time(end_str)
            
            if self._is_antenna_available(antenna, start_dt, end_dt):
                window_duration = (end_dt - start_dt).total_seconds()
                actual_rate = min(rate_mbps, antenna.max_data_rate_mbps)
                max_data = (actual_rate * window_duration) / (8 * 1024)  # GB
                
                available_windows.append({
                    'station_id': station_id,
                    'antenna_id': antenna_id,
                    'antenna': antenna,
                    'start_dt': start_dt,
                    'end_dt': end_dt,
                    'rate_mbps': actual_rate,
                    'max_data_gb': max_data,
                    'duration_sec': window_duration,
                })
        
        if not available_windows:
            return SegmentedDownlinkResult(
                success=False,
                message="无可用传输窗口"
            )
        
        # 按开始时间排序
        available_windows.sort(key=lambda w: w['start_dt'])
        
        # 贪心分配数据到各个窗口
        remaining_data = data_volume_gb
        segments = []
        segment_num = 0
        data_offset = 0.0
        
        for window in available_windows:
            if remaining_data <= 0.001:
                break
            
            if segment_num >= max_segments:
                break
            
            segment_num += 1
            
            # 扣除分段开销（非首段）
            usable_duration = window['duration_sec']
            overhead_for_segment = segment_overhead if segment_num > 1 else 0
            usable_duration -= overhead_for_segment
            
            if usable_duration <= 0:
                continue
            
            # 计算本窗口能传输的数据量
            window_capacity = (window['rate_mbps'] * usable_duration) / (8 * 1024)
            segment_data = min(remaining_data, window_capacity)
            
            # 计算实际传输时长
            actual_duration = (segment_data * 8 * 1024) / window['rate_mbps']
            actual_end = window['start_dt'] + timedelta(seconds=actual_duration + overhead_for_segment)
            
            # 创建分段
            segment = DownlinkSegment(
                segment_id=f"{task_id}_SEG{segment_num:02d}",
                parent_task_id=task_id,
                sequence_number=segment_num,
                total_segments=0,  # 稍后更新
                data_volume_gb=segment_data,
                data_offset_gb=data_offset,
            )
            
            # 创建分段数传动作
            action_id = self._generate_action_id("SDL")
            action = SegmentedDownlinkAction(
                id=action_id,
                satellite_id=satellite_id,
                station_id=window['station_id'],
                antenna_id=window['antenna_id'],
                start_time=format_time(window['start_dt']),
                end_time=format_time(actual_end),
                duration_sec=actual_duration + overhead_for_segment,
                data_volume_gb=segment_data,
                data_rate_mbps=window['rate_mbps'],
                segment=segment,
                segment_overhead_sec=overhead_for_segment,
            )
            
            segments.append((segment, action, window))
            remaining_data -= segment_data
            data_offset += segment_data
            
            # 添加时隙
            self._add_slot(window['antenna_id'], window['start_dt'], actual_end, action_id)
        
        if remaining_data > 0.001:
            return SegmentedDownlinkResult(
                success=False,
                message=f"可用窗口不足以传输全部数据，剩余{remaining_data:.2f}GB"
            )
        
        # 更新分段总数
        total_segments = len(segments)
        actions = []
        for segment, action, _ in segments:
            segment.total_segments = total_segments
            actions.append(action)
        
        # 创建数传计划
        plan = DownlinkPlan(
            plan_id=self._generate_plan_id(),
            satellite_id=satellite_id,
            task_id=task_id,
            total_data_gb=data_volume_gb,
            actions=actions,
            is_segmented=True,
            is_aggregated=False,
        )
        
        total_overhead = sum(a.segment_overhead_sec for a in actions)
        
        return SegmentedDownlinkResult(
            success=True,
            plan=plan,
            actions=actions,
            total_overhead_sec=total_overhead,
            message=f"分{total_segments}段传输，总开销{total_overhead:.1f}秒"
        )
    
    def plan_hybrid_downlink(
        self,
        satellite_id: str,
        task_id: str,
        data_volume_gb: float,
        visibility_windows: List[Tuple[str, str, str, str, float]],
        satellite_type: Optional[SatelliteTypeConfig] = None,
        prefer_aggregation: bool = True
    ) -> DownlinkPlan:
        """规划混合数传
        
        智能选择最优传输策略：
        1. 如果单窗口+聚合能完成，使用聚合
        2. 如果需要多窗口，使用分段传输
        3. 可以组合使用聚合+分段
        
        Args:
            satellite_id: 卫星ID
            task_id: 关联的成像任务ID
            data_volume_gb: 总数据量(GB)
            visibility_windows: 可见性窗口列表
            satellite_type: 卫星型号配置
            prefer_aggregation: 是否优先使用聚合（速度更快但资源占用更多）
            
        Returns:
            数传计划
        """
        plan = DownlinkPlan(
            plan_id=self._generate_plan_id(),
            satellite_id=satellite_id,
            task_id=task_id,
            total_data_gb=data_volume_gb,
        )
        
        # 检查能力
        can_aggregate = satellite_type is None or satellite_type.multi_antenna_capable
        can_segment = satellite_type is None or satellite_type.segmented_downlink_capable
        
        remaining_data = data_volume_gb
        
        # 按站点分组窗口
        windows_by_station: Dict[str, List] = {}
        for window in visibility_windows:
            station_id = window[0]
            if station_id not in windows_by_station:
                windows_by_station[station_id] = []
            windows_by_station[station_id].append(window)
        
        # 策略1：优先尝试单窗口聚合
        if prefer_aggregation and can_aggregate:
            for station_id, windows in windows_by_station.items():
                if remaining_data <= 0.001:
                    break
                
                # 取该站点最早的窗口尝试聚合
                window = windows[0]
                result = self.schedule_aggregated_downlink(
                    satellite_id=satellite_id,
                    data_volume_gb=remaining_data,
                    station_id=station_id,
                    start_time=window[2],
                    end_time=window[3],
                    satellite_type=satellite_type,
                )
                
                if result.success:
                    plan.actions.append(result.downlink_action)
                    plan.is_aggregated = True
                    remaining_data = 0
                    break
        
        # 策略2：分段传输剩余数据
        if remaining_data > 0.001 and can_segment:
            # 重新收集未使用的窗口
            unused_windows = []
            used_times = set()
            for action in plan.actions:
                used_times.add((action.start_time, action.end_time))
            
            for window in visibility_windows:
                if (window[2], window[3]) not in used_times:
                    unused_windows.append(window)
            
            result = self.plan_segmented_downlink(
                satellite_id=satellite_id,
                task_id=task_id,
                data_volume_gb=remaining_data,
                visibility_windows=unused_windows,
                satellite_type=satellite_type,
            )
            
            if result.success:
                plan.actions.extend(result.actions)
                plan.is_segmented = True
                remaining_data = 0
        
        # 更新计划状态
        if plan.actions:
            plan.is_segmented = plan.is_segmented or len(plan.actions) > 1
        
        return plan
    
    def clear_schedule(self) -> None:
        """清空调度状态"""
        self._scheduled_slots.clear()
        self._action_counter = 0
        self._plan_counter = 0
