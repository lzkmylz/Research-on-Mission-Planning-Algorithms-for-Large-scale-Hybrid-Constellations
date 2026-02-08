# -*- coding: utf-8 -*-
"""
动作转换时间约束

检查连续动作之间的最小转换时间是否满足要求。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union

from .checker import BaseConstraint, ConstraintViolation
from ..models.observation import ObservationWindow
from ..models.satellite import Satellite
from ..models.uplink import DownlinkAction


def parse_time(time_str: str) -> datetime:
    """解析ISO格式时间字符串"""
    return datetime.fromisoformat(time_str.replace("Z", "+00:00"))


def time_gap_seconds(end_time: str, start_time: str) -> float:
    """计算两个时间点之间的间隔（秒）"""
    end_dt = parse_time(end_time)
    start_dt = parse_time(start_time)
    return (start_dt - end_dt).total_seconds()


@dataclass
class TransitionViolation:
    """转换时间违规详情"""
    constraint_type: str
    action1_id: str
    action2_id: str
    required_gap: float
    actual_gap: float
    message: str


class ActionTransitionConstraint(BaseConstraint):
    """动作转换时间约束
    
    检查连续动作之间的最小转换时间：
    1. 成像-成像转换：同一卫星连续成像动作间的最小转换时间
    2. 成像-数传转换：成像动作与数传动作间的最小转换时间
    3. 同星多站转换：同一卫星对不同地面站数传动作间的最小转换时间
    """
    
    def __init__(
        self,
        default_imaging_switch_time: float = 5.0,
        default_imaging_to_downlink_time: float = 10.0,
        default_downlink_switch_time: float = 3.0,
        enabled: bool = True
    ):
        super().__init__(enabled=enabled)
        self.default_imaging_switch_time = default_imaging_switch_time
        self.default_imaging_to_downlink_time = default_imaging_to_downlink_time
        self.default_downlink_switch_time = default_downlink_switch_time
    
    def _check_impl(
        self,
        observation: ObservationWindow,
        **kwargs
    ) -> Optional[ConstraintViolation]:
        # 基类方法，保持兼容性
        return None
    
    def check_imaging_sequence(
        self,
        observations: List[ObservationWindow],
        satellite: Satellite
    ) -> List[TransitionViolation]:
        """检查成像序列的转换时间约束
        
        Args:
            observations: 同一卫星的观测序列（按时间排序）
            satellite: 执行观测的卫星
            
        Returns:
            违规列表
        """
        if not self.enabled or len(observations) < 2:
            return []
        
        violations = []
        min_gap = satellite.get_imaging_switch_time()
        
        # 按开始时间排序
        sorted_obs = sorted(observations, key=lambda x: x.start_time)
        
        for i in range(1, len(sorted_obs)):
            prev_obs = sorted_obs[i - 1]
            curr_obs = sorted_obs[i]
            
            # 计算时间间隔
            gap = time_gap_seconds(prev_obs.end_time, curr_obs.start_time)
            
            if gap < min_gap:
                violations.append(TransitionViolation(
                    constraint_type="imaging_switch",
                    action1_id=prev_obs.id,
                    action2_id=curr_obs.id,
                    required_gap=min_gap,
                    actual_gap=gap,
                    message=f"成像转换时间不足: {gap:.1f}s < {min_gap:.1f}s"
                ))
        
        return violations
    
    def check_imaging_to_downlink(
        self,
        last_imaging: ObservationWindow,
        first_downlink: DownlinkAction,
        satellite: Satellite
    ) -> Optional[TransitionViolation]:
        """检查成像到数传的转换时间
        
        Args:
            last_imaging: 最后一个成像动作
            first_downlink: 第一个数传动作
            satellite: 卫星
            
        Returns:
            违规记录或 None
        """
        if not self.enabled:
            return None
        
        min_gap = satellite.get_imaging_to_downlink_time()
        gap = time_gap_seconds(last_imaging.end_time, first_downlink.start_time)
        
        if gap < min_gap:
            return TransitionViolation(
                constraint_type="imaging_to_downlink",
                action1_id=last_imaging.id,
                action2_id=first_downlink.id,
                required_gap=min_gap,
                actual_gap=gap,
                message=f"成像-数传转换时间不足: {gap:.1f}s < {min_gap:.1f}s"
            )
        
        return None
    
    def check_downlink_sequence(
        self,
        downlinks: List[DownlinkAction],
        satellite: Satellite
    ) -> List[TransitionViolation]:
        """检查同一卫星数传序列的转换时间（对不同站）
        
        Args:
            downlinks: 同一卫星的数传动作序列
            satellite: 卫星
            
        Returns:
            违规列表
        """
        if not self.enabled or len(downlinks) < 2:
            return []
        
        violations = []
        min_gap = satellite.get_downlink_switch_time()
        
        # 按开始时间排序
        sorted_downlinks = sorted(downlinks, key=lambda x: x.start_time)
        
        for i in range(1, len(sorted_downlinks)):
            prev = sorted_downlinks[i - 1]
            curr = sorted_downlinks[i]
            
            # 只检查不同站的情况
            if prev.station_id != curr.station_id:
                gap = time_gap_seconds(prev.end_time, curr.start_time)
                
                if gap < min_gap:
                    violations.append(TransitionViolation(
                        constraint_type="downlink_switch",
                        action1_id=prev.id,
                        action2_id=curr.id,
                        required_gap=min_gap,
                        actual_gap=gap,
                        message=f"数传站切换时间不足: {gap:.1f}s < {min_gap:.1f}s"
                    ))
        
        return violations
    
    def check_all_transitions(
        self,
        satellite: Satellite,
        observations: List[ObservationWindow],
        downlinks: List[DownlinkAction]
    ) -> List[TransitionViolation]:
        """检查卫星所有动作的转换时间约束
        
        Args:
            satellite: 卫星
            observations: 成像观测列表
            downlinks: 数传动作列表
            
        Returns:
            所有违规列表
        """
        violations = []
        
        # 1. 检查成像序列
        violations.extend(self.check_imaging_sequence(observations, satellite))
        
        # 2. 检查数传序列
        violations.extend(self.check_downlink_sequence(downlinks, satellite))
        
        # 3. 检查成像-数传转换
        if observations and downlinks:
            sorted_obs = sorted(observations, key=lambda x: x.end_time)
            sorted_dl = sorted(downlinks, key=lambda x: x.start_time)
            
            # 找最后一个成像和第一个数传
            last_imaging = sorted_obs[-1]
            first_downlink = sorted_dl[0]
            
            # 只有当数传在成像之后才检查
            if time_gap_seconds(last_imaging.end_time, first_downlink.start_time) > 0:
                violation = self.check_imaging_to_downlink(
                    last_imaging, first_downlink, satellite
                )
                if violation:
                    violations.append(violation)
        
        return violations
