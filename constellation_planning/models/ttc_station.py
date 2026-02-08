# -*- coding: utf-8 -*-
"""
测控数传站模型

升级自 GroundStation，支持上注指令和多天线调度。
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Tuple

from .antenna import Antenna


@dataclass
class TTCStation:
    """测控数传站 (Telemetry, Tracking & Command Station)
    
    支持测控（上注指令、遥测遥控）和数据下传功能。
    由多个天线组成，测控和数传共用天线资源。
    
    Attributes:
        id: 站点标识
        name: 站点名称
        latitude: 纬度 (度)
        longitude: 经度 (度)
        altitude_m: 海拔高度 (米)
        antennas: 天线列表
        min_elevation_deg: 最小仰角 (度)
        uplink_rate_kbps: 上注速率 (kbps)
        base_uplink_time_sec: 基础上注时间 (秒)
        per_task_uplink_time_sec: 每任务附加上注时间 (秒)
    """
    id: str
    name: str
    latitude: float
    longitude: float
    altitude_m: float = 0.0
    
    # 天线配置
    antennas: List[Antenna] = field(default_factory=list)
    
    # 通信参数
    min_elevation_deg: float = 5.0
    
    # 上注能力
    uplink_rate_kbps: float = 64.0           # 上注速率 (kbps)
    base_uplink_time_sec: float = 5.0        # 基础上注时间
    per_task_uplink_time_sec: float = 1.0    # 每任务附加时间
    
    # 站内转换时间
    inter_antenna_switch_time: float = 2.0   # 同站不同天线间切换时间 (秒)
    
    def calculate_uplink_duration(self, num_tasks: int) -> float:
        """计算上注指令所需时间
        
        公式: 总时间 = 基础时间 + 每任务附加时间 × 任务数
        
        Args:
            num_tasks: 需要上注的任务数量
            
        Returns:
            上注时长 (秒)
        """
        return self.base_uplink_time_sec + self.per_task_uplink_time_sec * num_tasks
    
    def get_antenna(self, antenna_id: str) -> Optional[Antenna]:
        """根据ID获取天线"""
        for ant in self.antennas:
            if ant.id == antenna_id:
                return ant
        return None
    
    def get_available_antennas_at(self, time: str) -> List[Antenna]:
        """获取指定时刻可用的天线列表
        
        Args:
            time: ISO格式时间字符串
            
        Returns:
            可用天线列表
        """
        return [ant for ant in self.antennas if ant.is_available_at(time)]
    
    def get_available_antennas_during(
        self, 
        start_time: str, 
        end_time: str
    ) -> List[Antenna]:
        """获取指定时间段内可用的天线列表"""
        return [
            ant for ant in self.antennas 
            if ant.is_available_during(start_time, end_time)
        ]
    
    def get_antennas_by_frequency(self, frequency: str) -> List[Antenna]:
        """获取支持指定频段的天线列表"""
        return [ant for ant in self.antennas if ant.supports_frequency(frequency)]
    
    @property
    def max_data_rate_mbps(self) -> float:
        """站点最大数传速率（所有天线中最大的）"""
        if not self.antennas:
            return 0.0
        return max(ant.max_data_rate_mbps for ant in self.antennas)
    
    @property
    def total_antenna_count(self) -> int:
        """天线总数"""
        return len(self.antennas)
    
    def __repr__(self) -> str:
        return f"TTCStation({self.id}, {self.name}, ({self.latitude:.2f}, {self.longitude:.2f}), {self.total_antenna_count} antennas)"


@dataclass
class DownlinkWindow:
    """数据下传窗口
    
    描述卫星与地面站之间的可见性窗口。
    """
    id: str
    station_id: str
    satellite_id: str
    start_time: str       # ISO 格式
    end_time: str
    duration_sec: float = 0.0
    
    # 通信性能（窗口级别的约束）
    max_data_rate_mbps: float = 100.0
    
    @property
    def max_data_volume_gb(self) -> float:
        """该窗口内最大可下传数据量 (GB)"""
        return (self.max_data_rate_mbps * self.duration_sec) / 8 / 1024
    
    def __repr__(self) -> str:
        return f"DownlinkWindow({self.id}, sat={self.satellite_id}, station={self.station_id})"


# ============================================================
# 预定义的测控数传站
# ============================================================

def create_default_ttc_stations() -> List[TTCStation]:
    """创建默认的测控数传站列表（中国主要测控站）"""
    
    # 北京站
    beijing_antennas = [
        Antenna(
            id="BJGS_ANT01",
            name="北京站1号天线",
            station_id="BJGS",
            max_data_rate_mbps=1200.0,
            supported_frequencies=["X", "Ka"],
            satellite_switch_time=5.0,
        ),
        Antenna(
            id="BJGS_ANT02",
            name="北京站2号天线",
            station_id="BJGS",
            max_data_rate_mbps=800.0,
            supported_frequencies=["X"],
            satellite_switch_time=4.0,
        ),
    ]
    
    beijing = TTCStation(
        id="BJGS",
        name="北京测控站",
        latitude=40.0,
        longitude=116.4,
        altitude_m=50.0,
        antennas=beijing_antennas,
        min_elevation_deg=5.0,
        uplink_rate_kbps=64.0,
        base_uplink_time_sec=5.0,
        per_task_uplink_time_sec=1.0,
    )
    
    # 喀什站
    kashgar_antennas = [
        Antenna(
            id="KSGS_ANT01",
            name="喀什站1号天线",
            station_id="KSGS",
            max_data_rate_mbps=1000.0,
            supported_frequencies=["X", "Ka"],
            satellite_switch_time=5.0,
        ),
        Antenna(
            id="KSGS_ANT02",
            name="喀什站2号天线",
            station_id="KSGS",
            max_data_rate_mbps=600.0,
            supported_frequencies=["X"],
            satellite_switch_time=4.0,
        ),
    ]
    
    kashgar = TTCStation(
        id="KSGS",
        name="喀什测控站",
        latitude=39.5,
        longitude=76.0,
        altitude_m=1300.0,
        antennas=kashgar_antennas,
        min_elevation_deg=5.0,
        uplink_rate_kbps=64.0,
    )
    
    # 三亚站
    sanya_antennas = [
        Antenna(
            id="SYGS_ANT01",
            name="三亚站1号天线",
            station_id="SYGS",
            max_data_rate_mbps=1500.0,
            supported_frequencies=["X", "Ka", "S"],
            satellite_switch_time=5.0,
        ),
    ]
    
    sanya = TTCStation(
        id="SYGS",
        name="三亚测控站",
        latitude=18.2,
        longitude=109.5,
        altitude_m=10.0,
        antennas=sanya_antennas,
        min_elevation_deg=5.0,
        uplink_rate_kbps=128.0,
    )
    
    # 佳木斯站
    jiamusi_antennas = [
        Antenna(
            id="JMSGS_ANT01",
            name="佳木斯站1号天线",
            station_id="JMSGS",
            max_data_rate_mbps=800.0,
            supported_frequencies=["X"],
            satellite_switch_time=4.0,
        ),
    ]
    
    jiamusi = TTCStation(
        id="JMSGS",
        name="佳木斯测控站",
        latitude=46.8,
        longitude=130.3,
        altitude_m=80.0,
        antennas=jiamusi_antennas,
        min_elevation_deg=5.0,
    )
    
    return [beijing, kashgar, sanya, jiamusi]
