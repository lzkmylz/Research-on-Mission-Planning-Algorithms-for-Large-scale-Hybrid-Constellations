# -*- coding: utf-8 -*-
"""调度模块"""

from .ttc_scheduler import (
    TTCActionScheduler,
    UplinkScheduleResult,
    DownlinkScheduleResult,
    ScheduleSlot,
)

from .advanced_downlink import (
    AdvancedDownlinkScheduler,
    AggregatedDownlinkResult,
    SegmentedDownlinkResult,
)

__all__ = [
    # 基础调度器
    "TTCActionScheduler",
    "UplinkScheduleResult",
    "DownlinkScheduleResult",
    "ScheduleSlot",
    # 高级数传调度器
    "AdvancedDownlinkScheduler",
    "AggregatedDownlinkResult",
    "SegmentedDownlinkResult",
]

