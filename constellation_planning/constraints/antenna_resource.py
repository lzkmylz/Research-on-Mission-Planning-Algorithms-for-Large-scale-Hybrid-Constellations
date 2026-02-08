# -*- coding: utf-8 -*-
"""
天线资源约束

确保同一天线同时刻只服务一颗卫星，并检查同一天线服务不同卫星时的转换时间。
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union

from .checker import BaseConstraint, ConstraintViolation
from ..models.antenna import Antenna
from ..models.uplink import UplinkAction, DownlinkAction


def parse_time(time_str: str) -> datetime:
    """解析ISO格式时间字符串"""
    return datetime.fromisoformat(time_str.replace("Z", "+00:00"))


def time_gap_seconds(end_time: str, start_time: str) -> float:
    """计算两个时间点之间的间隔（秒）"""
    end_dt = parse_time(end_time)
    start_dt = parse_time(start_time)
    return (start_dt - end_dt).total_seconds()


def time_overlaps(start1: str, end1: str, start2: str, end2: str) -> bool:
    """检查两个时间段是否重叠"""
    s1, e1 = parse_time(start1), parse_time(end1)
    s2, e2 = parse_time(start2), parse_time(end2)
    return not (e1 <= s2 or e2 <= s1)


@dataclass
class AntennaAction:
    """天线动作的统一表示"""
    id: str
    action_type: str  # "uplink" | "downlink"
    satellite_id: str
    antenna_id: str
    start_time: str
    end_time: str
    
    @classmethod
    def from_uplink(cls, action: UplinkAction) -> "AntennaAction":
        return cls(
            id=action.id,
            action_type="uplink",
            satellite_id=action.satellite_id,
            antenna_id=action.antenna_id,
            start_time=action.start_time,
            end_time=action.end_time,
        )
    
    @classmethod
    def from_downlink(cls, action: DownlinkAction) -> "AntennaAction":
        return cls(
            id=action.id,
            action_type="downlink",
            satellite_id=action.satellite_id,
            antenna_id=action.antenna_id,
            start_time=action.start_time,
            end_time=action.end_time,
        )


@dataclass
class AntennaViolation:
    """天线约束违规详情"""
    violation_type: str  # "conflict" | "switch_time"
    antenna_id: str
    action1_id: str
    action2_id: str
    message: str
    required_gap: Optional[float] = None
    actual_gap: Optional[float] = None


class AntennaResourceConstraint(BaseConstraint):
    """天线资源互斥约束
    
    确保：
    1. 同一天线同时刻只能服务一颗卫星
    2. 同一天线服务不同卫星时满足最小转换时间
    """
    
    def __init__(
        self,
        enabled: bool = True
    ):
        super().__init__(enabled=enabled)
    
    def _check_impl(self, observation, **kwargs) -> Optional[ConstraintViolation]:
        # 基类方法，保持兼容性
        return None
    
    def check_antenna_schedule(
        self,
        antenna: Antenna,
        actions: List[AntennaAction]
    ) -> List[AntennaViolation]:
        """检查单个天线的调度冲突和转换时间
        
        Args:
            antenna: 天线对象
            actions: 该天线上调度的所有动作
            
        Returns:
            违规列表
        """
        if not self.enabled or len(actions) < 2:
            return []
        
        violations = []
        
        # 按开始时间排序
        sorted_actions = sorted(actions, key=lambda x: x.start_time)
        
        for i in range(1, len(sorted_actions)):
            prev = sorted_actions[i - 1]
            curr = sorted_actions[i]
            
            # 检查时间重叠（冲突）
            if time_overlaps(prev.start_time, prev.end_time, 
                            curr.start_time, curr.end_time):
                violations.append(AntennaViolation(
                    violation_type="conflict",
                    antenna_id=antenna.id,
                    action1_id=prev.id,
                    action2_id=curr.id,
                    message=f"天线{antenna.id}时间冲突: {prev.id} 与 {curr.id} 重叠"
                ))
                continue  # 冲突时跳过转换时间检查
            
            # 检查转换时间（仅当服务不同卫星时）
            if prev.satellite_id != curr.satellite_id:
                gap = time_gap_seconds(prev.end_time, curr.start_time)
                min_gap = antenna.satellite_switch_time
                
                if gap < min_gap:
                    violations.append(AntennaViolation(
                        violation_type="switch_time",
                        antenna_id=antenna.id,
                        action1_id=prev.id,
                        action2_id=curr.id,
                        required_gap=min_gap,
                        actual_gap=gap,
                        message=f"天线{antenna.id}卫星切换时间不足: {gap:.1f}s < {min_gap:.1f}s"
                    ))
        
        return violations
    
    def check_all_antennas(
        self,
        antenna_actions: Dict[str, List[AntennaAction]],
        antennas: Dict[str, Antenna]
    ) -> Dict[str, List[AntennaViolation]]:
        """检查所有天线的调度约束
        
        Args:
            antenna_actions: 按天线ID分组的动作列表
            antennas: 天线ID到天线对象的映射
            
        Returns:
            按天线ID分组的违规列表
        """
        result = {}
        
        for antenna_id, actions in antenna_actions.items():
            antenna = antennas.get(antenna_id)
            if antenna is None:
                continue
            
            violations = self.check_antenna_schedule(antenna, actions)
            if violations:
                result[antenna_id] = violations
        
        return result
    
    def group_actions_by_antenna(
        self,
        uplinks: List[UplinkAction],
        downlinks: List[DownlinkAction]
    ) -> Dict[str, List[AntennaAction]]:
        """将上注和数传动作按天线分组
        
        Args:
            uplinks: 上注动作列表
            downlinks: 数传动作列表
            
        Returns:
            按天线ID分组的动作列表
        """
        grouped: Dict[str, List[AntennaAction]] = {}
        
        for uplink in uplinks:
            action = AntennaAction.from_uplink(uplink)
            if action.antenna_id not in grouped:
                grouped[action.antenna_id] = []
            grouped[action.antenna_id].append(action)
        
        for downlink in downlinks:
            action = AntennaAction.from_downlink(downlink)
            if action.antenna_id not in grouped:
                grouped[action.antenna_id] = []
            grouped[action.antenna_id].append(action)
        
        return grouped
    
    def check_schedule(
        self,
        uplinks: List[UplinkAction],
        downlinks: List[DownlinkAction],
        antennas: Dict[str, Antenna]
    ) -> Dict[str, List[AntennaViolation]]:
        """检查完整调度的天线约束
        
        便捷方法，整合分组和检查。
        
        Args:
            uplinks: 上注动作列表
            downlinks: 数传动作列表
            antennas: 天线映射
            
        Returns:
            违规结果
        """
        grouped = self.group_actions_by_antenna(uplinks, downlinks)
        return self.check_all_antennas(grouped, antennas)
