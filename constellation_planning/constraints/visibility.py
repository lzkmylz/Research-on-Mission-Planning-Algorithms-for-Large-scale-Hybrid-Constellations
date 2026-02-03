# -*- coding: utf-8 -*-
"""可见性约束"""

from typing import Optional
from .checker import BaseConstraint, ConstraintViolation
from ..models.observation import ObservationWindow


class VisibilityConstraint(BaseConstraint):
    """可见性约束 - 检查观测窗口是否可行"""
    
    def __init__(
        self,
        min_elevation_deg: float = 10.0,
        max_off_nadir_deg: float = 45.0,
        enabled: bool = True
    ):
        super().__init__(enabled=enabled)
        self.min_elevation_deg = min_elevation_deg
        self.max_off_nadir_deg = max_off_nadir_deg
    
    def _check_impl(
        self,
        observation: ObservationWindow,
        **kwargs
    ) -> Optional[ConstraintViolation]:
        # 检查离轴角
        if observation.off_nadir_deg > self.max_off_nadir_deg:
            return ConstraintViolation(
                constraint_type="visibility",
                observation_id=observation.id,
                message=f"离轴角 {observation.off_nadir_deg:.1f}° 超过限制 {self.max_off_nadir_deg}°"
            )
        return None
