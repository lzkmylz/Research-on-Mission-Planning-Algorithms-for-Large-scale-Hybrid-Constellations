# -*- coding: utf-8 -*-
"""能源约束"""

from typing import Optional
from .checker import BaseConstraint, ConstraintViolation
from ..models.observation import ObservationWindow


class EnergyConstraint(BaseConstraint):
    """能源约束 - 检查卫星电量是否足够"""
    
    def __init__(self, min_power_reserve_pct: float = 20.0, enabled: bool = True):
        super().__init__(enabled=enabled)
        self.min_power_reserve_pct = min_power_reserve_pct
    
    def _check_impl(
        self,
        observation: ObservationWindow,
        current_power_pct: float = 100.0,
        power_consumption_pct: float = 5.0,
        **kwargs
    ) -> Optional[ConstraintViolation]:
        remaining = current_power_pct - power_consumption_pct
        if remaining < self.min_power_reserve_pct:
            return ConstraintViolation(
                constraint_type="energy",
                observation_id=observation.id,
                message=f"电量不足: 预计剩余 {remaining:.1f}%"
            )
        return None
