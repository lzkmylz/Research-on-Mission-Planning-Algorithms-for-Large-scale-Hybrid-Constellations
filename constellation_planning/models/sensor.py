# -*- coding: utf-8 -*-
"""
传感器模型
"""

from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ImagingMode(Enum):
    """成像模式"""
    # 光学模式
    PUSHBROOM = "pushbroom"         # 推扫
    AGILE = "agile"                 # 敏捷
    
    # SAR 模式
    STRIPMAP = "stripmap"           # 条带
    SPOTLIGHT = "spotlight"         # 聚束
    SLIDING_SPOTLIGHT = "sliding_spotlight"  # 滑动聚束
    SCANSAR = "scansar"             # 扫描


@dataclass
class Sensor:
    """传感器模型"""
    id: str
    name: str
    mode: ImagingMode
    
    # 几何参数
    fov_cross_track_deg: float      # 跨轨视场角 (度)
    fov_along_track_deg: float      # 顺轨视场角 (度)
    
    # 性能参数
    resolution_m: float             # 分辨率 (米)
    swath_width_km: float           # 幅宽 (公里)
    
    # SAR 专用参数
    min_incidence_deg: Optional[float] = None  # 最小入射角
    max_incidence_deg: Optional[float] = None  # 最大入射角
    
    # 约束参数
    min_sun_elevation_deg: float = 20.0  # 光学最小太阳高度角
    power_consumption_w: float = 100.0   # 成像功耗 (瓦)
    data_rate_mbps: float = 100.0        # 数据生成速率 (Mbps)
    
    def is_optical(self) -> bool:
        """是否为光学传感器"""
        return self.mode in (ImagingMode.PUSHBROOM, ImagingMode.AGILE)
    
    def is_sar(self) -> bool:
        """是否为 SAR 传感器"""
        return self.mode in (
            ImagingMode.STRIPMAP,
            ImagingMode.SPOTLIGHT,
            ImagingMode.SLIDING_SPOTLIGHT,
            ImagingMode.SCANSAR
        )
    
    def data_volume_gb(self, duration_sec: float) -> float:
        """计算成像数据量 (GB)"""
        return (self.data_rate_mbps * duration_sec) / 8 / 1024
    
    def __repr__(self) -> str:
        return f"Sensor({self.id}, {self.name}, {self.mode.value})"
