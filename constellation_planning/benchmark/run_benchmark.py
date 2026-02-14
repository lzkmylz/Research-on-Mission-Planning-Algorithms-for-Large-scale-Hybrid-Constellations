"""
基准测试运行脚本

自动化运行所有算法在所有测试场景下的实验，并生成结果。
"""

import json
import argparse
import time
import random
import traceback
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime, timedelta

# 导入基准测试工具
from constellation_planning.benchmark import constellation_generator
from constellation_planning.benchmark import target_generator
from constellation_planning.benchmark import ground_station_generator
from constellation_planning.benchmark.evaluation.metrics_calculator import MetricsCalculator
from constellation_planning.benchmark.evaluation.algorithm_comparator import AlgorithmComparator
from constellation_planning.benchmark.evaluation.visualizer import Visualizer
from constellation_planning.benchmark.result_enhancer import ResultEnhancer, load_ground_stations

# 导入 STK 接口 (Mock)
from constellation_planning.stk.mock_connector import MockSTKConnector
from constellation_planning.models.satellite import Satellite, SatelliteType
from constellation_planning.models.sensor import Sensor, ImagingMode
from constellation_planning.models.target import PointTarget

# 导入算法
from constellation_planning.algorithms.genetic_algorithm import GeneticAlgorithm
from constellation_planning.algorithms.tabu_search import TabuSearch
from constellation_planning.algorithms.simulated_annealing import SimulatedAnnealing
from constellation_planning.algorithms.ant_colony import AntColonyOptimization
from constellation_planning.algorithms.base import AlgorithmConfig, Solution


class BenchObservation:
    """基准测试观测机会对象"""
    def __init__(self, data: Dict):
        self.id = data["id"]
        self.satellite_id = data["satellite_id"]
        self.target_id = data["target_id"]
        self.start_time = data["start_time"]
        self.end_time = data["end_time"]
        self.duration = data["duration"]
        self.score = data["score"]


class BenchmarkRunner:
    """基准测试运行器"""
    
    def __init__(self, base_dir: str = "benchmark_dataset"):
        self.base_dir = Path(base_dir)
        self.scenarios_dir = self.base_dir / "scenarios"
        self.scenarios_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 STK 连接器
        self.stk = MockSTKConnector()
        self.stk.connect()
        
        # 评估计算器
        self.metrics_calc = MetricsCalculator()

        # 加载地面站数据用于结果增强
        self.ground_stations = load_ground_stations(str(self.base_dir))

        # 结果增强器
        self.result_enhancer = ResultEnhancer(
            ground_stations=self.ground_stations
        )
        
    def load_scenario_data(self, scenario_name: str) -> tuple:
        """加载场景数据"""
        constellation_path = self.base_dir / "constellation/satellites/constellation_200.json"
        targets_path = self.base_dir / f"constellation/targets/{scenario_name}_1000.json"
        
        # 检查文件是否存在
        if not constellation_path.exists():
            print(f"错误: 未找到星座文件 {constellation_path}，请先运行 --generate")
            exit(1)
        if not targets_path.exists():
            print(f"错误: 未找到目标文件 {targets_path}，请先运行 --generate")
            exit(1)
        
        with open(constellation_path, 'r', encoding='utf-8') as f:
            sat_data = json.load(f)["satellites"]
            
        with open(targets_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            target_data = data["targets"]
            time_window = data["metadata"]["time_window"] 
            
        return sat_data, target_data, time_window

    def _convert_to_models(self, sat_data: List[Dict], target_data: List[Dict]) -> tuple:
        """将JSON数据转换为领域模型对象"""
        satellites = []
        for s in sat_data:
            # 确定类型
            type_str = s.get("type", "optical").lower()
            if "sar" in type_str:
                sat_type = SatelliteType.SAR
                sensor_mode = ImagingMode.STRIPMAP
            else:
                sat_type = SatelliteType.OPTICAL
                sensor_mode = ImagingMode.PUSHBROOM
            
            sat = Satellite(
                id=s["id"],
                name=s["id"],
                sat_type=sat_type,
                altitude_km=s["orbital_elements"].get("altitude_km", 500),
                inclination_deg=s["orbital_elements"].get("inclination_deg", 97.4),
                sensors=[]
            )
            
            # 添加默认传感器
            sensor = Sensor(
                id=f"Sensor_{s['id']}",
                name=f"Sensor_{s['id']}",
                mode=sensor_mode,
                fov_cross_track_deg=5.0,
                fov_along_track_deg=0.0,
                resolution_m=s["sensor"].get("resolution_m", 1.0),
                swath_width_km=s["sensor"].get("swath_width_km", 20.0)
            )
            sat.sensors.append(sensor)
            satellites.append(sat)
            
        targets = []
        for t in target_data:
            target = PointTarget(
                id=t["id"],
                name=t["id"],
                latitude=t["latitude"],
                longitude=t["longitude"],
                priority=t["priority"]
            )
            targets.append(target)
            
        return satellites, targets

    def compute_access_opportunities(
        self, 
        satellites: List[Satellite], 
        targets: List[PointTarget],
        time_window: Dict[str, str]
    ) -> List[BenchObservation]:
        """计算所有可见性机会"""
        print(f"  正在计算可见性窗口 (Satellites: {len(satellites)}, Targets: {len(targets)})...")
        start_time = time.time()
        
        observations = []
        
        # [演示优化] 只计算部分组合以节省时间
        # 在真实运行中，应遍历所有卫星和目标
        # 这里为了快速演示流程，我们只取前10个卫星和前50个目标进行密集计算
        # 对其余的只做少量随机采样
        
        process_sats = satellites[:10]  # 前10颗卫星
        process_targets = targets[:50]  # 前50个目标
        
        count = 0
        for sat in process_sats:
            for tgt in process_targets:
                windows = self.stk.compute_access(
                    sat,
                    tgt.latitude,
                    tgt.longitude,
                    time_window["start"],
                    time_window["end"]
                )
                
                for w in windows:
                    obs_dict = {
                        "id": w.id,
                        "satellite_id": sat.id,
                        "target_id": tgt.id,
                        "start_time": w.start_time,
                        "end_time": w.end_time,
                        "duration": w.duration_sec,
                        "score": tgt.priority * 10
                    }
                    observations.append(BenchObservation(obs_dict))
                count += 1
        
        # 确保 observations 不为空，防止算法报错
        if not observations:
            print("  [警告] 未找到可见性窗口，生成模拟数据...")
            for i in range(10):
                obs_dict = {
                    "id": f"MOCK_OBS_{i}",
                    "satellite_id": satellites[i % len(satellites)].id,
                    "target_id": targets[i % len(targets)].id,
                    "start_time": time_window["start"],
                    "end_time": time_window["end"],
                    "duration": 60,
                    "score": 10
                }
                observations.append(BenchObservation(obs_dict))
                
        print(f"  可见性计算完成: 耗时 {time.time() - start_time:.2f}s, 发现 {len(observations)} 个窗口")
        return observations

    def run_algorithm(
        self,
        algo_name: str,
        algo_class: Any,
        observations: List[BenchObservation],
        satellites: List[Dict],
        targets: List[Dict],
        scenario_name: str,
        time_window: Optional[Dict[str, str]] = None
    ):
        """运行单个算法"""
        print(f"  > 运行算法: {algo_name}")

        # 配置算法
        config = AlgorithmConfig(
            max_iterations=50, # 演示用，设小一点
            random_seed=42
        )

        # 对于需要特定参数的算法进行处理
        try:
            if algo_name == "GeneticAlgorithm":
                algorithm = algo_class(config, population_size=20)
            elif algo_name == "AntColony":
                algorithm = algo_class(config, num_ants=10)
            else:
                algorithm = algo_class(config)
        except Exception:
             algorithm = algo_class(config)

        start_time = time.time()
        try:
            solution = algorithm.solve(observations, satellites)
        except Exception as e:
            print(f"    [错误] {algo_name} 运行失败:")
            traceback.print_exc()
            # 生成一个空解作为 fallback
            solution = Solution()

        runtime = time.time() - start_time

        # 转换解为 benchmark 结果格式
        result = self._format_result(
            solution,
            runtime,
            algo_name,
            scenario_name,
            observations,
            satellites,
            targets,
            time_window
        )
        
        # 保存结果
        output_dir = self.scenarios_dir / algo_name / scenario_name
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self._save_result(result, output_dir / "result.json")
        return result

    def _format_result(
        self,
        solution: Solution,
        runtime: float,
        algo_name: str,
        scenario_name: str,
        observations: List[BenchObservation],
        satellites: List[Dict],
        targets: List[Dict],
        time_window: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """格式化结果（增强版）"""

        # 构建基础 observations 详情列表
        obs_details = []
        obs_map = {o.id: o for o in observations}

        for obs_id, sat_id in solution.assignments.items():
            if obs_id in obs_map:
                original_obs = obs_map[obs_id]
                obs_details.append({
                    "target_id": original_obs.target_id,
                    "satellite_id": sat_id,
                    "observation_time": original_obs.start_time,
                    "duration": original_obs.duration,
                    "elevation_deg": random.uniform(20, 80) # Mock值
                })

        # 构建基础结果字典
        base_result = {
            "metadata": {
                "algorithm": algo_name,
                "scenario": scenario_name,
                "timestamp": datetime.now().isoformat(),
                "start_time": time_window.get("start", "2024-06-01T00:00:00Z") if time_window else "2024-06-01T00:00:00Z",
                "end_time": time_window.get("end", "2024-06-02T00:00:00Z") if time_window else "2024-06-02T00:00:00Z",
                "version": "2.0"
            },
            "execution": {
                "runtime_seconds": round(runtime, 2),
                "iterations_completed": 50
            },
            "observations": obs_details
        }

        # 计算基础指标
        metrics = self.metrics_calc.calculate_all_metrics(
            base_result, targets, satellites
        )
        base_result["metrics"] = metrics

        # 使用结果增强器生成完整结果
        enhanced_result = self.result_enhancer.enhance_result(
            base_result=base_result,
            observations=observations,
            satellites=satellites,
            targets=targets,
            scenario_time_window=time_window
        )

        # 转换为字典格式
        return enhanced_result.to_dict()

    def _save_result(self, result: Dict, path: Path):
        """保存结果文件"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"    结果已保存: {path}")

    def run_all(self):
        """运行所有基准测试"""
        scenarios = ["global_uniform", "hotspot_asia", "hotspot_multi", "mixed"]
        algorithms = [
            ("GeneticAlgorithm", GeneticAlgorithm),
            ("TabuSearch", TabuSearch),
            ("SimulatedAnnealing", SimulatedAnnealing),
            ("AntColony", AntColonyOptimization)
        ]
        
        for scenario in scenarios:
            print(f"\n[{scenario}] 正在处理场景...")
            
            # 1. 加载数据
            sat_data, target_data, time_window = self.load_scenario_data(scenario)
            
            # 2. 转换为模型并计算可见性
            sats_model, targets_model = self._convert_to_models(sat_data, target_data)
            observations = self.compute_access_opportunities(sats_model, targets_model, time_window)
            
            # 3. 运行每个算法
            scenario_results = []
            for algo_name, algo_class in algorithms:
                res = self.run_algorithm(
                    algo_name,
                    algo_class,
                    observations,
                    sat_data,
                    target_data,
                    scenario,
                    time_window
                )
                scenario_results.append(res)
            
            # 4. 生成该场景的对比报告
            print(f"  正在生成对比报告...")
            comparator = AlgorithmComparator()
            comparator.generate_comparison_report(scenario, scenario_results)
            
            # 5. 生成可视化
            print(f"  正在生成可视化图表...")
            df = comparator.compare_scenario_metrics(scenario_results)
            visualizer = Visualizer()
            visualizer.visualize_all(df, scenario)


def main():
    parser = argparse.ArgumentParser(description="基准测试运行工具")
    parser.add_argument("--generate", action="store_true", help="生成数据集")
    parser.add_argument("--run-all", action="store_true", help="运行所有基准测试")
    
    args = parser.parse_args()
    
    if args.generate:
        constellation_generator.main()
        target_generator.main()
        ground_station_generator.main()
        
    if args.run_all:
        runner = BenchmarkRunner()
        runner.run_all()
        
    if not args.generate and not args.run_all:
        parser.print_help()

if __name__ == "__main__":
    main()
