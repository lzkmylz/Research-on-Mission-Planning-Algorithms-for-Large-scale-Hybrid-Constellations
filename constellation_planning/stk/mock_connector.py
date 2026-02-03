# -*- coding: utf-8 -*-
"""
Mock STK 连接器 - 用于 Mac 开发测试
使用简化模型替代真实 STK 计算
"""

import math
from typing import List, Optional
from datetime import datetime, timedelta
from .interface import STKInterface
from .walker import WalkerConstellationBuilder
from ..models.satellite import Satellite, SatelliteType
from ..models.observation import ObservationWindow
from ..models.ground_station import GroundStation, DownlinkWindow


class MockSTKConnector(STKInterface):
    """
    模拟 STK 连接器
    用于 Mac 开发测试，使用简化几何模型
    """
    
    def __init__(self, use_sgp4: bool = False):
        """
        初始化模拟连接器
        
        Args:
            use_sgp4: 是否使用 SGP4 进行轨道传播（需要 sgp4 库）
        """
        self.use_sgp4 = use_sgp4
        self.connected = False
        self._satellites: List[Satellite] = []
        
    def connect(self) -> bool:
        """模拟连接 - 总是成功"""
        self.connected = True
        return True
    
    def disconnect(self) -> None:
        """断开连接"""
        self.connected = False
        self._satellites = []
    
    def create_walker_constellation(
        self,
        name: str,
        altitude_km: float,
        inclination_deg: float,
        num_planes: int,
        sats_per_plane: int,
        phase_factor: int = 1
    ) -> List[Satellite]:
        """使用 Walker 构建器创建星座"""
        builder = WalkerConstellationBuilder(
            name=name,
            altitude_km=altitude_km,
            inclination_deg=inclination_deg,
            num_planes=num_planes,
            sats_per_plane=sats_per_plane,
            phase_factor=phase_factor,
        )
        self._satellites = builder.build()
        return self._satellites
    
    def compute_access(
        self,
        satellite: Satellite,
        target_lat: float,
        target_lon: float,
        start_time: str,
        stop_time: str
    ) -> List[ObservationWindow]:
        """
        简化的可见性计算
        使用地面轨迹重复周期估算
        """
        windows = []
        
        # 解析时间
        t_start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        t_stop = datetime.fromisoformat(stop_time.replace("Z", "+00:00"))
        
        # 轨道周期 (分钟)
        orbital_period_min = self._compute_orbital_period(satellite.altitude_km)
        
        # 估算访问间隔 (简化模型)
        # 假设每天有 2-3 次过境机会
        visits_per_day = 2.5
        visit_interval_hrs = 24.0 / visits_per_day
        
        # 生成模拟的可见性窗口
        current_time = t_start + timedelta(hours=hash(satellite.id + str(target_lat)) % 10)
        window_id = 0
        
        while current_time < t_stop:
            # 窗口持续时间 (随机 2-8 分钟)
            duration_sec = 120 + (hash(f"{satellite.id}_{window_id}") % 360)
            
            window = ObservationWindow(
                id=f"OBS_{satellite.id}_{window_id:04d}",
                satellite_id=satellite.id,
                target_id=f"TGT_{target_lat:.2f}_{target_lon:.2f}",
                sensor_id=satellite.sensors[0].id if satellite.sensors else "default",
                start_time=current_time.isoformat(),
                end_time=(current_time + timedelta(seconds=duration_sec)).isoformat(),
                duration_sec=duration_sec,
                off_nadir_deg=abs(hash(f"{satellite.id}_{window_id}_angle") % 30),
                is_feasible=True,
            )
            windows.append(window)
            
            # 下一次过境
            current_time += timedelta(hours=visit_interval_hrs)
            window_id += 1
        
        return windows
    
    def compute_ground_station_access(
        self,
        satellite: Satellite,
        ground_station: GroundStation,
        start_time: str,
        stop_time: str
    ) -> List[DownlinkWindow]:
        """简化的地面站可见性计算"""
        windows = []
        
        t_start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        t_stop = datetime.fromisoformat(stop_time.replace("Z", "+00:00"))
        
        # 假设每天 4-6 次过境
        visit_interval_hrs = 5.0
        current_time = t_start + timedelta(hours=hash(satellite.id + ground_station.id) % 4)
        window_id = 0
        
        while current_time < t_stop:
            duration_sec = 300 + (hash(f"{satellite.id}_{ground_station.id}_{window_id}") % 300)
            
            window = DownlinkWindow(
                id=f"DL_{satellite.id}_{ground_station.id}_{window_id:04d}",
                ground_station_id=ground_station.id,
                satellite_id=satellite.id,
                start_time=current_time.isoformat(),
                end_time=(current_time + timedelta(seconds=duration_sec)).isoformat(),
                duration_sec=duration_sec,
                max_data_rate_mbps=ground_station.max_data_rate_mbps,
            )
            windows.append(window)
            
            current_time += timedelta(hours=visit_interval_hrs)
            window_id += 1
        
        return windows
    
    def _compute_orbital_period(self, altitude_km: float) -> float:
        """计算轨道周期 (分钟)"""
        Re = 6371.0  # 地球半径 km
        mu = 398600.4418  # 地球引力常数 km³/s²
        a = Re + altitude_km  # 半长轴
        T = 2 * math.pi * math.sqrt(a**3 / mu)  # 周期 (秒)
        return T / 60.0  # 转换为分钟
