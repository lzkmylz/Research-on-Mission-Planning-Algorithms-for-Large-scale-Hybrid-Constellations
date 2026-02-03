# -*- coding: utf-8 -*-
"""时效约束"""

from typing import Optional
from datetime import datetime
from .checker import BaseConstraint, ConstraintViolation
from ..models.observation import ObservationWindow


class TimingConstraint(BaseConstraint):
    """时效约束 - 检查成像时间是否在目标要求范围内"""
    
    def _check_impl(
        self,
        observation: ObservationWindow,
        earliest_time: str = None,
        latest_time: str = None,
        **kwargs
    ) -> Optional[ConstraintViolation]:
        if earliest_time is None and latest_time is None:
            return None
        
        obs_start = datetime.fromisoformat(observation.start_time.replace("Z", "+00:00"))
        
        if earliest_time:
            earliest = datetime.fromisoformat(earliest_time.replace("Z", "+00:00"))
            if obs_start < earliest:
                return ConstraintViolation(
                    constraint_type="timing",
                    observation_id=observation.id,
                    message=f"观测时间早于最早要求时间"
                )
        
        if latest_time:
            latest = datetime.fromisoformat(latest_time.replace("Z", "+00:00"))
            if obs_start > latest:
                return ConstraintViolation(
                    constraint_type="timing",
                    observation_id=observation.id,
                    message=f"观测时间晚于最晚要求时间"
                )
        
        return None
