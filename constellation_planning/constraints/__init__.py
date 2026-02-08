# -*- coding: utf-8 -*-
"""约束模块"""

from .checker import ConstraintChecker, BaseConstraint, ConstraintViolation
from .cloud import CloudConstraint
from .visibility import VisibilityConstraint
from .storage import StorageConstraint
from .timing import TimingConstraint
from .energy import EnergyConstraint
from .downlink import DownlinkConstraint

# 新增约束
from .transition import (
    ActionTransitionConstraint,
    TransitionViolation,
)
from .antenna_resource import (
    AntennaResourceConstraint,
    AntennaAction,
    AntennaViolation,
)
from .uplink_precedence import (
    UplinkPrecedenceConstraint,
    UplinkViolation,
)

__all__ = [
    # 核心
    "ConstraintChecker",
    "BaseConstraint",
    "ConstraintViolation",
    # 原有约束
    "CloudConstraint",
    "VisibilityConstraint",
    "StorageConstraint",
    "TimingConstraint",
    "EnergyConstraint",
    "DownlinkConstraint",
    # 新增：动作转换约束
    "ActionTransitionConstraint",
    "TransitionViolation",
    # 新增：天线资源约束
    "AntennaResourceConstraint",
    "AntennaAction",
    "AntennaViolation",
    # 新增：上注前置约束
    "UplinkPrecedenceConstraint",
    "UplinkViolation",
]

