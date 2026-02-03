# -*- coding: utf-8 -*-
"""
STK 10 COM 接口连接器 (Windows 专用)
"""

import sys

# 仅在 Windows 平台导入
if sys.platform != "win32":
    raise ImportError("STK10Connector 仅支持 Windows 平台")

import win32com.client
from typing import List, Optional
from .interface import STKInterface
from ..models.satellite import Satellite, SatelliteType
from ..models.observation import ObservationWindow
from ..models.ground_station import GroundStation, DownlinkWindow


class STK10Connector(STKInterface):
    """
    STK 10 COM 接口连接器
    使用 win32com 调用 STK Object Model
    """
    
    def __init__(self):
        self.app = None
        self.root = None
        self._scenario = None
    
    def connect(self) -> bool:
        """连接到 STK 10"""
        try:
            # 尝试连接到已运行的 STK 实例
            try:
                self.app = win32com.client.GetActiveObject("STK10.Application")
            except:
                # 启动新的 STK 实例
                self.app = win32com.client.Dispatch("STK10.Application")
            
            self.app.Visible = True
            self.root = self.app.Personality2
            return True
            
        except Exception as e:
            raise RuntimeError(f"无法连接 STK 10: {e}")
    
    def disconnect(self) -> None:
        """断开连接"""
        if self._scenario:
            self.root.CloseScenario()
        self.app = None
        self.root = None
        self._scenario = None
    
    def create_walker_constellation(
        self,
        name: str,
        altitude_km: float,
        inclination_deg: float,
        num_planes: int,
        sats_per_plane: int,
        phase_factor: int = 1
    ) -> List[Satellite]:
        """使用 STK Walker 命令创建星座"""
        # 创建场景 (如果不存在)
        if not self._scenario:
            self.root.NewScenario("ConstellationPlanning")
            self._scenario = self.root.CurrentScenario
        
        # 使用 Walker 命令创建星座
        # TODO: 实现完整的 STK Connect 命令调用
        
        satellites = []
        # ... 解析 STK 返回结果，创建 Satellite 对象
        
        return satellites
    
    def compute_access(
        self,
        satellite: Satellite,
        target_lat: float,
        target_lon: float,
        start_time: str,
        stop_time: str
    ) -> List[ObservationWindow]:
        """使用 STK Access 工具计算可见性"""
        windows = []
        
        # TODO: 实现 STK Access 计算
        # 1. 创建目标点
        # 2. 计算 Access
        # 3. 提取时间窗口
        
        return windows
    
    def compute_ground_station_access(
        self,
        satellite: Satellite,
        ground_station: GroundStation,
        start_time: str,
        stop_time: str
    ) -> List[DownlinkWindow]:
        """计算地面站可见性"""
        windows = []
        
        # TODO: 实现地面站 Access 计算
        
        return windows
