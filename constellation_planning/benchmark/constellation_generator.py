"""
星座配置生成器

基于真实卫星参数生成混合星座配置，用于基准测试。
"""

import json
import math
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class SatelliteTemplate:
    """卫星型号模板"""
    type: str
    count: int
    resolution_m: float
    swath_width_km: float
    altitude_km: float
    inclination_deg: float
    imaging_modes: List[str]
    agility: Dict[str, Any]
    constraints: Dict[str, Any]
    storage_capacity_gb: int
    downlink_rate_mbps: int
    
    @classmethod
    def ultra_high_res_optical(cls) -> 'SatelliteTemplate':
        """超高分辨率光学卫星（参考WorldView-3、高景一号）"""
        return cls(
            type="ultra_high_res_optical",
            count=10,
            resolution_m=0.5,
            swath_width_km=12,
            altitude_km=530,
            inclination_deg=97.4,
            imaging_modes=["strip", "stare", "area"],
            agility={
                "roll_range_deg": [-30, 30],
                "pitch_range_deg": [-15, 15],
                "yaw_range_deg": [-5, 5],
                "maneuver_time_sec": 8,
                "settling_time_sec": 4,
                "max_slew_rate_deg_per_sec": 3.0
            },
            constraints={
                "min_elevation_deg": 20,
                "max_sun_angle_deg": 70,
                "max_cloud_cover": 0.3,
                "min_sun_elevation_deg": 10
            },
            storage_capacity_gb=256,
            downlink_rate_mbps=300
        )
    
    @classmethod
    def high_res_optical(cls) -> 'SatelliteTemplate':
        """高分辨率光学卫星（参考Sentinel-2、资源三号）"""
        return cls(
            type="high_res_optical",
            count=90,
            resolution_m=2.0,
            swath_width_km=40,
            altitude_km=645,
            inclination_deg=98.0,
            imaging_modes=["strip", "stare", "area"],
            agility={
                "roll_range_deg": [-25, 25],
                "pitch_range_deg": [-10, 10],
                "maneuver_time_sec": 12,
                "settling_time_sec": 5,
                "max_slew_rate_deg_per_sec": 2.0
            },
            constraints={
                "min_elevation_deg": 15,
                "max_cloud_cover": 0.4
            },
            storage_capacity_gb=128,
            downlink_rate_mbps=150
        )
    
    @classmethod
    def ultra_high_res_sar(cls) -> 'SatelliteTemplate':
        """超高分辨率SAR卫星（参考TerraSAR-X、高分三号）"""
        return cls(
            type="ultra_high_res_sar",
            count=10,
            resolution_m=1.0,
            swath_width_km=10,
            altitude_km=514,
            inclination_deg=97.44,
            imaging_modes=["spotlight", "stripmap", "sliding_spotlight", "scanSAR"],
            agility={
                "roll_range_deg": [-35, 35],
                "maneuver_time_sec": 10,
                "max_slew_rate_deg_per_sec": 2.5
            },
            constraints={
                "min_elevation_deg": 15,
                "no_cloud_constraint": True
            },
            storage_capacity_gb=384,
            downlink_rate_mbps=600
        )
    
    @classmethod
    def high_res_sar(cls) -> 'SatelliteTemplate':
        """高分辨率SAR卫星（参考Sentinel-1、ALOS-2）"""
        return cls(
            type="high_res_sar",
            count=90,
            resolution_m=5.0,
            swath_width_km=80,
            altitude_km=693,
            inclination_deg=98.18,
            imaging_modes=["spotlight", "stripmap", "sliding_spotlight", "scanSAR"],
            agility={
                "roll_range_deg": [-30, 30],
                "maneuver_time_sec": 15,
                "max_slew_rate_deg_per_sec": 1.5
            },
            constraints={
                "min_elevation_deg": 15,
                "no_cloud_constraint": True
            },
            storage_capacity_gb=256,
            downlink_rate_mbps=300
        )


class WalkerConstellationGenerator:
    """Walker星座生成器"""
    
    def __init__(self, output_dir: str = "benchmark_dataset/constellation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 定义四种卫星模板
        self.templates = {
            "ultra_high_res_optical": SatelliteTemplate.ultra_high_res_optical(),
            "high_res_optical": SatelliteTemplate.high_res_optical(),
            "ultra_high_res_sar": SatelliteTemplate.ultra_high_res_sar(),
            "high_res_sar": SatelliteTemplate.high_res_sar()
        }
    
    def generate_walker_constellation(
        self,
        total_satellites: int = 200,
        num_planes: int = 10,
        phase_factor: int = 1,
        start_epoch: str = "2024-06-01T00:00:00Z"
    ) -> List[Dict[str, Any]]:
        """
        生成Walker Delta星座配置
        
        Args:
            total_satellites: 总卫星数
            num_planes: 轨道平面数
            phase_factor: 相位因子
            start_epoch: 起始历元
            
        Returns:
            卫星配置列表
        """
        sats_per_plane = total_satellites // num_planes
        satellites = []
        
        # 计算各型号卫星数量
        type_distribution = {
            "ultra_high_res_optical": 10,
            "high_res_optical": 90,
            "ultra_high_res_sar": 10,
            "high_res_sar": 90
        }
        
        # 为每个型号生成卫星
        sat_id_counter = 1
        for sat_type, count in type_distribution.items():
            template = self.templates[sat_type]
            
            for i in range(count):
                # 确定所在轨道平面
                plane_index = (sat_id_counter - 1) % num_planes
                # 确定在平面内的位置
                sat_in_plane = (sat_id_counter - 1) // num_planes
                
                # 计算轨道参数
                raan_deg = plane_index * (360.0 / num_planes)
                true_anomaly_deg = sat_in_plane * (360.0 / sats_per_plane) + \
                                   phase_factor * plane_index * (360.0 / total_satellites)
                
                satellite = {
                    "id": f"SAT_{sat_type.upper()[:8]}_{sat_id_counter:03d}",
                    "type": sat_type,
                    "orbital_elements": {
                        "semi_major_axis_km": 6378.137 + template.altitude_km,
                        "eccentricity": 0.001,
                        "inclination_deg": template.inclination_deg,
                        "raan_deg": raan_deg,
                        "argument_of_perigee_deg": 0.0,
                        "true_anomaly_deg": true_anomaly_deg % 360.0,
                        "epoch": start_epoch
                    },
                    "sensor": {
                        "resolution_m": template.resolution_m,
                        "swath_width_km": template.swath_width_km,
                        "imaging_modes": template.imaging_modes,
                        "agility": template.agility,
                        "constraints": template.constraints
                    },
                    "resources": {
                        "storage_capacity_gb": template.storage_capacity_gb,
                        "downlink_rate_mbps": template.downlink_rate_mbps,
                        "power_capacity_wh": 1200 if "optical" in sat_type else 1500
                    }
                }
                
                satellites.append(satellite)
                sat_id_counter += 1
        
        return satellites
    
    def export_templates(self, output_file: str = "satellites/satellite_templates.json"):
        """导出卫星模板配置"""
        output_path = self.output_dir / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        templates_dict = {
            name: asdict(template)
            for name, template in self.templates.items()
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(templates_dict, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 卫星模板已导出至: {output_path}")
        return output_path
    
    def export_constellation(
        self,
        satellites: List[Dict[str, Any]],
        output_file: str = "satellites/constellation_200.json"
    ):
        """导出星座配置"""
        output_path = self.output_dir / output_file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 统计各型号数量
        type_counts = {}
        for sat in satellites:
            sat_type = sat["type"]
            type_counts[sat_type] = type_counts.get(sat_type, 0) + 1
        
        constellation_data = {
            "metadata": {
                "name": "Mixed Constellation 200",
                "total_satellites": len(satellites),
                "type_distribution": type_counts,
                "simulation_start": "2024-06-01T00:00:00Z",
                "duration_hours": 24,
                "description": "混合星座基准测试配置（分层型：少量超高分辨率+主力高分辨率，光学+SAR）"
            },
            "satellites": satellites
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(constellation_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 星座配置已导出至: {output_path}")
        print(f"  - 总卫星数: {len(satellites)}")
        for sat_type, count in type_counts.items():
            print(f"  - {sat_type}: {count}颗")
        
        return output_path


def main():
    """主函数：生成星座配置"""
    print("=" * 60)
    print("星座配置生成器")
    print("=" * 60)
    
    generator = WalkerConstellationGenerator()
    
    # 1. 导出卫星模板
    print("\n[1/2] 生成卫星模板...")
    generator.export_templates()
    
    # 2. 生成并导出星座
    print("\n[2/2] 生成Walker星座配置...")
    satellites = generator.generate_walker_constellation(
        total_satellites=200,
        num_planes=10,
        phase_factor=1
    )
    generator.export_constellation(satellites)
    
    print("\n" + "=" * 60)
    print("✓ 星座配置生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
