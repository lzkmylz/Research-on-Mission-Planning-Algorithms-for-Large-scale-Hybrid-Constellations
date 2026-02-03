# -*- coding: utf-8 -*-
"""
地面站模型
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class GroundStation:
    """地面站模型"""
    id: str
    name: str
    latitude: float       # 纬度 (度)
    longitude: float      # 经度 (度)
    altitude_m: float = 0.0  # 海拔高度 (米)
    
    # 通信能力
    min_elevation_deg: float = 5.0      # 最小仰角 (度)
    max_data_rate_mbps: float = 100.0   # 最大下行速率 (Mbps)
    
    # 可用时间窗口 (可选，None表示全天可用)
    # 格式: [(start_time, end_time), ...]
    available_windows: Optional[List[Tuple[str, str]]] = None
    
    def is_available_at(self, time: str) -> bool:
        """检查指定时刻地面站是否可用"""
        if self.available_windows is None:
            return True
        
        from datetime import datetime
        target_time = datetime.fromisoformat(time.replace("Z", "+00:00"))
        
        for start_str, end_str in self.available_windows:
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            if start <= target_time <= end:
                return True
        
        return False
    
    def __repr__(self) -> str:
        return f"GroundStation({self.id}, {self.name}, ({self.latitude:.2f}, {self.longitude:.2f}))"


@dataclass
class DownlinkWindow:
    """数据下传窗口"""
    id: str
    ground_station_id: str
    satellite_id: str
    start_time: str       # ISO 格式
    end_time: str
    duration_sec: float = 0.0
    
    # 通信性能
    max_data_rate_mbps: float = 100.0
    
    @property
    def max_data_volume_gb(self) -> float:
        """该窗口内最大可下传数据量 (GB)"""
        return (self.max_data_rate_mbps * self.duration_sec) / 8 / 1024
    
    def __repr__(self) -> str:
        return f"DownlinkWindow({self.id}, sat={self.satellite_id}, gs={self.ground_station_id})"
