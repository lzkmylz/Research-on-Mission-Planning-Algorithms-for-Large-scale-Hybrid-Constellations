"""
评估指标计算器

计算任务规划解的六大评估指标。
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime
from collections import Counter


class MetricsCalculator:
    """评估指标计算器"""
    
    def __init__(self):
        # 价值函数权重
        self.weights = {
            "priority": 0.4,
            "elevation": 0.2,
            "resolution": 0.2,
            "timeliness": 0.2
        }
    
    def calculate_task_completion_rate(
        self,
        solution: Dict[str, Any],
        targets: List[Dict[str, Any]]
    ) -> float:
        """
        计算任务完成率
        
        Args:
            solution: 算法求解结果
            targets: 目标列表
            
        Returns:
            完成率 (0-1)
        """
        if not targets:
            return 0.0
        
        observations = solution.get("observations", [])
        observed_targets = set(obs["target_id"] for obs in observations)
        
        return len(observed_targets) / len(targets)
    
    def calculate_total_value(
        self,
        solution: Dict[str, Any],
        targets: Dict[str, Dict[str, Any]]
    ) -> float:
        """
        计算总收益
        
        Args:
            solution: 算法求解结果
            targets: 目标字典 (target_id -> target_info)
            
        Returns:
            总收益值
        """
        total_value = 0.0
        observations = solution.get("observations", [])
        
        # 获取时间窗口信息
        start_time = self._parse_time(solution.get("metadata", {}).get("start_time", "2024-06-01T00:00:00Z"))
        
        for obs in observations:
            target_id = obs["target_id"]
            target = targets.get(target_id, {})
            
            # 优先级分数 (1-5 归一化到 0-1)
            priority = target.get("priority", 1)
            priority_score = (priority - 1) / 4.0
            
            # 仰角分数 (归一化)
            elevation = obs.get("elevation_deg", 30)
            elevation_score = (elevation - 15) / (90 - 15)  # 15度到90度
            elevation_score = max(0, min(1, elevation_score))
            
            # 分辨率分数 (假设更高分辨率更好)
            # 这里简化处理，实际应根据卫星类型判断
            resolution_score = 0.8  # 简化
            
            # 时效性分数 (越早完成越好)
            obs_time = self._parse_time(obs.get("observation_time", "2024-06-01T12:00:00Z"))
            time_diff = (obs_time - start_time).total_seconds()
            max_time = 24 * 3600  # 24小时
            timeliness_score = 1.0 - (time_diff / max_time)
            timeliness_score = max(0, min(1, timeliness_score))
            
            # 加权计算价值
            value = (
                self.weights["priority"] * priority_score +
                self.weights["elevation"] * elevation_score +
                self.weights["resolution"] * resolution_score +
                self.weights["timeliness"] * timeliness_score
            ) * 100  # 放大到0-100
            
            total_value += value
        
        return round(total_value, 2)
    
    def calculate_resource_utilization(
        self,
        solution: Dict[str, Any],
        satellites: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        计算资源利用率
        
        Args:
            solution: 算法求解结果
            satellites: 卫星列表
            
        Returns:
            资源利用率字典
        """
        observations = solution.get("observations", [])
        
        # 按卫星统计观测次数
        sat_obs_count = Counter(obs["satellite_id"] for obs in observations)
        
        # 简化计算：假设每次观测消耗固定存储和能源
        storage_per_obs = 10  # GB
        energy_per_obs = 50   # Wh
        
        sat_utilization = {}
        for sat in satellites:
            sat_id = sat["id"]
            num_obs = sat_obs_count.get(sat_id, 0)
            
            storage_cap = sat["resources"]["storage_capacity_gb"]
            power_cap = sat["resources"]["power_capacity_wh"]
            
            storage_used = num_obs * storage_per_obs
            energy_used = num_obs * energy_per_obs
            
            sat_utilization[sat_id] = {
                "storage": min(1.0, storage_used / storage_cap),
                "energy": min(1.0, energy_used / power_cap)
            }
        
        # 计算平均值
        if sat_utilization:
            avg_storage = sum(u["storage"] for u in sat_utilization.values()) / len(sat_utilization)
            avg_energy = sum(u["energy"] for u in sat_utilization.values()) / len(sat_utilization)
            max_storage = max(u["storage"] for u in sat_utilization.values())
            max_energy = max(u["energy"] for u in sat_utilization.values())
        else:
            avg_storage = avg_energy = max_storage = max_energy = 0.0
        
        return {
            "avg_storage_usage": round(avg_storage, 3),
            "max_storage_usage": round(max_storage, 3),
            "avg_energy_usage": round(avg_energy, 3),
            "max_energy_usage": round(max_energy, 3)
        }
    
    def calculate_revisit_distribution(
        self,
        solution: Dict[str, Any],
        targets: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        计算重访次数分布
        
        Args:
            solution: 算法求解结果
            targets: 目标列表
            
        Returns:
            重访次数分布
        """
        observations = solution.get("observations", [])
        
        # 统计每个目标被观测次数
        revisit_count = Counter(obs["target_id"] for obs in observations)
        
        # 分类统计
        distribution = {
            "0_times": 0,
            "1_time": 0,
            "2_times": 0,
            "3+_times": 0
        }
        
        for target in targets:
            target_id = target["id"]
            count = revisit_count.get(target_id, 0)
            
            if count == 0:
                distribution["0_times"] += 1
            elif count == 1:
                distribution["1_time"] += 1
            elif count == 2:
                distribution["2_times"] += 1
            else:
                distribution["3+_times"] += 1
        
        return distribution
    
    def calculate_completion_time(
        self,
        solution: Dict[str, Any]
    ) -> float:
        """
        计算完成观测用时（小时）
        
        Args:
            solution: 算法求解结果
            
        Returns:
            完成时间（小时）
        """
        observations = solution.get("observations", [])
        if not observations:
            return 0.0
        
        start_time = self._parse_time(solution.get("metadata", {}).get("start_time", "2024-06-01T00:00:00Z"))
        
        # 找到最后一次观测时间
        obs_times = [self._parse_time(obs.get("observation_time", "2024-06-01T00:00:00Z")) 
                     for obs in observations]
        last_obs_time = max(obs_times)
        
        # 计算时间差（小时）
        time_diff = (last_obs_time - start_time).total_seconds() / 3600
        
        return round(time_diff, 2)
    
    def calculate_all_metrics(
        self,
        solution: Dict[str, Any],
        targets: List[Dict[str, Any]],
        satellites: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        计算所有评估指标
        
        Args:
            solution: 算法求解结果
            targets: 目标列表
            satellites: 卫星列表
            
        Returns:
            完整的评估指标字典
        """
        # 将targets转为字典便于查找
        targets_dict = {t["id"]: t for t in targets}
        
        # 计算各项指标
        completion_rate = self.calculate_task_completion_rate(solution, targets)
        total_value = self.calculate_total_value(solution, targets_dict)
        resource_util = self.calculate_resource_utilization(solution, satellites)
        revisit_dist = self.calculate_revisit_distribution(solution, targets)
        completion_time = self.calculate_completion_time(solution)
        
        # 运行时间从solution中获取
        runtime = solution.get("execution", {}).get("runtime_seconds", 0)
        
        # 统计覆盖的目标数
        observations = solution.get("observations", [])
        observed_targets = set(obs["target_id"] for obs in observations)
        
        # 按卫星类型分解统计
        sat_type_dict = {sat["id"]: sat["type"] for sat in satellites}
        type_breakdown = {}
        for obs in observations:
            sat_type = sat_type_dict.get(obs["satellite_id"], "unknown")
            if sat_type not in type_breakdown:
                type_breakdown[sat_type] = {"observations": 0, "total_value": 0}
            type_breakdown[sat_type]["observations"] += 1
        
        # 计算平均价值
        for sat_type in type_breakdown:
            if type_breakdown[sat_type]["observations"] > 0:
                type_breakdown[sat_type]["avg_value"] = round(
                    total_value / len(observations), 2
                )
        
        return {
            "task_completion_rate": round(completion_rate, 3),
            "runtime_seconds": runtime,
            "total_value": total_value,
            "targets_covered": len(observed_targets),
            "targets_total": len(targets),
            "resource_utilization": resource_util,
            "revisit_distribution": revisit_dist,
            "completion_time_hours": completion_time,
            "detailed_breakdown": type_breakdown
        }
    
    def _parse_time(self, time_str: str) -> datetime:
        """解析ISO时间字符串"""
        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))


def load_data(constellation_file: str, targets_file: str) -> tuple:
    """加载星座和目标数据"""
    with open(constellation_file, 'r', encoding='utf-8') as f:
        constellation_data = json.load(f)
    
    with open(targets_file, 'r', encoding='utf-8') as f:
        targets_data = json.load(f)
    
    return constellation_data["satellites"], targets_data["targets"]


def main():
    """测试评估指标计算"""
    print("=" * 60)
    print("评估指标计算器测试")
    print("=" * 60)
    
    # 创建模拟解
    mock_solution = {
        "metadata": {
            "algorithm": "test",
            "scenario": "test",
            "start_time": "2024-06-01T00:00:00Z"
        },
        "execution": {
            "runtime_seconds": 100.5
        },
        "observations": [
            {
                "target_id": "TGT_0001",
                "satellite_id": "SAT_ULTRA_HI_001",
                "observation_time": "2024-06-01T03:00:00Z",
                "elevation_deg": 45.0
            },
            {
                "target_id": "TGT_0002",
                "satellite_id": "SAT_HIGH_RE_001",
                "observation_time": "2024-06-01T05:00:00Z",
                "elevation_deg": 30.0
            }
        ]
    }
    
    # 加载真实数据
    satellites, targets = load_data(
        "benchmark_dataset/constellation/satellites/constellation_200.json",
        "benchmark_dataset/constellation/targets/global_uniform_1000.json"
    )
    
    # 计算指标
    calculator = MetricsCalculator()
    metrics = calculator.calculate_all_metrics(mock_solution, targets, satellites)
    
    print("\n计算结果:")
    print(json.dumps(metrics, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("✓ 测试完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
