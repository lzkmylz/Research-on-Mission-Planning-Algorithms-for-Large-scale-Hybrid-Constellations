# -*- coding: utf-8 -*-
"""
卫星模型
"""

from dataclasses import dataclass, field
from typing import List, Optional, TYPE_CHECKING
from enum import Enum

if TYPE_CHECKING:
    from .sensor import Sensor
    from .observation import ObservationWindow


class SatelliteType(Enum):
    """卫星类型"""
    OPTICAL = "optical"
    SAR = "sar"


@dataclass
class Satellite:
    """卫星模型"""
    id: str
    name: str
    sat_type: SatelliteType
    
    # 轨道参数
    altitude_km: float
    inclination_deg: float
    raan_deg: float = 0.0           # 升交点赤经
    arg_perigee_deg: float = 0.0    # 近地点幅角
    true_anomaly_deg: float = 0.0   # 真近点角
    
    # 传感器列表
    sensors: List["Sensor"] = field(default_factory=list)
    
    # 机动能力
    max_roll_deg: float = 30.0      # 最大侧摆角
    max_pitch_deg: float = 30.0     # 最大俯仰角
    slew_rate_deg_s: float = 1.0    # 姿态机动速率 (度/秒)
    
    # 同轨多目标成像能力
    max_targets_per_pass: int = 10          # 单轨最大成像目标数
    min_target_interval_sec: float = 30.0   # 目标间最小间隔时间
    
    # 资源约束
    storage_gb: float = 100.0       # 存储容量 (GB)
    current_storage_gb: float = 0.0 # 当前已用存储
    power_capacity_wh: float = 1000.0  # 电池容量 (Wh)
    
    def can_image_sequence(
        self, 
        observations: List["ObservationWindow"]
    ) -> bool:
        """检查是否可在单轨内完成多目标成像序列"""
        if len(observations) > self.max_targets_per_pass:
            return False
        
        # 按时间排序
        sorted_obs = sorted(observations, key=lambda x: x.start_time)
        
        for i in range(1, len(sorted_obs)):
            prev = sorted_obs[i - 1]
            curr = sorted_obs[i]
            
            # 计算时间间隔
            # TODO: 实现时间解析和间隔计算
            # 检查机动时间是否足够
            # 检查累积存储是否超限
            pass
        
        return True
    
    def available_storage(self) -> float:
        """返回可用存储空间 (GB)"""
        return self.storage_gb - self.current_storage_gb
    
    def reset_storage(self) -> None:
        """重置存储状态（数据下传后）"""
        self.current_storage_gb = 0.0
    
    def __repr__(self) -> str:
        return f"Satellite({self.id}, {self.name}, {self.sat_type.value})"
