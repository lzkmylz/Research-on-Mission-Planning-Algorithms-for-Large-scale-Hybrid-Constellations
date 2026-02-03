# -*- coding: utf-8 -*-
"""
目标模型 - 点目标、网格目标、动态目标、区域目标
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Union
from enum import Enum
from datetime import datetime


class TargetType(Enum):
    """目标类型"""
    POINT = "point"       # 点目标
    GRID = "grid"         # 网格目标
    VEHICLE = "vehicle"   # 车辆动态目标
    SHIP = "ship"         # 舰船动态目标
    AREA = "area"         # 区域目标


@dataclass
class PointTarget:
    """点目标"""
    id: str
    name: str
    latitude: float       # 纬度 (度)
    longitude: float      # 经度 (度)
    priority: float = 1.0 # 优先级/重要程度 (0-1)
    
    # 时间约束
    earliest_time: Optional[str] = None  # 最早成像时间 (ISO格式)
    latest_time: Optional[str] = None    # 最晚成像时间
    
    # 成像要求
    required_resolution_m: Optional[float] = None  # 所需分辨率
    
    def __repr__(self) -> str:
        return f"PointTarget({self.id}, {self.name}, ({self.latitude:.2f}, {self.longitude:.2f}))"


@dataclass
class GridTarget:
    """
    网格目标 - 固定大小的网格单元
    默认为 0.1°×0.1° (约 11km×11km)
    """
    id: str
    name: str
    center_lat: float           # 网格中心纬度
    center_lon: float           # 网格中心经度
    size_deg: float = 0.1       # 网格边长 (度)
    priority: float = 1.0       # 重要程度 (0-1)
    
    # 时间约束
    earliest_time: Optional[str] = None
    latest_time: Optional[str] = None
    
    @property
    def bounds(self) -> Tuple[float, float, float, float]:
        """返回边界 (min_lat, min_lon, max_lat, max_lon)"""
        half = self.size_deg / 2
        return (
            self.center_lat - half,
            self.center_lon - half,
            self.center_lat + half,
            self.center_lon + half
        )
    
    def contains(self, lat: float, lon: float) -> bool:
        """检查点是否在网格内"""
        min_lat, min_lon, max_lat, max_lon = self.bounds
        return min_lat <= lat <= max_lat and min_lon <= lon <= max_lon
    
    def __repr__(self) -> str:
        return f"GridTarget({self.id}, center=({self.center_lat:.2f}, {self.center_lon:.2f}))"


@dataclass
class WaypointPath:
    """
    运动路径 - 航点序列
    每个航点包含: (时间, 纬度, 经度)
    """
    waypoints: List[Tuple[str, float, float]] = field(default_factory=list)
    
    def add_waypoint(self, time: str, lat: float, lon: float) -> None:
        """添加航点"""
        self.waypoints.append((time, lat, lon))
    
    def position_at(self, time: str) -> Tuple[float, float]:
        """
        插值计算指定时刻的位置
        使用线性插值
        """
        if not self.waypoints:
            raise ValueError("路径为空")
        
        if len(self.waypoints) == 1:
            return (self.waypoints[0][1], self.waypoints[0][2])
        
        # 解析目标时间
        target_time = datetime.fromisoformat(time.replace("Z", "+00:00"))
        
        # 查找插值区间
        for i in range(len(self.waypoints) - 1):
            t1_str, lat1, lon1 = self.waypoints[i]
            t2_str, lat2, lon2 = self.waypoints[i + 1]
            
            t1 = datetime.fromisoformat(t1_str.replace("Z", "+00:00"))
            t2 = datetime.fromisoformat(t2_str.replace("Z", "+00:00"))
            
            if t1 <= target_time <= t2:
                # 线性插值
                total_sec = (t2 - t1).total_seconds()
                if total_sec == 0:
                    return (lat1, lon1)
                
                elapsed_sec = (target_time - t1).total_seconds()
                ratio = elapsed_sec / total_sec
                
                lat = lat1 + ratio * (lat2 - lat1)
                lon = lon1 + ratio * (lon2 - lon1)
                return (lat, lon)
        
        # 时间超出范围，返回最近的端点
        first_time = datetime.fromisoformat(self.waypoints[0][0].replace("Z", "+00:00"))
        if target_time < first_time:
            return (self.waypoints[0][1], self.waypoints[0][2])
        else:
            return (self.waypoints[-1][1], self.waypoints[-1][2])


@dataclass
class MovingTarget:
    """
    动态目标 - 车辆或舰船
    位置随时间变化
    """
    id: str
    name: str
    target_type: TargetType  # VEHICLE 或 SHIP
    path: WaypointPath       # 运动路径
    priority: float = 1.0
    speed_kmh: float = 30.0  # 典型速度 (km/h)，用于估算
    
    # 时间约束
    earliest_time: Optional[str] = None
    latest_time: Optional[str] = None
    
    def position_at(self, time: str) -> Tuple[float, float]:
        """获取指定时刻的位置"""
        return self.path.position_at(time)
    
    @classmethod
    def create_vehicle(
        cls,
        id: str,
        name: str,
        waypoints: List[Tuple[str, float, float]],
        priority: float = 1.0,
        speed_kmh: float = 60.0
    ) -> "MovingTarget":
        """创建车辆目标"""
        path = WaypointPath(waypoints=waypoints)
        return cls(
            id=id,
            name=name,
            target_type=TargetType.VEHICLE,
            path=path,
            priority=priority,
            speed_kmh=speed_kmh
        )
    
    @classmethod
    def create_ship(
        cls,
        id: str,
        name: str,
        waypoints: List[Tuple[str, float, float]],
        priority: float = 1.0,
        speed_kmh: float = 30.0
    ) -> "MovingTarget":
        """创建舰船目标"""
        path = WaypointPath(waypoints=waypoints)
        return cls(
            id=id,
            name=name,
            target_type=TargetType.SHIP,
            path=path,
            priority=priority,
            speed_kmh=speed_kmh
        )
    
    def __repr__(self) -> str:
        return f"MovingTarget({self.id}, {self.name}, {self.target_type.value})"


@dataclass
class AreaTarget:
    """
    区域目标 - 多边形区域
    可分解为点目标或网格目标
    """
    id: str
    name: str
    polygon: List[Tuple[float, float]]  # [(lat, lon), ...] 多边形顶点
    priority: float = 1.0
    
    # 分解后的子目标
    sub_targets: List[Union[PointTarget, GridTarget]] = field(default_factory=list)
    
    def bounding_box(self) -> Tuple[float, float, float, float]:
        """返回边界框 (min_lat, min_lon, max_lat, max_lon)"""
        lats = [p[0] for p in self.polygon]
        lons = [p[1] for p in self.polygon]
        return (min(lats), min(lons), max(lats), max(lons))
    
    def __repr__(self) -> str:
        return f"AreaTarget({self.id}, {self.name}, vertices={len(self.polygon)})"


# 类型别名：所有目标类型的联合
Target = Union[PointTarget, GridTarget, MovingTarget, AreaTarget]
