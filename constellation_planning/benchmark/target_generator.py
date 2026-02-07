"""
目标任务生成器

生成不同分布模式的点目标，用于基准测试场景。
"""

import json
import random
import numpy as np
from pathlib import Path
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, asdict


@dataclass
class PointTarget:
    """点目标"""
    id: str
    type: str
    latitude: float
    longitude: float
    priority: int
    time_window: Dict[str, str]
    observation_requirements: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        if self.observation_requirements is None:
            result["observation_requirements"] = {
                "min_resolution_m": 5.0,
                "min_elevation_deg": 15,
                "max_cloud_cover": 0.3
            }
        return result


class TargetGenerator:
    """目标生成器"""
    
    def __init__(self, output_dir: str = "benchmark_dataset/constellation/targets"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.start_time = "2024-06-01T00:00:00Z"
        self.end_time = "2024-06-02T00:00:00Z"
    
    def generate_uniform(
        self,
        num_targets: int = 1000,
        lat_range: Tuple[float, float] = (-60, 60),
        lon_range: Tuple[float, float] = (-180, 180),
        seed: int = 42
    ) -> List[PointTarget]:
        """
        生成全球均匀分布的点目标
        
        Args:
            num_targets: 目标数量
            lat_range: 纬度范围
            lon_range: 经度范围
            seed: 随机种子
            
        Returns:
            目标列表
        """
        random.seed(seed)
        np.random.seed(seed)
        
        targets = []
        for i in range(num_targets):
            lat = random.uniform(lat_range[0], lat_range[1])
            lon = random.uniform(lon_range[0], lon_range[1])
            priority = random.randint(1, 5)
            
            target = PointTarget(
                id=f"TGT_{i+1:04d}",
                type="point",
                latitude=round(lat, 4),
                longitude=round(lon, 4),
                priority=priority,
                time_window={
                    "start": self.start_time,
                    "end": self.end_time
                }
            )
            targets.append(target)
        
        return targets
    
    def generate_hotspot_asia(
        self,
        num_targets: int = 1000,
        seed: int = 42
    ) -> List[PointTarget]:
        """
        生成亚太热点分布
        
        Args:
            num_targets: 总目标数
            seed: 随机种子
            
        Returns:
            目标列表
        """
        random.seed(seed)
        np.random.seed(seed)
        
        targets = []
        target_id = 1
        
        # 热点区域配置（800个目标）
        hotspot_config = [
            # 中国东部 35% = 280个
            {
                "count": 280,
                "lat_range": (20, 45),
                "lon_range": (110, 125),
                "priority_range": (3, 5),
                "name": "China East"
            },
            # 东南亚 20% = 160个
            {
                "count": 160,
                "lat_range": (0, 20),
                "lon_range": (95, 115),
                "priority_range": (3, 5),
                "name": "Southeast Asia"
            },
            # 日韩 15% = 120个
            {
                "count": 120,
                "lat_range": (30, 45),
                "lon_range": (125, 140),
                "priority_range": (3, 5),
                "name": "Japan Korea"
            },
            # 印度及南亚 30% = 240个
            {
                "count": 240,
                "lat_range": (8, 35),
                "lon_range": (68, 95),
                "priority_range": (3, 5),
                "name": "India South Asia"
            }
        ]
        
        # 生成热点区域目标
        for config in hotspot_config:
            for _ in range(config["count"]):
                lat = random.uniform(config["lat_range"][0], config["lat_range"][1])
                lon = random.uniform(config["lon_range"][0], config["lon_range"][1])
                priority = random.randint(config["priority_range"][0], config["priority_range"][1])
                
                target = PointTarget(
                    id=f"TGT_{target_id:04d}",
                    type="point",
                    latitude=round(lat, 4),
                    longitude=round(lon, 4),
                    priority=priority,
                    time_window={
                        "start": self.start_time,
                        "end": self.end_time
                    }
                )
                targets.append(target)
                target_id += 1
        
        # 全球分散 200个
        scattered_count = num_targets - len(targets)
        for _ in range(scattered_count):
            lat = random.uniform(-60, 60)
            lon = random.uniform(-180, 180)
            priority = random.randint(1, 3)  # 较低优先级
            
            target = PointTarget(
                id=f"TGT_{target_id:04d}",
                type="point",
                latitude=round(lat, 4),
                longitude=round(lon, 4),
                priority=priority,
                time_window={
                    "start": self.start_time,
                    "end": self.end_time
                }
            )
            targets.append(target)
            target_id += 1
        
        return targets
    
    def generate_multi_hotspot(
        self,
        num_targets: int = 1000,
        seed: int = 42
    ) -> List[PointTarget]:
        """
        生成多热点区域分布
        
        Args:
            num_targets: 总目标数
            seed: 随机种子
            
        Returns:
            目标列表
        """
        random.seed(seed)
        np.random.seed(seed)
        
        targets = []
        target_id = 1
        
        # 五大热点区域（各150个）
        hotspot_regions = [
            {
                "name": "Asia Pacific",
                "count": 150,
                "lat_range": (20, 45),
                "lon_range": (110, 140)
            },
            {
                "name": "Europe",
                "count": 150,
                "lat_range": (40, 60),
                "lon_range": (-10, 30)
            },
            {
                "name": "North America",
                "count": 150,
                "lat_range": (25, 50),
                "lon_range": (-130, -70)
            },
            {
                "name": "Middle East",
                "count": 150,
                "lat_range": (15, 40),
                "lon_range": (30, 60)
            },
            {
                "name": "South America",
                "count": 150,
                "lat_range": (-35, 5),
                "lon_range": (-75, -35)
            }
        ]
        
        # 生成热点区域目标
        for region in hotspot_regions:
            for _ in range(region["count"]):
                lat = random.uniform(region["lat_range"][0], region["lat_range"][1])
                lon = random.uniform(region["lon_range"][0], region["lon_range"][1])
                priority = random.randint(3, 5)
                
                target = PointTarget(
                    id=f"TGT_{target_id:04d}",
                    type="point",
                    latitude=round(lat, 4),
                    longitude=round(lon, 4),
                    priority=priority,
                    time_window={
                        "start": self.start_time,
                        "end": self.end_time
                    }
                )
                targets.append(target)
                target_id += 1
        
        # 全球分散 250个
        scattered_count = num_targets - len(targets)
        for _ in range(scattered_count):
            lat = random.uniform(-60, 60)
            lon = random.uniform(-180, 180)
            priority = random.randint(1, 3)
            
            target = PointTarget(
                id=f"TGT_{target_id:04d}",
                type="point",
                latitude=round(lat, 4),
                longitude=round(lon, 4),
                priority=priority,
                time_window={
                    "start": self.start_time,
                    "end": self.end_time
                }
            )
            targets.append(target)
            target_id += 1
        
        return targets
    
    def generate_mixed(
        self,
        num_targets: int = 1000,
        seed: int = 42
    ) -> List[PointTarget]:
        """
        生成混合分布（沿海+内陆+随机）
        
        Args:
            num_targets: 总目标数
            seed: 随机种子
            
        Returns:
            目标列表
        """
        random.seed(seed)
        np.random.seed(seed)
        
        targets = []
        target_id = 1
        
        # 沿海区域聚集 500个
        coastal_regions = [
            {"lat_range": (30, 45), "lon_range": (115, 125), "count": 100},  # 中国沿海
            {"lat_range": (25, 45), "lon_range": (-125, -70), "count": 150},  # 美国东西海岸
            {"lat_range": (40, 60), "lon_range": (-10, 20), "count": 100},    # 欧洲沿海
            {"lat_range": (30, 40), "lon_range": (130, 140), "count": 50},    # 日本
            {"lat_range": (-40, -20), "lon_range": (110, 155), "count": 100}  # 澳大利亚
        ]
        
        for region in coastal_regions:
            for _ in range(region["count"]):
                lat = random.uniform(region["lat_range"][0], region["lat_range"][1])
                lon = random.uniform(region["lon_range"][0], region["lon_range"][1])
                priority = random.randint(3, 5)
                
                target = PointTarget(
                    id=f"TGT_{target_id:04d}",
                    type="point",
                    latitude=round(lat, 4),
                    longitude=round(lon, 4),
                    priority=priority,
                    time_window={
                        "start": self.start_time,
                        "end": self.end_time
                    }
                )
                targets.append(target)
                target_id += 1
        
        # 内陆城市 300个
        inland_cities = [
            {"lat": 55.75, "lon": 37.62, "name": "Moscow"},
            {"lat": 28.61, "lon": 77.21, "name": "Delhi"},
            {"lat": 41.88, "lon": -87.63, "name": "Chicago"},
            {"lat": 39.90, "lon": 116.40, "name": "Beijing"}
        ]
        
        for _ in range(300):
            # 在主要内陆城市周边生成目标
            city = random.choice(inland_cities)
            lat = city["lat"] + random.uniform(-5, 5)
            lon = city["lon"] + random.uniform(-5, 5)
            priority = random.randint(2, 4)
            
            target = PointTarget(
                id=f"TGT_{target_id:04d}",
                type="point",
                latitude=round(lat, 4),
                longitude=round(lon, 4),
                priority=priority,
                time_window={
                    "start": self.start_time,
                    "end": self.end_time
                }
            )
            targets.append(target)
            target_id += 1
        
        # 随机分布 200个
        for _ in range(200):
            lat = random.uniform(-60, 60)
            lon = random.uniform(-180, 180)
            priority = random.randint(1, 3)
            
            target = PointTarget(
                id=f"TGT_{target_id:04d}",
                type="point",
                latitude=round(lat, 4),
                longitude=round(lon, 4),
                priority=priority,
                time_window={
                    "start": self.start_time,
                    "end": self.end_time
                }
            )
            targets.append(target)
            target_id += 1
        
        return targets
    
    def export_targets(
        self,
        targets: List[PointTarget],
        scenario_name: str,
        filename: str
    ):
        """导出目标配置"""
        output_path = self.output_dir / filename
        
        # 统计信息
        priority_dist = {i: 0 for i in range(1, 6)}
        for target in targets:
            priority_dist[target.priority] += 1
        
        targets_data = {
            "metadata": {
                "scenario": scenario_name,
                "total_targets": len(targets),
                "random_seed": 42,
                "priority_distribution": priority_dist,
                "time_window": {
                    "start": self.start_time,
                    "end": self.end_time
                }
            },
            "targets": [target.to_dict() for target in targets]
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(targets_data, f, indent=2, ensure_ascii=False)
        
        print(f"✓ {scenario_name} 已导出: {output_path}")
        print(f"  - 目标数量: {len(targets)}")
        print(f"  - 优先级分布: {priority_dist}")
        
        return output_path


def main():
    """主函数：生成所有测试场景"""
    print("=" * 60)
    print("目标任务生成器")
    print("=" * 60)
    
    generator = TargetGenerator()
    
    # 场景1: 全球均匀分布
    print("\n[1/4] 生成场景1：全球均匀分布...")
    targets1 = generator.generate_uniform(num_targets=1000, seed=42)
    generator.export_targets(targets1, "global_uniform", "global_uniform_1000.json")
    
    # 场景2: 亚太热点
    print("\n[2/4] 生成场景2：亚太热点...")
    targets2 = generator.generate_hotspot_asia(num_targets=1000, seed=42)
    generator.export_targets(targets2, "hotspot_asia", "hotspot_asia_1000.json")
    
    # 场景3: 多热点
    print("\n[3/4] 生成场景3：多热点区域...")
    targets3 = generator.generate_multi_hotspot(num_targets=1000, seed=42)
    generator.export_targets(targets3, "hotspot_multi", "hotspot_multi_1000.json")
    
    # 场景4: 混合分布
    print("\n[4/4] 生成场景4：混合分布...")
    targets4 = generator.generate_mixed(num_targets=1000, seed=42)
    generator.export_targets(targets4, "mixed", "mixed_1000.json")
    
    print("\n" + "=" * 60)
    print("✓ 所有测试场景生成完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()
