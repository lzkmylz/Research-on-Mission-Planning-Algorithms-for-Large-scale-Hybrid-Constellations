# -*- coding: utf-8 -*-
"""云层约束 - 手动设置云层区域"""

from typing import List, Tuple, Optional
from .checker import BaseConstraint, ConstraintViolation
from ..models.observation import ObservationWindow


class CloudConstraint(BaseConstraint):
    """
    云层约束
    通过手动定义多边形区域表示云层覆盖范围
    """
    
    def __init__(
        self, 
        cloud_regions: List[List[Tuple[float, float]]] = None,
        enabled: bool = True
    ):
        """
        初始化云层约束
        
        Args:
            cloud_regions: 云层区域列表，每个区域为多边形顶点 [(lat, lon), ...]
        """
        super().__init__(enabled=enabled)
        self.cloud_regions = cloud_regions or []
    
    def add_region(self, polygon: List[Tuple[float, float]]) -> None:
        """添加云层区域"""
        self.cloud_regions.append(polygon)
    
    def clear_regions(self) -> None:
        """清除所有云层区域"""
        self.cloud_regions = []
    
    def _check_impl(
        self, 
        observation: ObservationWindow, 
        target_lat: float = None,
        target_lon: float = None,
        is_optical: bool = True,
        **kwargs
    ) -> Optional[ConstraintViolation]:
        """检查观测是否被云层遮挡"""
        # SAR 卫星不受云层影响
        if not is_optical:
            return None
        
        if target_lat is None or target_lon is None:
            return None
        
        # 检查目标是否在任一云层区域内
        for region in self.cloud_regions:
            if self._point_in_polygon(target_lat, target_lon, region):
                return ConstraintViolation(
                    constraint_type="cloud",
                    observation_id=observation.id,
                    message=f"目标位置 ({target_lat:.2f}, {target_lon:.2f}) 被云层遮挡",
                    severity=1.0
                )
        
        return None
    
    def _point_in_polygon(
        self, 
        lat: float, 
        lon: float, 
        polygon: List[Tuple[float, float]]
    ) -> bool:
        """射线法判断点是否在多边形内"""
        n = len(polygon)
        inside = False
        j = n - 1
        for i in range(n):
            yi, xi = polygon[i]
            yj, xj = polygon[j]
            if ((yi > lat) != (yj > lat)) and \
               (lon < (xj - xi) * (lat - yi) / (yj - yi) + xi):
                inside = not inside
            j = i
        return inside
