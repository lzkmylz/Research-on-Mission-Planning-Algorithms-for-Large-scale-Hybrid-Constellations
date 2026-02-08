# -*- coding: utf-8 -*-
"""
天线模型

定义地面站天线的属性和可用时间段。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple


@dataclass
class Antenna:
    """地面站天线模型
    
    Attributes:
        id: 天线标识，如 "BJGS_ANT01"
        name: 天线名称，如 "北京站1号天线"
        station_id: 所属测控数传站ID
        max_data_rate_mbps: 最大数传速率 (Mbps)
        supported_frequencies: 支持的频段，如 ["X", "Ka"]
        available_windows: 可用时间窗口列表，None表示全天可用
        satellite_switch_time: 同一天线服务不同卫星的转换时间 (秒)
    """
    id: str
    name: str
    station_id: str
    
    # 能力参数
    max_data_rate_mbps: float = 800.0
    supported_frequencies: List[str] = field(default_factory=lambda: ["X"])
    
    # 可用时间窗口 [(start_time, end_time), ...]
    # None 表示全天可用
    available_windows: Optional[List[Tuple[str, str]]] = None
    
    # 转换时间 (秒)
    satellite_switch_time: float = 5.0
    
    def is_available_at(self, time: str) -> bool:
        """检查指定时刻天线是否可用
        
        Args:
            time: ISO格式时间字符串
            
        Returns:
            是否可用
        """
        if self.available_windows is None:
            return True
        
        target_time = datetime.fromisoformat(time.replace("Z", "+00:00"))
        
        for start_str, end_str in self.available_windows:
            start = datetime.fromisoformat(start_str.replace("Z", "+00:00"))
            end = datetime.fromisoformat(end_str.replace("Z", "+00:00"))
            if start <= target_time <= end:
                return True
        
        return False
    
    def is_available_during(self, start_time: str, end_time: str) -> bool:
        """检查指定时间段内天线是否可用
        
        Args:
            start_time: 开始时间 (ISO格式)
            end_time: 结束时间 (ISO格式)
            
        Returns:
            是否在整个时间段内可用
        """
        if self.available_windows is None:
            return True
        
        target_start = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
        target_end = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
        
        for win_start_str, win_end_str in self.available_windows:
            win_start = datetime.fromisoformat(win_start_str.replace("Z", "+00:00"))
            win_end = datetime.fromisoformat(win_end_str.replace("Z", "+00:00"))
            if win_start <= target_start and target_end <= win_end:
                return True
        
        return False
    
    def supports_frequency(self, frequency: str) -> bool:
        """检查是否支持指定频段"""
        return frequency in self.supported_frequencies
    
    def __repr__(self) -> str:
        return f"Antenna({self.id}, {self.name}, station={self.station_id}, {self.max_data_rate_mbps}Mbps)"
