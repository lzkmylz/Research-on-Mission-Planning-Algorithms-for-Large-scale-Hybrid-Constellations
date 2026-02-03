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
    # 地面站
    "GroundStation",
    "DownlinkWindow",
    # 观测
    "ObservationWindow",
    "ImagingTask",
]
