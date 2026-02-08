# -*- coding: utf-8 -*-
"""核心数据模型"""

from .satellite import Satellite, SatelliteType
from .sensor import Sensor, ImagingMode
from .target import (
    TargetType,
    PointTarget,
    GridTarget,
    MovingTarget,
    WaypointPath,
    AreaTarget,
)
from .ground_station import GroundStation, DownlinkWindow
from .observation import ObservationWindow, ImagingTask

# 新增模型
from .imaging_mode import (
    ImagingMode as ImagingModeConfig,  # 避免与 sensor.ImagingMode 冲突
    OPTICAL_STRIP_MODE, OPTICAL_STARE_MODE, OPTICAL_AREA_MODE,
    SAR_SPOTLIGHT_MODE, SAR_STRIPMAP_MODE, SAR_SLIDING_SPOTLIGHT_MODE, SAR_SCANSAR_MODE,
)
from .satellite_type import (
    SatelliteTypeConfig,
    UHR_OPTICAL_TYPE, HR_OPTICAL_TYPE, UHR_SAR_TYPE, HR_SAR_TYPE,
    SATELLITE_TYPE_REGISTRY,
    get_satellite_type_config,
)
from .antenna import Antenna
from .ttc_station import TTCStation, DownlinkWindow as TTCDownlinkWindow, create_default_ttc_stations
from .uplink import (
    UplinkAction, 
    UplinkRequest, 
    DownlinkAction,
    DownlinkSegment,
    SegmentedDownlinkAction,
    DownlinkPlan,
)

__all__ = [
    # 卫星
    "Satellite",
    "SatelliteType",
    # 传感器
    "Sensor",
    "ImagingMode",
    # 目标
    "TargetType",
    "PointTarget",
    "GridTarget",
    "MovingTarget",
    "WaypointPath",
    "AreaTarget",
    # 地面站（原有）
    "GroundStation",
    "DownlinkWindow",
    # 观测
    "ObservationWindow",
    "ImagingTask",
    # 新增：成像模式配置
    "ImagingModeConfig",
    "OPTICAL_STRIP_MODE",
    "OPTICAL_STARE_MODE",
    "OPTICAL_AREA_MODE",
    "SAR_SPOTLIGHT_MODE",
    "SAR_STRIPMAP_MODE",
    "SAR_SLIDING_SPOTLIGHT_MODE",
    "SAR_SCANSAR_MODE",
    # 新增：卫星型号配置
    "SatelliteTypeConfig",
    "UHR_OPTICAL_TYPE",
    "HR_OPTICAL_TYPE",
    "UHR_SAR_TYPE",
    "HR_SAR_TYPE",
    "SATELLITE_TYPE_REGISTRY",
    "get_satellite_type_config",
    # 新增：天线
    "Antenna",
    # 新增：测控数传站
    "TTCStation",
    "TTCDownlinkWindow",
    "create_default_ttc_stations",
    # 新增：上注和数传动作
    "UplinkAction",
    "UplinkRequest",
    "DownlinkAction",
    # 新增：分段传输
    "DownlinkSegment",
    "SegmentedDownlinkAction",
    "DownlinkPlan",
]

