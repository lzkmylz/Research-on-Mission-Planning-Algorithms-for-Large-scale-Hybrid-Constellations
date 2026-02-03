# -*- coding: utf-8 -*-
"""
STK 接口抽象基类
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.satellite import Satellite
from ..models.observation import ObservationWindow
from ..models.ground_station import GroundStation, DownlinkWindow


class STKInterface(ABC):
    """STK 接口抽象基类"""
    
    @abstractmethod
    def connect(self) -> bool:
        """建立 STK 连接"""
        pass
    
    @abstractmethod
    def disconnect(self) -> None:
        """断开连接"""
        pass
    
    @abstractmethod
    def create_walker_constellation(
        self,
        name: str,
        altitude_km: float,
        inclination_deg: float,
        num_planes: int,
        sats_per_plane: int,
        phase_factor: int = 1
    ) -> List[Satellite]:
        """创建 Walker 星座"""
        pass
    
    @abstractmethod
    def compute_access(
        self,
        satellite: Satellite,
        target_lat: float,
        target_lon: float,
        start_time: str,
        stop_time: str
    ) -> List[ObservationWindow]:
        """计算卫星对目标的可见性窗口"""
        pass
    
    @abstractmethod
    def compute_ground_station_access(
        self,
        satellite: Satellite,
        ground_station: GroundStation,
        start_time: str,
        stop_time: str
    ) -> List[DownlinkWindow]:
        """计算卫星对地面站的可见性窗口"""
        pass
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
        return False
