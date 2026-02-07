"""
地面站配置生成器

生成全球地面站网络配置，用于卫星数据下传。
"""

import json
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class GroundStation:
    """地面站"""
    id: str
    name: str
    latitude: float
    longitude: float
    elevation_m: float
    min_elevation_deg: float
    uplink_rate_mbps: float
    downlink_rate_mbps: float
    antenna_diameter_m: float


class GroundStationGenerator:
    """地面站生成器"""
    
    def __init__(self, output_dir: str = "benchmark_dataset/constellation/ground_stations"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_global_network(self) -> List[GroundStation]:
        """
        生成全球地面站网络（8个站点）
        
        Returns:
            地面站列表
        """
        stations = [
            GroundStation(
                id="GS_001",
                name="Beijing Station",
                latitude=40.0,
                longitude=116.4,
                elevation_m=50,
                min_elevation_deg=5,
                uplink_rate_mbps=50,
                downlink_rate_mbps=400,
                antenna_diameter_m=12.0
            ),
            GroundStation(
                id="GS_002",
                name="Melbourne Station",
                latitude=-37.8,
                longitude=144.9,
                elevation_m=30,
                min_elevation_deg=5,
                uplink_rate_mbps=50,
                downlink_rate_mbps=400,
                antenna_diameter_m=12.0
            ),
            GroundStation(
                id="GS_003",
                name="Svalbard Station",
                latitude=78.2,
                longitude=15.6,
                elevation_m=20,
                min_elevation_deg=5,
                uplink_rate_mbps=50,
                downlink_rate_mbps=400,
                antenna_diameter_m=12.0
            ),
            GroundStation(
                id="GS_004",
                name="Alaska Station",
                latitude=64.8,
                longitude=-147.7,
                elevation_m=150,
                min_elevation_deg=5,
                uplink_rate_mbps=50,
                downlink_rate_mbps=400,
                antenna_diameter_m=10.0
            ),
            GroundStation(
                id="GS_005",
                name="Miami Station",
                latitude=25.8,
                longitude=-80.2,
                elevation_m=5,
                min_elevation_deg=5,
                uplink_rate_mbps=50,
                downlink_rate_mbps=400,
                antenna_diameter_m=10.0
            ),
            GroundStation(
                id="GS_006",
                name="Madrid Station",
                latitude=40.4,
                longitude=-3.7,
                elevation_m=600,
                min_elevation_deg=5,
                uplink_rate_mbps=50,
                downlink_rate_mbps=400,
                antenna_diameter_m=12.0
            ),
            GroundStation(
                id="GS_007",
                name="Santiago Station",
                latitude=-33.3,
                longitude=-70.7,
                elevation_m=570,
                min_elevation_deg=5,
                uplink_rate_mbps=50,
                downlink_rate_mbps=400,
                antenna_diameter_m=10.0
            ),
            GroundStation(
                id="GS_008",
                name="Cape Town Station",
                latitude=-33.9,
                longitude=18.4,
                elevation_m=25,
                min_elevation_deg=5,
                uplink_rate_mbps=50,
                downlink_rate_mbps=400,
                antenna_diameter_m=10.0
            )
        ]
        
        return stations
    
    def export_ground_stations(
        self,
        stations: List[GroundStation],
        output_file: str = "stations_global.json"
    ):
        """导出地面站配置"""
        output_path = self.output_dir / output_file
        
        stations_data = {
            "metadata": {
                "total_stations": len(stations),
                "coverage": "global",
                "description": "全球地面站网络，支持数据下传"
            },
            "ground_stations": [asdict(station) for station in stations]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(stations_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ 地面站配置已导出: {output_path}")
        print(f"  - 地面站数量: {len(stations)}")
        for station in stations:
            print(f"  - {station.name}: ({station.latitude:.1f}°, {station.longitude:.1f}°)")
        
        return output_path


def main():
    """主函数：生成地面站配置"""
    print("=" * 60)
    print("地面站配置生成器")
    print("=" * 60)
    
    generator = GroundStationGenerator()
    
    print("\n[1/1] 生成全球地面站网络...")
    stations = generator.generate_global_network()
    generator.export_ground_stations(stations)
    
    print("\n" + "=" * 60)
    print("✓ 地面站配置生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
