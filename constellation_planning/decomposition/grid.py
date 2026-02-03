# -*- coding: utf-8 -*-
"""网格分解策略"""

from typing import List, Union
from .base import DecompositionStrategy
from ..models.target import AreaTarget, PointTarget, GridTarget


class GridDecomposer(DecompositionStrategy):
    """
    网格分解策略
    将区域按固定网格大小分解
    """
    
    def __init__(self, grid_size_deg: float = 0.1):
        """
        初始化网格分解器
        
        Args:
            grid_size_deg: 网格边长 (度)，默认 0.1°
        """
        self.grid_size_deg = grid_size_deg
    
    def get_name(self) -> str:
        return f"GridDecomposer({self.grid_size_deg}°)"
    
    def decompose(
        self, 
        area: AreaTarget
    ) -> List[GridTarget]:
        """将区域分解为网格目标"""
        grids = []
        
        # 获取边界框
        min_lat, min_lon, max_lat, max_lon = area.bounding_box()
        
        # 生成网格
        grid_id = 0
        lat = min_lat + self.grid_size_deg / 2
        while lat < max_lat:
            lon = min_lon + self.grid_size_deg / 2
            while lon < max_lon:
                # 检查网格中心是否在多边形内
                if self._point_in_polygon(lat, lon, area.polygon):
                    grid = GridTarget(
                        id=f"{area.id}_G{grid_id:04d}",
                        name=f"{area.name}_Grid_{grid_id}",
                        center_lat=lat,
                        center_lon=lon,
                        size_deg=self.grid_size_deg,
                        priority=area.priority,
                    )
                    grids.append(grid)
                    grid_id += 1
                lon += self.grid_size_deg
            lat += self.grid_size_deg
        
        # 更新区域的子目标
        area.sub_targets = grids
        return grids
    
    def decompose_to_points(self, area: AreaTarget) -> List[PointTarget]:
        """将区域分解为点目标（网格中心点）"""
        grids = self.decompose(area)
        points = []
        for grid in grids:
            point = PointTarget(
                id=grid.id.replace("_G", "_P"),
                name=grid.name.replace("Grid", "Point"),
                latitude=grid.center_lat,
                longitude=grid.center_lon,
                priority=grid.priority,
            )
            points.append(point)
        return points
    
    def _point_in_polygon(
        self, 
        lat: float, 
        lon: float, 
        polygon: list
    ) -> bool:
        """
        射线法判断点是否在多边形内
        """
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
