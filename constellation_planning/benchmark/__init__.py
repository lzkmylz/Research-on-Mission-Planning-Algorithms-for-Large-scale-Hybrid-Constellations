"""
基准测试数据集生成工具包

用于生成标准的测试数据集，包括星座配置、目标任务和地面站配置。
"""

__version__ = "1.0.0"

# 导出结果增强器
from .result_enhancer import (
    ResultEnhancer,
    EnhancedResult,
    EnhancedObservationRecord,
    DownlinkPlanRecord,
    UplinkPlanRecord,
    PayloadTimelineRecord,
    SatelliteResourceTimeline,
    ConstraintCheckResult,
    load_ground_stations,
)
