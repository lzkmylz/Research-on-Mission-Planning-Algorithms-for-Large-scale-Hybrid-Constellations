# -*- coding: utf-8 -*-
"""
结果增强器

扩展基准测试结果数据，包含完整的规划执行细节，支持甘特图、资源时间线可视化。
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
from pathlib import Path

from ..models.satellite import Satellite
from ..models.target import PointTarget
from ..models.uplink import (
    DownlinkAction, UplinkAction, DownlinkPlan, SegmentedDownlinkAction
)
from ..models.ttc_station import TTCStation
from ..models.ground_station import GroundStation
from ..scheduling.ttc_scheduler import TTCActionScheduler
from ..scheduling.advanced_downlink import AdvancedDownlinkScheduler
from ..constraints.checker import ConstraintChecker, ConstraintViolation


def parse_time(time_str: str) -> datetime:
    """解析ISO格式时间字符串"""
    return datetime.fromisoformat(time_str.replace("Z", "+00:00"))


def format_time(dt: datetime) -> str:
    """格式化为ISO时间字符串"""
    return dt.isoformat().replace("+00:00", "Z")


@dataclass
class EnhancedObservationRecord:
    """增强的观测记录"""
    target_id: str
    target_latitude: float
    target_longitude: float
    target_priority: int
    satellite_id: str
    satellite_type: str  # UHR_OPTICAL/HR_OPTICAL/UHR_SAR/HR_SAR
    observation_time: str  # ISO 8601
    duration: int  # 秒
    elevation_deg: float
    off_nadir_deg: float
    data_volume_gb: float
    imaging_mode: str
    required_uplink: bool  # 是否需要上注


@dataclass
class DownlinkPlanRecord:
    """数传计划记录"""
    satellite_id: str
    task_id: str
    station_id: str
    station_name: str
    station_latitude: float
    station_longitude: float
    antenna_id: str
    start_time: str
    end_time: str
    duration_sec: float
    data_volume_gb: float
    data_rate_mbps: float
    is_segmented: bool
    is_aggregated: bool
    segment_number: int = 0  # 如果是分段传输
    total_segments: int = 0


@dataclass
class UplinkPlanRecord:
    """上注计划记录"""
    satellite_id: str
    station_id: str
    station_name: str
    antenna_id: str
    start_time: str
    end_time: str
    duration_sec: float
    task_ids: List[str]  # 上注的任务列表
    num_tasks: int


@dataclass
class PayloadEvent:
    """载荷事件"""
    time: str
    event_type: str  # "imaging_start", "imaging_end", "downlink_start", "downlink_end"
    action_id: str
    target_id: Optional[str] = None  # 如果是观测
    station_id: Optional[str] = None  # 如果是数传


@dataclass
class PayloadTimelineRecord:
    """载荷状态时间线"""
    satellite_id: str
    events: List[PayloadEvent] = field(default_factory=list)


@dataclass
class StorageEvent:
    """存储状态事件"""
    time: str
    storage_used_gb: float
    storage_available_gb: float
    storage_usage_pct: float
    event: str  # "imaging", "downlink"


@dataclass
class EnergyEvent:
    """能源状态事件"""
    time: str
    energy_remaining_wh: float
    energy_usage_pct: float
    event: str


@dataclass
class SatelliteResourceTimeline:
    """卫星资源状态时间线"""
    satellite_id: str
    storage_timeline: List[StorageEvent] = field(default_factory=list)
    energy_timeline: List[EnergyEvent] = field(default_factory=list)


@dataclass
class ConstraintViolationRecord:
    """约束违规记录"""
    constraint_type: str  # "transition", "antenna", "uplink", "storage", "energy"
    severity: str  # "error", "warning"
    message: str
    action1_id: Optional[str] = None
    action2_id: Optional[str] = None
    required_gap: Optional[float] = None
    actual_gap: Optional[float] = None


@dataclass
class ConstraintCheckResult:
    """约束检查结果"""
    violations: List[ConstraintViolationRecord] = field(default_factory=list)
    is_feasible: bool = True


@dataclass
class EnhancedResult:
    """增强的规划结果"""
    # 元数据
    metadata: Dict[str, Any] = field(default_factory=dict)

    # 执行信息
    execution: Dict[str, Any] = field(default_factory=dict)

    # 增强的观测记录
    enhanced_observations: List[EnhancedObservationRecord] = field(default_factory=list)

    # 数传计划
    downlink_plans: List[DownlinkPlanRecord] = field(default_factory=list)

    # 上注计划
    uplink_plans: List[UplinkPlanRecord] = field(default_factory=list)

    # 载荷时间线
    payload_timelines: List[PayloadTimelineRecord] = field(default_factory=list)

    # 资源时间线
    resource_timelines: List[SatelliteResourceTimeline] = field(default_factory=list)

    # 约束检查结果
    constraint_check: ConstraintCheckResult = field(default_factory=lambda: ConstraintCheckResult())

    # 性能指标
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "version": "2.0",
            "metadata": self.metadata,
            "execution": self.execution,
            "enhanced_observations": [
                {
                    "target_id": o.target_id,
                    "target_latitude": o.target_latitude,
                    "target_longitude": o.target_longitude,
                    "target_priority": o.target_priority,
                    "satellite_id": o.satellite_id,
                    "satellite_type": o.satellite_type,
                    "observation_time": o.observation_time,
                    "duration": o.duration,
                    "elevation_deg": o.elevation_deg,
                    "off_nadir_deg": o.off_nadir_deg,
                    "data_volume_gb": o.data_volume_gb,
                    "imaging_mode": o.imaging_mode,
                    "required_uplink": o.required_uplink,
                }
                for o in self.enhanced_observations
            ],
            "downlink_plans": [
                {
                    "satellite_id": d.satellite_id,
                    "task_id": d.task_id,
                    "station_id": d.station_id,
                    "station_name": d.station_name,
                    "station_latitude": d.station_latitude,
                    "station_longitude": d.station_longitude,
                    "antenna_id": d.antenna_id,
                    "start_time": d.start_time,
                    "end_time": d.end_time,
                    "duration_sec": d.duration_sec,
                    "data_volume_gb": d.data_volume_gb,
                    "data_rate_mbps": d.data_rate_mbps,
                    "is_segmented": d.is_segmented,
                    "is_aggregated": d.is_aggregated,
                    "segment_number": d.segment_number,
                    "total_segments": d.total_segments,
                }
                for d in self.downlink_plans
            ],
            "uplink_plans": [
                {
                    "satellite_id": u.satellite_id,
                    "station_id": u.station_id,
                    "station_name": u.station_name,
                    "antenna_id": u.antenna_id,
                    "start_time": u.start_time,
                    "end_time": u.end_time,
                    "duration_sec": u.duration_sec,
                    "task_ids": u.task_ids,
                    "num_tasks": u.num_tasks,
                }
                for u in self.uplink_plans
            ],
            "payload_timelines": [
                {
                    "satellite_id": t.satellite_id,
                    "events": [
                        {
                            "time": e.time,
                            "event_type": e.event_type,
                            "action_id": e.action_id,
                            "target_id": e.target_id,
                            "station_id": e.station_id,
                        }
                        for e in t.events
                    ]
                }
                for t in self.payload_timelines
            ],
            "resource_timelines": [
                {
                    "satellite_id": r.satellite_id,
                    "storage_timeline": [
                        {
                            "time": s.time,
                            "storage_used_gb": s.storage_used_gb,
                            "storage_available_gb": s.storage_available_gb,
                            "storage_usage_pct": s.storage_usage_pct,
                            "event": s.event,
                        }
                        for s in r.storage_timeline
                    ],
                    "energy_timeline": [
                        {
                            "time": e.time,
                            "energy_remaining_wh": e.energy_remaining_wh,
                            "energy_usage_pct": e.energy_usage_pct,
                            "event": e.event,
                        }
                        for e in r.energy_timeline
                    ]
                }
                for r in self.resource_timelines
            ],
            "constraint_check": {
                "is_feasible": self.constraint_check.is_feasible,
                "violations": [
                    {
                        "constraint_type": v.constraint_type,
                        "severity": v.severity,
                        "message": v.message,
                        "action1_id": v.action1_id,
                        "action2_id": v.action2_id,
                        "required_gap": v.required_gap,
                        "actual_gap": v.actual_gap,
                    }
                    for v in self.constraint_check.violations
                ]
            },
            "metrics": self.metrics,
        }


class ResultEnhancer:
    """结果增强器

    整合调度器和约束检查器，生成完整的执行计划。
    """

    def __init__(
        self,
        stations: Optional[List[TTCStation]] = None,
        ground_stations: Optional[List[GroundStation]] = None,
        constraint_checker: Optional[ConstraintChecker] = None
    ):
        """
        Args:
            stations: 测控数传站列表
            ground_stations: 地面站列表（用于数传规划）
            constraint_checker: 约束检查器
        """
        self.stations = stations or []
        self.ground_stations = ground_stations or []
        self.constraint_checker = constraint_checker

        # 初始化调度器
        self.ttc_scheduler = TTCActionScheduler(self.stations) if self.stations else None
        self.downlink_scheduler = AdvancedDownlinkScheduler(self.stations) if self.stations else None

        # 地面站映射
        self.gs_map: Dict[str, GroundStation] = {
            gs.id: gs for gs in self.ground_stations
        }

    def enhance_result(
        self,
        base_result: Dict[str, Any],
        observations: List[Any],
        satellites: List[Dict[str, Any]],
        targets: List[Dict[str, Any]],
        scenario_time_window: Optional[Dict[str, str]] = None
    ) -> EnhancedResult:
        """增强基准测试结果

        Args:
            base_result: 基础结果字典
            observations: 观测机会列表
            satellites: 卫星数据列表
            targets: 目标数据列表
            scenario_time_window: 场景时间窗口

        Returns:
            增强的规划结果
        """
        enhanced = EnhancedResult()

        # 复制基础元数据
        enhanced.metadata = base_result.get("metadata", {})
        enhanced.execution = base_result.get("execution", {})
        enhanced.metrics = base_result.get("metrics", {})

        # 构建映射
        sat_map = {s["id"]: s for s in satellites}
        target_map = {t["id"]: t for t in targets}
        obs_map = {getattr(o, "id", str(i)): o for i, o in enumerate(observations)}

        # 生成增强观测记录
        enhanced.enhanced_observations = self._generate_enhanced_observations(
            base_result, observations, sat_map, target_map
        )

        # 生成数传计划（模拟）
        enhanced.downlink_plans = self._generate_downlink_plans(
            enhanced.enhanced_observations, sat_map, scenario_time_window
        )

        # 生成上注计划（模拟）
        enhanced.uplink_plans = self._generate_uplink_plans(
            enhanced.enhanced_observations, sat_map, scenario_time_window
        )

        # 生成载荷时间线
        enhanced.payload_timelines = self._generate_payload_timelines(
            enhanced.enhanced_observations, enhanced.downlink_plans, enhanced.uplink_plans
        )

        # 生成资源时间线
        enhanced.resource_timelines = self._generate_resource_timelines(
            enhanced.enhanced_observations, enhanced.downlink_plans, sat_map
        )

        # 执行约束检查
        enhanced.constraint_check = self._perform_constraint_check(
            enhanced.enhanced_observations, enhanced.downlink_plans, enhanced.uplink_plans
        )

        return enhanced

    def _generate_enhanced_observations(
        self,
        base_result: Dict[str, Any],
        observations: List[Any],
        sat_map: Dict[str, Dict],
        target_map: Dict[str, Dict]
    ) -> List[EnhancedObservationRecord]:
        """生成增强的观测记录"""
        enhanced_list = []

        # 获取基础观测结果
        base_obs = base_result.get("observations", [])

        for obs in base_obs:
            target_id = obs.get("target_id")
            satellite_id = obs.get("satellite_id")

            # 获取目标详情
            target = target_map.get(target_id, {})
            sat = sat_map.get(satellite_id, {})

            # 确定卫星类型
            sat_type = self._get_satellite_type(sat)

            # 确定成像模式
            imaging_mode = self._get_imaging_mode(sat)

            # 计算数据量（基于分辨率和观测时长）
            duration = obs.get("duration", 60)
            resolution_m = sat.get("sensor", {}).get("resolution_m", 1.0)
            data_volume = self._estimate_data_volume(duration, resolution_m)

            # 判断是否需要上注（高优先级或特殊任务）
            priority = target.get("priority", 5)
            required_uplink = priority >= 8

            record = EnhancedObservationRecord(
                target_id=target_id,
                target_latitude=target.get("latitude", 0.0),
                target_longitude=target.get("longitude", 0.0),
                target_priority=priority,
                satellite_id=satellite_id,
                satellite_type=sat_type,
                observation_time=obs.get("observation_time", ""),
                duration=duration,
                elevation_deg=obs.get("elevation_deg", 45.0),
                off_nadir_deg=obs.get("off_nadir_deg", 0.0),
                data_volume_gb=data_volume,
                imaging_mode=imaging_mode,
                required_uplink=required_uplink
            )
            enhanced_list.append(record)

        return enhanced_list

    def _generate_downlink_plans(
        self,
        enhanced_observations: List[EnhancedObservationRecord],
        sat_map: Dict[str, Dict],
        time_window: Optional[Dict[str, str]] = None
    ) -> List[DownlinkPlanRecord]:
        """生成数传计划"""
        downlink_plans = []

        # 按卫星分组观测
        obs_by_sat: Dict[str, List[EnhancedObservationRecord]] = {}
        for obs in enhanced_observations:
            if obs.satellite_id not in obs_by_sat:
                obs_by_sat[obs.satellite_id] = []
            obs_by_sat[obs.satellite_id].append(obs)

        # 为每颗卫星规划数传
        for sat_id, sat_observations in obs_by_sat.items():
            # 计算卫星总数据量
            total_data = sum(o.data_volume_gb for o in sat_observations)

            # 获取卫星信息
            sat = sat_map.get(sat_id, {})

            # 计算每个地面站的可视窗口并规划数传
            for i, gs in enumerate(self.ground_stations):
                # 简化：假设每个地面站都可以在一定时间窗口内接收
                # 实际应该使用STK计算可见性窗口

                # 计算每个观测后的数传时间
                for j, obs in enumerate(sat_observations):
                    # 数传在观测后的一段时间进行
                    obs_time = parse_time(obs.observation_time) if obs.observation_time else datetime.now()
                    downlink_start = obs_time + timedelta(minutes=30 + i * 10 + j * 5)
                    downlink_duration = obs.data_volume_gb * 20  # 简化的传输时间计算
                    downlink_end = downlink_start + timedelta(seconds=downlink_duration)

                    # 数据率计算
                    data_rate_mbps = gs.downlink_rate_mbps if hasattr(gs, 'downlink_rate_mbps') else 400.0

                    record = DownlinkPlanRecord(
                        satellite_id=sat_id,
                        task_id=f"{obs.target_id}_{sat_id}",
                        station_id=gs.id,
                        station_name=gs.name if hasattr(gs, 'name') else gs.id,
                        station_latitude=gs.latitude,
                        station_longitude=gs.longitude,
                        antenna_id=f"{gs.id}_ANT1",
                        start_time=format_time(downlink_start),
                        end_time=format_time(downlink_end),
                        duration_sec=downlink_duration,
                        data_volume_gb=obs.data_volume_gb,
                        data_rate_mbps=data_rate_mbps,
                        is_segmented=False,
                        is_aggregated=False,
                        segment_number=0,
                        total_segments=0
                    )
                    downlink_plans.append(record)

        return downlink_plans

    def _generate_uplink_plans(
        self,
        enhanced_observations: List[EnhancedObservationRecord],
        sat_map: Dict[str, Dict],
        time_window: Optional[Dict[str, str]] = None
    ) -> List[UplinkPlanRecord]:
        """生成上注计划"""
        uplink_plans = []

        # 找出需要上注的观测
        uplink_required_obs = [o for o in enhanced_observations if o.required_uplink]

        # 按卫星分组
        obs_by_sat: Dict[str, List[EnhancedObservationRecord]] = {}
        for obs in uplink_required_obs:
            if obs.satellite_id not in obs_by_sat:
                obs_by_sat[obs.satellite_id] = []
            obs_by_sat[obs.satellite_id].append(obs)

        # 为每颗卫星规划上注
        for sat_id, sat_observations in obs_by_sat.items():
            # 每个地面站上注一部分任务
            for i, gs in enumerate(self.ground_stations[:3]):  # 使用前3个地面站
                if i >= len(sat_observations):
                    break

                # 上注在观测前进行
                obs = sat_observations[i]
                obs_time = parse_time(obs.observation_time) if obs.observation_time else datetime.now()
                uplink_start = obs_time - timedelta(minutes=45)
                uplink_end = obs_time - timedelta(minutes=35)
                uplink_duration = 600  # 10分钟

                task_ids = [obs.target_id]

                record = UplinkPlanRecord(
                    satellite_id=sat_id,
                    station_id=gs.id,
                    station_name=gs.name if hasattr(gs, 'name') else gs.id,
                    antenna_id=f"{gs.id}_ANT1",
                    start_time=format_time(uplink_start),
                    end_time=format_time(uplink_end),
                    duration_sec=uplink_duration,
                    task_ids=task_ids,
                    num_tasks=len(task_ids)
                )
                uplink_plans.append(record)

        return uplink_plans

    def _generate_payload_timelines(
        self,
        enhanced_observations: List[EnhancedObservationRecord],
        downlink_plans: List[DownlinkPlanRecord],
        uplink_plans: List[UplinkPlanRecord]
    ) -> List[PayloadTimelineRecord]:
        """生成载荷时间线"""
        timelines = []

        # 按卫星分组所有事件
        events_by_sat: Dict[str, List[PayloadEvent]] = {}

        # 添加观测事件
        for obs in enhanced_observations:
            sat_id = obs.satellite_id
            if sat_id not in events_by_sat:
                events_by_sat[sat_id] = []

            obs_time = parse_time(obs.observation_time) if obs.observation_time else datetime.now()
            end_time = obs_time + timedelta(seconds=obs.duration)

            # 成像开始
            events_by_sat[sat_id].append(PayloadEvent(
                time=obs.observation_time,
                event_type="imaging_start",
                action_id=f"IMG_{obs.target_id}",
                target_id=obs.target_id
            ))

            # 成像结束
            events_by_sat[sat_id].append(PayloadEvent(
                time=format_time(end_time),
                event_type="imaging_end",
                action_id=f"IMG_{obs.target_id}",
                target_id=obs.target_id
            ))

        # 添加数传事件
        for dl in downlink_plans:
            sat_id = dl.satellite_id
            if sat_id not in events_by_sat:
                events_by_sat[sat_id] = []

            # 数传开始
            events_by_sat[sat_id].append(PayloadEvent(
                time=dl.start_time,
                event_type="downlink_start",
                action_id=dl.task_id,
                station_id=dl.station_id
            ))

            # 数传结束
            events_by_sat[sat_id].append(PayloadEvent(
                time=dl.end_time,
                event_type="downlink_end",
                action_id=dl.task_id,
                station_id=dl.station_id
            ))

        # 添加上注事件
        for ul in uplink_plans:
            sat_id = ul.satellite_id
            if sat_id not in events_by_sat:
                events_by_sat[sat_id] = []

            # 上注开始
            events_by_sat[sat_id].append(PayloadEvent(
                time=ul.start_time,
                event_type="uplink_start",
                action_id=f"UL_{sat_id}_{ul.start_time}",
                station_id=ul.station_id
            ))

            # 上注结束
            events_by_sat[sat_id].append(PayloadEvent(
                time=ul.end_time,
                event_type="uplink_end",
                action_id=f"UL_{sat_id}_{ul.start_time}",
                station_id=ul.station_id
            ))

        # 构建时间线记录
        for sat_id, events in events_by_sat.items():
            # 按时间排序
            events.sort(key=lambda e: e.time)
            timelines.append(PayloadTimelineRecord(
                satellite_id=sat_id,
                events=events
            ))

        return timelines

    def _generate_resource_timelines(
        self,
        enhanced_observations: List[EnhancedObservationRecord],
        downlink_plans: List[DownlinkPlanRecord],
        sat_map: Dict[str, Dict]
    ) -> List[SatelliteResourceTimeline]:
        """生成资源时间线"""
        timelines = []

        # 按卫星分组
        obs_by_sat: Dict[str, List[EnhancedObservationRecord]] = {}
        for obs in enhanced_observations:
            if obs.satellite_id not in obs_by_sat:
                obs_by_sat[obs.satellite_id] = []
            obs_by_sat[obs.satellite_id].append(obs)

        dl_by_sat: Dict[str, List[DownlinkPlanRecord]] = {}
        for dl in downlink_plans:
            if dl.satellite_id not in dl_by_sat:
                dl_by_sat[dl.satellite_id] = []
            dl_by_sat[dl.satellite_id].append(dl)

        all_sat_ids = set(obs_by_sat.keys()) | set(dl_by_sat.keys())

        for sat_id in all_sat_ids:
            sat = sat_map.get(sat_id, {})
            storage_capacity = sat.get("storage_gb", 100.0)
            power_capacity = sat.get("power_capacity_wh", 1000.0)

            storage_timeline = []
            energy_timeline = []

            # 初始化状态
            current_storage = 0.0
            current_energy = power_capacity

            # 收集所有事件
            all_events = []

            # 观测事件（增加存储，消耗能源）
            for obs in obs_by_sat.get(sat_id, []):
                all_events.append((obs.observation_time, "imaging", obs.data_volume_gb))

            # 数传事件（减少存储）
            for dl in dl_by_sat.get(sat_id, []):
                all_events.append((dl.start_time, "downlink", dl.data_volume_gb))

            # 按时间排序
            all_events.sort(key=lambda x: x[0])

            # 初始状态
            if all_events:
                storage_timeline.append(StorageEvent(
                    time=all_events[0][0],
                    storage_used_gb=0.0,
                    storage_available_gb=storage_capacity,
                    storage_usage_pct=0.0,
                    event="initial"
                ))

            # 处理每个事件
            for time_str, event_type, data_vol in all_events:
                if event_type == "imaging":
                    # 增加存储
                    current_storage = min(current_storage + data_vol, storage_capacity)
                    # 消耗能源（简化的能源模型）
                    current_energy -= data_vol * 10  # 每GB消耗10Wh
                elif event_type == "downlink":
                    # 减少存储
                    current_storage = max(current_storage - data_vol, 0.0)
                    # 消耗能源
                    current_energy -= data_vol * 5  # 每GB消耗5Wh

                storage_timeline.append(StorageEvent(
                    time=time_str,
                    storage_used_gb=current_storage,
                    storage_available_gb=storage_capacity - current_storage,
                    storage_usage_pct=(current_storage / storage_capacity * 100) if storage_capacity > 0 else 0.0,
                    event=event_type
                ))

                energy_timeline.append(EnergyEvent(
                    time=time_str,
                    energy_remaining_wh=max(current_energy, 0.0),
                    energy_usage_pct=((power_capacity - current_energy) / power_capacity * 100) if power_capacity > 0 else 0.0,
                    event=event_type
                ))

            timelines.append(SatelliteResourceTimeline(
                satellite_id=sat_id,
                storage_timeline=storage_timeline,
                energy_timeline=energy_timeline
            ))

        return timelines

    def _perform_constraint_check(
        self,
        enhanced_observations: List[EnhancedObservationRecord],
        downlink_plans: List[DownlinkPlanRecord],
        uplink_plans: List[UplinkPlanRecord]
    ) -> ConstraintCheckResult:
        """执行约束检查"""
        result = ConstraintCheckResult()
        violations = []

        # 1. 检查转换时间约束
        # 按卫星分组观测，检查时间间隔
        obs_by_sat: Dict[str, List[EnhancedObservationRecord]] = {}
        for obs in enhanced_observations:
            if obs.satellite_id not in obs_by_sat:
                obs_by_sat[obs.satellite_id] = []
            obs_by_sat[obs.satellite_id].append(obs)

        for sat_id, obs_list in obs_by_sat.items():
            # 按时间排序
            sorted_obs = sorted(obs_list, key=lambda o: o.observation_time)

            # 检查相邻观测的间隔
            for i in range(1, len(sorted_obs)):
                prev_obs = sorted_obs[i-1]
                curr_obs = sorted_obs[i]

                prev_end = parse_time(prev_obs.observation_time) + timedelta(seconds=prev_obs.duration)
                curr_start = parse_time(curr_obs.observation_time)

                gap = (curr_start - prev_end).total_seconds()

                # 假设最小转换时间为30秒
                min_gap = 30.0

                if gap < min_gap:
                    violations.append(ConstraintViolationRecord(
                        constraint_type="transition",
                        severity="error" if gap < 0 else "warning",
                        message=f"卫星{sat_id}的观测间转换时间不足",
                        action1_id=prev_obs.target_id,
                        action2_id=curr_obs.target_id,
                        required_gap=min_gap,
                        actual_gap=gap
                    ))

        # 2. 检查存储约束
        # 简化：检查每个观测的数据量是否超过存储容量
        for obs in enhanced_observations:
            if obs.data_volume_gb > 100.0:  # 假设最大存储100GB
                violations.append(ConstraintViolationRecord(
                    constraint_type="storage",
                    severity="warning",
                    message=f"观测{obs.target_id}的数据量({obs.data_volume_gb:.2f}GB)较大，可能超出存储容量"
                ))

        # 3. 检查天线资源冲突（简化）
        # 检查同一时间同一地面站是否有多个任务
        dl_by_station: Dict[str, List[DownlinkPlanRecord]] = {}
        for dl in downlink_plans:
            if dl.station_id not in dl_by_station:
                dl_by_station[dl.station_id] = []
            dl_by_station[dl.station_id].append(dl)

        for station_id, dl_list in dl_by_station.items():
            sorted_dl = sorted(dl_list, key=lambda d: d.start_time)
            for i in range(1, len(sorted_dl)):
                prev_dl = sorted_dl[i-1]
                curr_dl = sorted_dl[i]

                prev_end = parse_time(prev_dl.end_time)
                curr_start = parse_time(curr_dl.start_time)

                if curr_start < prev_end:
                    violations.append(ConstraintViolationRecord(
                        constraint_type="antenna",
                        severity="error",
                        message=f"地面站{station_id}存在天线时间冲突",
                        action1_id=prev_dl.task_id,
                        action2_id=curr_dl.task_id
                    ))

        result.violations = violations
        result.is_feasible = not any(v.severity == "error" for v in violations)

        return result

    def _get_satellite_type(self, sat: Dict) -> str:
        """获取卫星类型字符串"""
        sat_type = sat.get("type", "optical").lower()
        resolution_m = sat.get("sensor", {}).get("resolution_m", 1.0)

        if "sar" in sat_type:
            if resolution_m <= 1.0:
                return "UHR_SAR"  # 超高分辨率SAR
            else:
                return "HR_SAR"  # 高分辨率SAR
        else:
            if resolution_m <= 1.0:
                return "UHR_OPTICAL"  # 超高分辨率光学
            else:
                return "HR_OPTICAL"  # 高分辨率光学

    def _get_imaging_mode(self, sat: Dict) -> str:
        """获取成像模式"""
        sat_type = sat.get("type", "optical").lower()
        if "sar" in sat_type:
            return "stripmap"  # SAR默认条带模式
        else:
            return "pushbroom"  # 光学默认推扫模式

    def _estimate_data_volume(self, duration_sec: int, resolution_m: float) -> float:
        """估算数据量 (GB)"""
        # 简化的数据量估算
        # 高分辨率产生更多数据
        base_rate = 0.1  # GB/分钟基础速率
        resolution_factor = 10.0 / max(resolution_m, 0.1)  # 分辨率越低，数据量越大
        duration_min = duration_sec / 60.0

        return base_rate * resolution_factor * duration_min


def load_ground_stations(base_dir: str = "benchmark_dataset") -> List[GroundStation]:
    """从文件加载地面站数据"""
    gs_path = Path(base_dir) / "constellation/ground_stations/stations_global.json"

    if not gs_path.exists():
        # 返回默认地面站
        return [
            GroundStation(
                id=f"GS_{i:03d}",
                name=f"Station_{i:03d}",
                latitude=0.0,
                longitude=i * 45.0,
                elevation_m=0,
                min_elevation_deg=5.0,
                uplink_rate_mbps=50.0,
                downlink_rate_mbps=400.0,
                antenna_diameter_m=10.0
            )
            for i in range(8)
        ]

    with open(gs_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    stations = []
    for gs_data in data.get("ground_stations", []):
        stations.append(GroundStation(
            id=gs_data["id"],
            name=gs_data["name"],
            latitude=gs_data["latitude"],
            longitude=gs_data["longitude"],
            elevation_m=gs_data.get("elevation_m", 0),
            min_elevation_deg=gs_data.get("min_elevation_deg", 5.0),
            uplink_rate_mbps=gs_data.get("uplink_rate_mbps", 50.0),
            downlink_rate_mbps=gs_data.get("downlink_rate_mbps", 400.0),
            antenna_diameter_m=gs_data.get("antenna_diameter_m", 10.0)
        ))

    return stations
