# -*- coding: utf-8 -*-
"""
Orekit 轨道计算连接器 - 高精度轨道外推与可见性计算

使用 Orekit Java 库的 Python 封装，提供：
- Walker 星座创建
- 卫星-目标可见性窗口计算
- 卫星-地面站可见性窗口计算

安装要求：
    conda install -c conda-forge orekit
    需要 JDK 11+
"""

import math
from typing import List, Optional
from datetime import datetime, timedelta
from pathlib import Path

from .interface import STKInterface
from .walker import WalkerConstellationBuilder
from ..models.satellite import Satellite
from ..models.observation import ObservationWindow
from ..models.ground_station import GroundStation, DownlinkWindow

# Orekit 延迟导入（仅在实际使用时）
_orekit_initialized = False


def _init_orekit(data_path: Optional[Path] = None):
    """
    初始化 Orekit JVM 和数据文件
    
    Args:
        data_path: Orekit 数据文件路径，如果为 None 则使用默认路径
    """
    global _orekit_initialized
    if _orekit_initialized:
        return
    
    import orekit
    orekit.initVM()
    
    from org.orekit.data import DataContext, DirectoryCrawler, ZipJarCrawler
    from java.io import File
    import os
    
    data_manager = DataContext.getDefault().getDataProvidersManager()
    
    # 尝试按优先级加载数据源
    data_loaded = False
    
    # 1. 首先尝试用户指定的路径
    if data_path:
        data_path = Path(data_path)
        if data_path.exists():
            if data_path.is_dir():
                data_manager.addProvider(DirectoryCrawler(File(str(data_path))))
                data_loaded = True
                print(f"Orekit 数据已从目录加载: {data_path}")
            elif data_path.suffix == '.zip':
                data_manager.addProvider(ZipJarCrawler(File(str(data_path))))
                data_loaded = True
                print(f"Orekit 数据已从 ZIP 加载: {data_path}")
    
    # 2. 尝试当前目录的 orekit-data 目录或 zip 文件
    if not data_loaded:
        cwd = Path.cwd()
        possible_paths = [
            cwd / "orekit-data",
            cwd / "orekit-data.zip",
            Path.home() / ".orekit" / "orekit-data",
            Path.home() / ".orekit" / "orekit-data.zip",
        ]
        
        for p in possible_paths:
            if p.exists():
                if p.is_dir():
                    data_manager.addProvider(DirectoryCrawler(File(str(p))))
                    data_loaded = True
                    print(f"Orekit 数据已从目录加载: {p}")
                    break
                elif p.suffix == '.zip':
                    data_manager.addProvider(ZipJarCrawler(File(str(p))))
                    data_loaded = True
                    print(f"Orekit 数据已从 ZIP 加载: {p}")
                    break
    
    # 3. 使用 orekit.pyhelpers 下载数据
    if not data_loaded:
        try:
            from orekit.pyhelpers import download_orekit_data_curdir, setup_orekit_curdir
            
            # 检查是否已有数据
            orekit_data_zip = Path.cwd() / "orekit-data.zip"
            if not orekit_data_zip.exists():
                print("正在下载 Orekit 数据文件（首次运行，可能需要几分钟）...")
                download_orekit_data_curdir()
            
            setup_orekit_curdir()
            data_loaded = True
            print("Orekit 数据初始化完成")
        except Exception as e:
            print(f"自动下载失败: {e}")
            print("请手动下载 orekit-data.zip：")
            print("  https://gitlab.orekit.org/orekit/orekit-data/-/archive/master/orekit-data-master.zip")
            print("并将其放置在项目目录或 ~/.orekit/ 目录下")
            raise RuntimeError(f"Orekit 数据加载失败: {e}")
    
    _orekit_initialized = True


class OrekitConnector(STKInterface):
    """
    Orekit 轨道计算连接器
    
    使用 Orekit 提供高精度轨道外推和可见性计算，
    可在 Mac/Linux 上运行，无需 STK。
    """
    
    def __init__(self, data_path: Optional[Path] = None):
        """
        初始化 Orekit 连接器
        
        Args:
            data_path: Orekit 数据文件路径（包含 UTC-TAI.history 等）
        """
        self.data_path = data_path
        self.connected = False
        self._satellites: List[Satellite] = []
        self._propagators = {}  # satellite_id -> Propagator
        
    def connect(self) -> bool:
        """初始化 Orekit JVM"""
        try:
            _init_orekit(self.data_path)
            self.connected = True
            return True
        except Exception as e:
            print(f"Orekit 初始化失败: {e}")
            return False
    
    def disconnect(self) -> None:
        """断开连接（清理缓存）"""
        self.connected = False
        self._satellites = []
        self._propagators = {}
    
    def create_walker_constellation(
        self,
        name: str,
        altitude_km: float,
        inclination_deg: float,
        num_planes: int,
        sats_per_plane: int,
        phase_factor: int = 1
    ) -> List[Satellite]:
        """
        使用 Orekit 创建 Walker 星座
        
        使用开普勒轨道模型创建卫星，并为每颗卫星创建 SGP4 或数值传播器。
        """
        # 使用现有的 Walker 构建器创建卫星对象
        builder = WalkerConstellationBuilder(
            name=name,
            altitude_km=altitude_km,
            inclination_deg=inclination_deg,
            num_planes=num_planes,
            sats_per_plane=sats_per_plane,
            phase_factor=phase_factor,
        )
        self._satellites = builder.build()
        
        # 为每颗卫星创建 Orekit 传播器
        self._create_propagators(altitude_km, inclination_deg, num_planes, sats_per_plane, phase_factor)
        
        return self._satellites
    
    def _create_propagators(
        self,
        altitude_km: float,
        inclination_deg: float,
        num_planes: int,
        sats_per_plane: int,
        phase_factor: int
    ):
        """为星座中的每颗卫星创建 Orekit 传播器"""
        from org.orekit.orbits import KeplerianOrbit, PositionAngleType
        from org.orekit.propagation.analytical import KeplerianPropagator
        from org.orekit.frames import FramesFactory
        from org.orekit.time import TimeScalesFactory, AbsoluteDate
        from org.orekit.utils import Constants
        
        mu = Constants.WGS84_EARTH_MU  # 地球引力常数
        Re = Constants.WGS84_EARTH_EQUATORIAL_RADIUS / 1000.0  # km
        a = (Re + altitude_km) * 1000.0  # 半长轴 (m)
        e = 0.0  # 圆轨道
        i = math.radians(inclination_deg)
        
        inertial_frame = FramesFactory.getEME2000()
        utc = TimeScalesFactory.getUTC()
        epoch = AbsoluteDate(2026, 1, 1, 0, 0, 0.0, utc)
        
        # Walker Delta Pattern: i:t/p/f
        total_sats = num_planes * sats_per_plane
        
        for plane_idx in range(num_planes):
            # 升交点赤经 (RAAN)
            raan = 2 * math.pi * plane_idx / num_planes
            
            for sat_idx in range(sats_per_plane):
                # 相位角（真近点角）
                phase_offset = 2 * math.pi * phase_factor * plane_idx / total_sats
                true_anomaly = 2 * math.pi * sat_idx / sats_per_plane + phase_offset
                
                # 创建开普勒轨道
                orbit = KeplerianOrbit(
                    a,                      # 半长轴 (m)
                    e,                      # 偏心率
                    i,                      # 轨道倾角 (rad)
                    0.0,                    # 近地点辐角 (rad)
                    raan,                   # 升交点赤经 (rad)
                    true_anomaly,           # 真近点角 (rad)
                    PositionAngleType.TRUE,
                    inertial_frame,
                    epoch,
                    mu
                )
                
                # 创建开普勒传播器
                propagator = KeplerianPropagator(orbit)
                
                # 获取对应的卫星 ID
                sat_index = plane_idx * sats_per_plane + sat_idx
                if sat_index < len(self._satellites):
                    sat_id = self._satellites[sat_index].id
                    self._propagators[sat_id] = propagator
    
    def compute_access(
        self,
        satellite: Satellite,
        target_lat: float,
        target_lon: float,
        start_time: str,
        stop_time: str
    ) -> List[ObservationWindow]:
        """
        使用 Orekit 计算卫星对目标的可见性窗口
        
        使用仰角检测器 (ElevationDetector) 检测卫星何时进入/离开目标视野。
        """
        from org.orekit.time import TimeScalesFactory, AbsoluteDate
        from org.orekit.frames import FramesFactory, TopocentricFrame
        from org.orekit.bodies import GeodeticPoint, OneAxisEllipsoid
        from org.orekit.propagation.events import ElevationDetector, EventsLogger
        from org.orekit.utils import Constants, IERSConventions
        
        windows = []
        
        # 检查传播器是否存在
        if satellite.id not in self._propagators:
            return windows
        
        propagator = self._propagators[satellite.id]
        
        # 解析时间
        utc = TimeScalesFactory.getUTC()
        t_start = self._parse_iso_to_absolute_date(start_time, utc)
        t_stop = self._parse_iso_to_absolute_date(stop_time, utc)
        
        # 创建地球模型
        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(
            Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
            Constants.WGS84_EARTH_FLATTENING,
            itrf
        )
        
        # 创建地面站（目标位置）
        target_point = GeodeticPoint(
            math.radians(target_lat),
            math.radians(target_lon),
            0.0  # 海拔
        )
        target_frame = TopocentricFrame(earth, target_point, "Target")
        
        # 创建仰角检测器（最小仰角 10°）
        min_elevation = math.radians(10.0)
        elevation_detector = ElevationDetector(target_frame).withConstantElevation(min_elevation)
        
        # 创建事件记录器
        events_logger = EventsLogger()
        logged_detector = events_logger.monitorDetector(elevation_detector)
        
        # 添加检测器并传播
        propagator.clearEventsDetectors()
        propagator.addEventDetector(logged_detector)
        
        try:
            propagator.propagate(t_start, t_stop)
        except Exception as e:
            print(f"传播过程中出错: {e}")
            return windows
        
        # 提取可见性窗口
        logged_events = events_logger.getLoggedEvents()
        window_start = None
        window_id = 0
        
        for i in range(logged_events.size()):
            event = logged_events.get(i)
            is_increasing = event.isIncreasing()
            event_date = event.getState().getDate()
            
            if is_increasing:
                # 卫星进入视野
                window_start = event_date
            else:
                # 卫星离开视野
                if window_start is not None:
                    duration_sec = event_date.durationFrom(window_start)
                    
                    window = ObservationWindow(
                        id=f"OBS_{satellite.id}_{window_id:04d}",
                        satellite_id=satellite.id,
                        target_id=f"TGT_{target_lat:.2f}_{target_lon:.2f}",
                        sensor_id=satellite.sensors[0].id if satellite.sensors else "default",
                        start_time=self._absolute_date_to_iso(window_start),
                        end_time=self._absolute_date_to_iso(event_date),
                        duration_sec=duration_sec,
                        off_nadir_deg=0.0,  # TODO: 计算实际离轴角
                        is_feasible=True,
                    )
                    windows.append(window)
                    window_id += 1
                    window_start = None
        
        return windows
    
    def compute_ground_station_access(
        self,
        satellite: Satellite,
        ground_station: GroundStation,
        start_time: str,
        stop_time: str
    ) -> List[DownlinkWindow]:
        """
        使用 Orekit 计算卫星对地面站的可见性窗口
        
        与 compute_access 类似，但返回 DownlinkWindow 类型。
        """
        from org.orekit.time import TimeScalesFactory, AbsoluteDate
        from org.orekit.frames import FramesFactory, TopocentricFrame
        from org.orekit.bodies import GeodeticPoint, OneAxisEllipsoid
        from org.orekit.propagation.events import ElevationDetector, EventsLogger
        from org.orekit.utils import Constants, IERSConventions
        
        windows = []
        
        if satellite.id not in self._propagators:
            return windows
        
        propagator = self._propagators[satellite.id]
        
        utc = TimeScalesFactory.getUTC()
        t_start = self._parse_iso_to_absolute_date(start_time, utc)
        t_stop = self._parse_iso_to_absolute_date(stop_time, utc)
        
        # 创建地球模型
        itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
        earth = OneAxisEllipsoid(
            Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
            Constants.WGS84_EARTH_FLATTENING,
            itrf
        )
        
        # 创建地面站拓扑坐标系
        gs_point = GeodeticPoint(
            math.radians(ground_station.latitude),
            math.radians(ground_station.longitude),
            ground_station.altitude_m if hasattr(ground_station, 'altitude_m') else 0.0
        )
        gs_frame = TopocentricFrame(earth, gs_point, ground_station.name)
        
        # 使用地面站的最小仰角
        min_elev_deg = ground_station.min_elevation_deg if hasattr(ground_station, 'min_elevation_deg') else 5.0
        min_elevation = math.radians(min_elev_deg)
        elevation_detector = ElevationDetector(gs_frame).withConstantElevation(min_elevation)
        
        events_logger = EventsLogger()
        logged_detector = events_logger.monitorDetector(elevation_detector)
        
        propagator.clearEventsDetectors()
        propagator.addEventDetector(logged_detector)
        
        try:
            propagator.propagate(t_start, t_stop)
        except Exception as e:
            print(f"传播过程中出错: {e}")
            return windows
        
        logged_events = events_logger.getLoggedEvents()
        window_start = None
        window_id = 0
        
        for i in range(logged_events.size()):
            event = logged_events.get(i)
            is_increasing = event.isIncreasing()
            event_date = event.getState().getDate()
            
            if is_increasing:
                window_start = event_date
            else:
                if window_start is not None:
                    duration_sec = event_date.durationFrom(window_start)
                    
                    window = DownlinkWindow(
                        id=f"DL_{satellite.id}_{ground_station.id}_{window_id:04d}",
                        ground_station_id=ground_station.id,
                        satellite_id=satellite.id,
                        start_time=self._absolute_date_to_iso(window_start),
                        end_time=self._absolute_date_to_iso(event_date),
                        duration_sec=duration_sec,
                        max_data_rate_mbps=ground_station.max_data_rate_mbps,
                    )
                    windows.append(window)
                    window_id += 1
                    window_start = None
        
        return windows
    
    def _parse_iso_to_absolute_date(self, iso_string: str, utc) -> "AbsoluteDate":
        """将 ISO 时间字符串转换为 Orekit AbsoluteDate"""
        from org.orekit.time import AbsoluteDate
        
        # 解析 ISO 格式
        dt = datetime.fromisoformat(iso_string.replace("Z", "+00:00"))
        return AbsoluteDate(
            dt.year, dt.month, dt.day,
            dt.hour, dt.minute, float(dt.second + dt.microsecond / 1e6),
            utc
        )
    
    def _absolute_date_to_iso(self, abs_date) -> str:
        """将 Orekit AbsoluteDate 转换为 ISO 时间字符串"""
        from org.orekit.time import TimeScalesFactory
        
        utc = TimeScalesFactory.getUTC()
        components = abs_date.getComponents(utc)
        date_comp = components.getDate()
        time_comp = components.getTime()
        
        return f"{date_comp.getYear():04d}-{date_comp.getMonth():02d}-{date_comp.getDay():02d}T{time_comp.getHour():02d}:{time_comp.getMinute():02d}:{time_comp.getSecond():06.3f}Z"
