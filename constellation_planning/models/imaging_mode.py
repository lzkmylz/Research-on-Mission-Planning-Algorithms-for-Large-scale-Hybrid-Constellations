# -*- coding: utf-8 -*-
"""
成像模式配置

定义不同成像模式的数据生成参数、压缩比、功耗等。
"""

from dataclasses import dataclass


@dataclass
class ImagingMode:
    """成像模式配置
    
    Attributes:
        id: 模式标识，如 "strip", "stare", "spotlight"
        name: 模式名称，如 "条带模式"
        raw_data_rate_gbps: 原始数据生成速率 (Gbps)
        compression_ratio: 压缩比（原始数据量/压缩后数据量）
        startup_overhead_gb: 每次开机的固定数据开销 (GB)
        power_consumption_w: 该模式的功耗 (W)
    """
    id: str
    name: str
    raw_data_rate_gbps: float
    compression_ratio: float = 3.0
    startup_overhead_gb: float = 0.1
    power_consumption_w: float = 500.0
    
    @property
    def effective_data_rate_gbps(self) -> float:
        """压缩后的有效数据速率 (Gbps)"""
        return self.raw_data_rate_gbps / self.compression_ratio
    
    def calculate_data_volume(self, duration_sec: float) -> float:
        """计算成像产生的数据量 (GB)
        
        公式: 总数据量 = 固定开销 + (原始速率 / 压缩比) × 时长 / 8
        
        Args:
            duration_sec: 成像持续时间 (秒)
            
        Returns:
            数据量 (GB)
        """
        # Gbps -> GB: 除以 8
        return self.startup_overhead_gb + \
               (self.effective_data_rate_gbps * duration_sec / 8)
    
    def __repr__(self) -> str:
        return f"ImagingMode({self.id}, rate={self.raw_data_rate_gbps}Gbps, compression={self.compression_ratio})"


# 预定义的常用成像模式
OPTICAL_STRIP_MODE = ImagingMode(
    id="strip",
    name="条带模式",
    raw_data_rate_gbps=4.0,
    compression_ratio=4.0,
    startup_overhead_gb=0.1,
    power_consumption_w=450.0
)

OPTICAL_STARE_MODE = ImagingMode(
    id="stare",
    name="凝视模式",
    raw_data_rate_gbps=2.0,
    compression_ratio=3.0,
    startup_overhead_gb=0.05,
    power_consumption_w=400.0
)

OPTICAL_AREA_MODE = ImagingMode(
    id="area",
    name="区域模式",
    raw_data_rate_gbps=6.0,
    compression_ratio=5.0,
    startup_overhead_gb=0.15,
    power_consumption_w=550.0
)

SAR_SPOTLIGHT_MODE = ImagingMode(
    id="spotlight",
    name="聚束模式",
    raw_data_rate_gbps=3.0,
    compression_ratio=2.5,
    startup_overhead_gb=0.2,
    power_consumption_w=800.0
)

SAR_STRIPMAP_MODE = ImagingMode(
    id="stripmap",
    name="条带模式",
    raw_data_rate_gbps=5.0,
    compression_ratio=3.0,
    startup_overhead_gb=0.15,
    power_consumption_w=700.0
)

SAR_SLIDING_SPOTLIGHT_MODE = ImagingMode(
    id="sliding_spotlight",
    name="滑动聚束模式",
    raw_data_rate_gbps=4.0,
    compression_ratio=2.5,
    startup_overhead_gb=0.18,
    power_consumption_w=750.0
)

SAR_SCANSAR_MODE = ImagingMode(
    id="scansar",
    name="扫描模式",
    raw_data_rate_gbps=8.0,
    compression_ratio=4.0,
    startup_overhead_gb=0.25,
    power_consumption_w=850.0
)
