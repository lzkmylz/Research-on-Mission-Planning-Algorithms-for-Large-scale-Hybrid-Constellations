# -*- coding: utf-8 -*-
"""
上注前置约束

确保成像任务在执行前已完成上注指令的传输。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from .checker import BaseConstraint, ConstraintViolation
from ..models.observation import ObservationWindow
from ..models.uplink import UplinkAction


def parse_time(time_str: str) -> datetime:
    """解析ISO格式时间字符串"""
    return datetime.fromisoformat(time_str.replace("Z", "+00:00"))


def time_gap_seconds(end_time: str, start_time: str) -> float:
    """计算两个时间点之间的间隔（秒）"""
    end_dt = parse_time(end_time)
    start_dt = parse_time(start_time)
    return (start_dt - end_dt).total_seconds()


@dataclass
class UplinkViolation:
    """上注约束违规详情"""
    violation_type: str  # "missing_uplink" | "insufficient_gap"
    task_id: str
    satellite_id: str
    message: str
    uplink_id: Optional[str] = None
    required_gap: Optional[float] = None
    actual_gap: Optional[float] = None


class UplinkPrecedenceConstraint(BaseConstraint):
    """上注前置约束
    
    确保：
    1. 每个成像任务都有对应的前置上注动作
    2. 上注完成后到任务开始有足够的间隔时间
    """
    
    def __init__(
        self,
        min_gap_after_uplink_sec: float = 60.0,
        enabled: bool = True
    ):
        """
        Args:
            min_gap_after_uplink_sec: 上注完成后到任务开始的最小间隔时间（秒）
            enabled: 是否启用约束
        """
        super().__init__(enabled=enabled)
        self.min_gap_after_uplink_sec = min_gap_after_uplink_sec
    
    def _check_impl(
        self,
        observation: ObservationWindow,
        uplink_actions: List[UplinkAction] = None,
        **kwargs
    ) -> Optional[ConstraintViolation]:
        """检查单个观测任务的上注前置约束
        
        Args:
            observation: 观测任务
            uplink_actions: 可用的上注动作列表
            
        Returns:
            约束违规记录或 None
        """
        if uplink_actions is None:
            uplink_actions = []
        
        violation = self._check_single_task(observation, uplink_actions)
        
        if violation:
            return ConstraintViolation(
                constraint_type="uplink_precedence",
                observation_id=observation.id,
                message=violation.message,
                severity=1.0
            )
        
        return None
    
    def _check_single_task(
        self,
        observation: ObservationWindow,
        uplink_actions: List[UplinkAction]
    ) -> Optional[UplinkViolation]:
        """检查单个任务的上注前置约束（返回详细违规信息）"""
        
        # 查找包含此任务的上注动作
        relevant_uplinks = [
            u for u in uplink_actions
            if observation.id in u.task_ids and u.satellite_id == observation.satellite_id
        ]
        
        if not relevant_uplinks:
            return UplinkViolation(
                violation_type="missing_uplink",
                task_id=observation.id,
                satellite_id=observation.satellite_id,
                message=f"任务{observation.id}未找到对应的上注指令"
            )
        
        # 检查时序：上注必须在任务开始前完成，且有足够间隔
        obs_start = parse_time(observation.start_time)
        
        # 找最晚的有效上注（在任务开始前完成的）
        valid_uplinks = []
        for uplink in relevant_uplinks:
            uplink_end = parse_time(uplink.end_time)
            if uplink_end < obs_start:
                valid_uplinks.append(uplink)
        
        if not valid_uplinks:
            return UplinkViolation(
                violation_type="missing_uplink",
                task_id=observation.id,
                satellite_id=observation.satellite_id,
                message=f"任务{observation.id}的上注指令未在任务开始前完成"
            )
        
        # 使用最晚完成的上注
        latest_uplink = max(valid_uplinks, key=lambda u: u.end_time)
        gap = time_gap_seconds(latest_uplink.end_time, observation.start_time)
        
        if gap < self.min_gap_after_uplink_sec:
            return UplinkViolation(
                violation_type="insufficient_gap",
                task_id=observation.id,
                satellite_id=observation.satellite_id,
                uplink_id=latest_uplink.id,
                required_gap=self.min_gap_after_uplink_sec,
                actual_gap=gap,
                message=f"上注后间隔不足: {gap:.1f}s < {self.min_gap_after_uplink_sec:.1f}s"
            )
        
        return None
    
    def check_all_tasks(
        self,
        observations: List[ObservationWindow],
        uplink_actions: List[UplinkAction]
    ) -> List[UplinkViolation]:
        """检查所有任务的上注前置约束
        
        Args:
            observations: 观测任务列表
            uplink_actions: 上注动作列表
            
        Returns:
            违规列表
        """
        if not self.enabled:
            return []
        
        violations = []
        
        for obs in observations:
            violation = self._check_single_task(obs, uplink_actions)
            if violation:
                violations.append(violation)
        
        return violations
    
    def find_required_uplinks(
        self,
        observations: List[ObservationWindow]
    ) -> dict:
        """分析任务列表，找出需要的上注请求
        
        将同一卫星的连续任务分组，生成最优的上注请求建议。
        
        Args:
            observations: 观测任务列表
            
        Returns:
            按卫星ID分组的任务列表，可用于生成上注请求
        """
        # 按卫星分组
        by_satellite = {}
        for obs in observations:
            if obs.satellite_id not in by_satellite:
                by_satellite[obs.satellite_id] = []
            by_satellite[obs.satellite_id].append(obs)
        
        # 按开始时间排序
        for sat_id in by_satellite:
            by_satellite[sat_id].sort(key=lambda x: x.start_time)
        
        return by_satellite
