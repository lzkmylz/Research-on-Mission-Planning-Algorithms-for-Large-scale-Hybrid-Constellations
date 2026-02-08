# -*- coding: utf-8 -*-
"""
卫星型号配置

定义不同型号卫星的能力参数，包括转换时间、数传能力、能源、存储、机动能力等。
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .imaging_mode import (
    ImagingMode,
    OPTICAL_STRIP_MODE, OPTICAL_STARE_MODE, OPTICAL_AREA_MODE,
    SAR_SPOTLIGHT_MODE, SAR_STRIPMAP_MODE, SAR_SLIDING_SPOTLIGHT_MODE, SAR_SCANSAR_MODE
)


@dataclass
class SatelliteTypeConfig:
    """卫星型号配置
    
    定义特定型号卫星的所有能力参数。
    
    Attributes:
        id: 型号标识，如 "UHR_OPTICAL", "HR_SAR"
        name: 型号名称，如 "超高分辨率光学"
        category: 类别 "optical" | "sar"
    """
    id: str
    name: str
    category: str  # "optical" | "sar"
    
    # === 转换时间配置（秒）===
    imaging_switch_time: float = 5.0        # 成像-成像转换时间
    imaging_to_downlink_time: float = 10.0  # 成像-数传转换时间
    downlink_switch_time: float = 3.0       # 同一卫星对不同站的数传转换时间
    
    # === 成像模式 ===
    imaging_modes: Dict[str, ImagingMode] = field(default_factory=dict)
    default_imaging_mode: str = "strip"
    
    # === 数传能力 ===
    antenna_types: List[str] = field(default_factory=lambda: ["X"])  # 支持的天线类型
    max_downlink_rate_mbps: float = 800.0     # 最大下行速率 (Mbps)
    multi_antenna_capable: bool = False       # 是否支持多天线聚合
    segmented_downlink_capable: bool = False  # 是否支持分段传输
    segment_overhead_sec: float = 2.0         # 分段传输开销 (秒)
    
    # === 能源能力 ===
    battery_capacity_wh: float = 5000.0       # 电池容量 (Wh)
    solar_panel_power_w: float = 2000.0       # 太阳能板功率 (W)
    imaging_power_w: float = 500.0            # 成像平均功耗 (W)
    downlink_power_w: float = 300.0           # 数传功耗 (W)
    idle_power_w: float = 100.0               # 待机功耗 (W)
    
    # === 存储能力 ===
    storage_capacity_gb: float = 2000.0       # 存储容量 (GB)
    
    # === 机动能力 ===
    max_slew_rate_deg_s: float = 3.0          # 最大姿态机动速率 (°/s)
    agile_imaging: bool = True                # 是否支持敏捷成像
    max_off_nadir_deg: float = 45.0           # 最大侧摆角 (°)
    
    def get_imaging_mode(self, mode_id: str) -> Optional[ImagingMode]:
        """获取指定的成像模式"""
        return self.imaging_modes.get(mode_id)
    
    def calculate_data_volume(
        self, 
        imaging_duration_sec: float,
        mode_id: Optional[str] = None
    ) -> float:
        """计算成像产生的数据量 (GB)
        
        Args:
            imaging_duration_sec: 成像持续时间 (秒)
            mode_id: 成像模式ID，默认使用 default_imaging_mode
            
        Returns:
            数据量 (GB)
        """
        mode_id = mode_id or self.default_imaging_mode
        mode = self.get_imaging_mode(mode_id)
        if mode is None:
            raise ValueError(f"未知的成像模式: {mode_id}")
        return mode.calculate_data_volume(imaging_duration_sec)
    
    def calculate_imaging_power(self, mode_id: Optional[str] = None) -> float:
        """获取指定成像模式的功耗 (W)"""
        mode_id = mode_id or self.default_imaging_mode
        mode = self.get_imaging_mode(mode_id)
        if mode is None:
            return self.imaging_power_w
        return mode.power_consumption_w
    
    def __repr__(self) -> str:
        return f"SatelliteTypeConfig({self.id}, {self.name}, {self.category})"


# ============================================================
# 预定义的卫星型号
# ============================================================

# 超高分辨率光学卫星
UHR_OPTICAL_TYPE = SatelliteTypeConfig(
    id="UHR_OPTICAL",
    name="超高分辨率光学",
    category="optical",
    imaging_switch_time=8.0,
    imaging_to_downlink_time=15.0,
    downlink_switch_time=5.0,
    imaging_modes={
        "strip": OPTICAL_STRIP_MODE,
        "stare": OPTICAL_STARE_MODE,
        "area": OPTICAL_AREA_MODE,
    },
    default_imaging_mode="strip",
    antenna_types=["X", "Ka"],
    max_downlink_rate_mbps=1200.0,
    multi_antenna_capable=True,
    battery_capacity_wh=8000.0,
    solar_panel_power_w=3000.0,
    storage_capacity_gb=4000.0,
    max_slew_rate_deg_s=4.0,
    max_off_nadir_deg=45.0,
)

# 高分辨率光学卫星
HR_OPTICAL_TYPE = SatelliteTypeConfig(
    id="HR_OPTICAL",
    name="高分辨率光学",
    category="optical",
    imaging_switch_time=5.0,
    imaging_to_downlink_time=10.0,
    downlink_switch_time=3.0,
    imaging_modes={
        "strip": OPTICAL_STRIP_MODE,
        "stare": OPTICAL_STARE_MODE,
        "area": OPTICAL_AREA_MODE,
    },
    default_imaging_mode="strip",
    antenna_types=["X"],
    max_downlink_rate_mbps=800.0,
    multi_antenna_capable=False,
    battery_capacity_wh=5000.0,
    solar_panel_power_w=2000.0,
    storage_capacity_gb=2000.0,
    max_slew_rate_deg_s=3.0,
    max_off_nadir_deg=40.0,
)

# 超高分辨率SAR卫星
UHR_SAR_TYPE = SatelliteTypeConfig(
    id="UHR_SAR",
    name="超高分辨率SAR",
    category="sar",
    imaging_switch_time=10.0,
    imaging_to_downlink_time=20.0,
    downlink_switch_time=5.0,
    imaging_modes={
        "spotlight": SAR_SPOTLIGHT_MODE,
        "stripmap": SAR_STRIPMAP_MODE,
        "sliding_spotlight": SAR_SLIDING_SPOTLIGHT_MODE,
        "scansar": SAR_SCANSAR_MODE,
    },
    default_imaging_mode="spotlight",
    antenna_types=["X", "Ka"],
    max_downlink_rate_mbps=1500.0,
    multi_antenna_capable=True,
    segmented_downlink_capable=True,
    segment_overhead_sec=3.0,
    battery_capacity_wh=10000.0,
    solar_panel_power_w=4000.0,
    imaging_power_w=1000.0,
    storage_capacity_gb=6000.0,
    max_slew_rate_deg_s=2.5,
    max_off_nadir_deg=35.0,
)

# 高分辨率SAR卫星
HR_SAR_TYPE = SatelliteTypeConfig(
    id="HR_SAR",
    name="高分辨率SAR",
    category="sar",
    imaging_switch_time=8.0,
    imaging_to_downlink_time=15.0,
    downlink_switch_time=4.0,
    imaging_modes={
        "spotlight": SAR_SPOTLIGHT_MODE,
        "stripmap": SAR_STRIPMAP_MODE,
        "sliding_spotlight": SAR_SLIDING_SPOTLIGHT_MODE,
        "scansar": SAR_SCANSAR_MODE,
    },
    default_imaging_mode="stripmap",
    antenna_types=["X"],
    max_downlink_rate_mbps=1000.0,
    multi_antenna_capable=False,
    battery_capacity_wh=7000.0,
    solar_panel_power_w=3000.0,
    imaging_power_w=800.0,
    storage_capacity_gb=4000.0,
    max_slew_rate_deg_s=2.0,
    max_off_nadir_deg=30.0,
)

# 型号注册表
SATELLITE_TYPE_REGISTRY: Dict[str, SatelliteTypeConfig] = {
    "UHR_OPTICAL": UHR_OPTICAL_TYPE,
    "HR_OPTICAL": HR_OPTICAL_TYPE,
    "UHR_SAR": UHR_SAR_TYPE,
    "HR_SAR": HR_SAR_TYPE,
}


def get_satellite_type_config(type_id: str) -> Optional[SatelliteTypeConfig]:
    """获取卫星型号配置"""
    return SATELLITE_TYPE_REGISTRY.get(type_id)
