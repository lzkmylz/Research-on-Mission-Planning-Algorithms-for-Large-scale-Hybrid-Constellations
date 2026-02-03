# -*- coding: utf-8 -*-
"""
Walker 星座生成器
"""

import math
from typing import List
from dataclasses import dataclass
from ..models.satellite import Satellite, SatelliteType


@dataclass
class WalkerConstellationBuilder:
    """
    Walker 星座构建器
    Walker Delta 星座表示: t/p/f
    - t: 总卫星数
    - p: 轨道面数
    - f: 相位因子
    """
    
    name: str = "Constellation"
    altitude_km: float = 500.0
    inclination_deg: float = 97.4  # 太阳同步轨道
    num_planes: int = 6
    sats_per_plane: int = 10
    phase_factor: int = 1
    
    # 卫星类型
    sat_type: SatelliteType = SatelliteType.OPTICAL
    
    @property
    def total_satellites(self) -> int:
        return self.num_planes * self.sats_per_plane
    
    @property
    def walker_notation(self) -> str:
        """Walker 表示法 t/p/f"""
        return f"{self.total_satellites}/{self.num_planes}/{self.phase_factor}"
    
    def build(self) -> List[Satellite]:
        """生成星座中的所有卫星"""
        satellites = []
        
        # 轨道面间 RAAN 间隔
        raan_spacing = 360.0 / self.num_planes
        
        # 同一轨道面内卫星间真近点角间隔
        ta_spacing = 360.0 / self.sats_per_plane
        
        # 相位偏移
        phase_offset = (360.0 * self.phase_factor) / self.total_satellites
        
        sat_id = 0
        for plane_idx in range(self.num_planes):
            raan = plane_idx * raan_spacing
            
            for sat_idx in range(self.sats_per_plane):
                # 真近点角 = 面内索引 * 间隔 + 面间相位偏移
                true_anomaly = (sat_idx * ta_spacing + plane_idx * phase_offset) % 360.0
                
                satellite = Satellite(
                    id=f"SAT_{sat_id:03d}",
                    name=f"{self.name}_P{plane_idx:02d}_S{sat_idx:02d}",
                    sat_type=self.sat_type,
                    altitude_km=self.altitude_km,
                    inclination_deg=self.inclination_deg,
                    raan_deg=raan,
                    arg_perigee_deg=0.0,  # 圆轨道
                    true_anomaly_deg=true_anomaly,
                )
                satellites.append(satellite)
                sat_id += 1
        
        return satellites
    
    @classmethod
    def from_config(cls, config: "ConstellationConfig") -> "WalkerConstellationBuilder":
        """从配置创建构建器"""
        from ..config.schemas import ConstellationConfig
        return cls(
            name=config.name,
            altitude_km=config.altitude_km,
            inclination_deg=config.inclination_deg,
            num_planes=config.num_planes,
            sats_per_plane=config.sats_per_plane,
            phase_factor=config.phase_factor,
        )
