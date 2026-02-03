# -*- coding: utf-8 -*-
"""存储容量约束"""

from typing import Optional
from .checker import BaseConstraint, ConstraintViolation
from ..models.observation import ObservationWindow
from ..models.satellite import Satellite


class StorageConstraint(BaseConstraint):
    """存储容量约束"""
    
    def _check_impl(
        self,
        observation: ObservationWindow,
        satellite: Satellite = None,
        **kwargs
    ) -> Optional[ConstraintViolation]:
        if satellite is None:
            return None
        
        # 检查存储空间是否足够
        if observation.data_volume_gb > satellite.available_storage():
            return ConstraintViolation(
                constraint_type="storage",
                observation_id=observation.id,
                message=f"存储不足: 需要 {observation.data_volume_gb:.2f}GB, 可用 {satellite.available_storage():.2f}GB"
            )
        return None
