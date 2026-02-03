# -*- coding: utf-8 -*-
"""
配置数据结构定义
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class SatelliteType(Enum):
    """卫星类型"""
    OPTICAL = "optical"
    SAR = "sar"


class ImagingMode(Enum):
    """成像模式"""
    # 光学模式
    PUSHBROOM = "pushbroom"
    AGILE = "agile"
    # SAR 模式
    STRIPMAP = "stripmap"
    SPOTLIGHT = "spotlight"
    SLIDING_SPOTLIGHT = "sliding_spotlight"
    SCANSAR = "scansar"


@dataclass
class SensorConfig:
    """传感器配置"""
    name: str
    mode: ImagingMode
    fov_cross_track_deg: float = 5.0
    fov_along_track_deg: float = 5.0
    resolution_m: float = 1.0
    swath_width_km: float = 10.0
    min_sun_elevation_deg: float = 20.0
    power_consumption_w: float = 100.0
    # SAR 专用
    min_incidence_deg: Optional[float] = None
    max_incidence_deg: Optional[float] = None


@dataclass
class SatelliteConfig:
    """卫星配置"""
    name: str
    sat_type: SatelliteType
    sensors: List[SensorConfig] = field(default_factory=list)
    
    # 机动能力
    max_roll_deg: float = 30.0
    max_pitch_deg: float = 30.0
    slew_rate_deg_s: float = 1.0
    
    # 同轨多目标能力
    max_targets_per_pass: int = 10
    min_target_interval_sec: float = 30.0
    
    # 资源约束
    storage_gb: float = 100.0
    power_capacity_wh: float = 1000.0


@dataclass
class ConstellationConfig:
    """Walker 星座配置"""
    name: str = "Constellation"
    altitude_km: float = 500.0
    inclination_deg: float = 97.4  # 太阳同步轨道
    num_planes: int = 6
    sats_per_plane: int = 10
    phase_factor: int = 1
    
    # 卫星配置模板（所有卫星使用相同配置）
    satellite_template: Optional[SatelliteConfig] = None
    
    @property
    def total_satellites(self) -> int:
        return self.num_planes * self.sats_per_plane


@dataclass
class GroundStationConfig:
    """地面站配置"""
    name: str
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    min_elevation_deg: float = 5.0
    max_data_rate_mbps: float = 100.0


@dataclass
class PlanningConfig:
    """任务规划配置"""
    # 优化目标权重
    coverage_weight: float = 1.0
    revisit_weight: float = 0.5
    efficiency_weight: float = 0.3
    
    # 约束开关
    enable_cloud_constraint: bool = True
    enable_storage_constraint: bool = True
    enable_energy_constraint: bool = True
    enable_downlink_constraint: bool = True
    
    # 算法配置
    algorithm: str = "genetic"  # tabu, sa, genetic, aco
    max_iterations: int = 1000
    time_limit_sec: float = 300.0
