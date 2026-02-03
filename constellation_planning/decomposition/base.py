# -*- coding: utf-8 -*-
"""区域分解策略基类"""

from abc import ABC, abstractmethod
from typing import List, Union
from ..models.target import AreaTarget, PointTarget, GridTarget


class DecompositionStrategy(ABC):
    """区域分解策略抽象基类"""
    
    @abstractmethod
    def decompose(
        self, 
        area: AreaTarget
    ) -> List[Union[PointTarget, GridTarget]]:
        """将区域分解为子目标"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """策略名称"""
        pass
