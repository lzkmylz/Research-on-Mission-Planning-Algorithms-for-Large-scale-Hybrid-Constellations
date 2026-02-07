"""
算法结果对比工具

加载不同算法在各场景下的运行结果，并生成性能对比如 DataFrame、CSV。
"""

import json
import pandas as pd
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime


class AlgorithmComparator:
    """算法对比工具"""

    def __init__(self, output_dir: str = "benchmark_dataset/evaluation"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_result_file(self, result_path: str) -> Dict[str, Any]:
        """加载单个结果文件"""
        with open(result_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def compare_scenario_metrics(
        self,
        results: List[Dict[str, Any]]
    ) -> pd.DataFrame:
        """比较单场景下各算法的指标"""
        data = []
        for res in results:
            meta = res.get("metadata", {})
            metrics = res.get("metrics", {})
            
            algo_name = meta.get("algorithm", "unknown")
            
            data.append({
                "Algorithm": algo_name,
                "Completion Rate": metrics.get("task_completion_rate", 0),
                "Total Value": metrics.get("total_value", 0),
                "Runtime (s)": metrics.get("runtime_seconds", 0),
                "Targets Covered": metrics.get("targets_covered", 0),
                "Completion Time (h)": metrics.get("completion_time_hours", 0),
                "Avg Storage Usage": metrics.get("resource_utilization", {}).get("avg_storage_usage", 0),
                "Avg Energy Usage": metrics.get("resource_utilization", {}).get("avg_energy_usage", 0)
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index("Algorithm", inplace=True)
            df.sort_values(by="Completion Rate", ascending=False, inplace=True)
        return df

    def generate_comparison_report(
        self,
        scenario_name: str,
        results: List[Dict[str, Any]],
        output_name: str = "comparison_report.csv"
    ) -> pd.DataFrame:
        """生成并保存对比报告"""
        df = self.compare_scenario_metrics(results)
        
        output_path = self.output_dir / f"{scenario_name}_{output_name}"
        df.to_csv(output_path, encoding='utf-8-sig')
        print(f"✓ 对比报告已保存: {output_path}")
        
        # 简单打印
        print(f"\n[{scenario_name} 对比报告]")
        print("-" * 60)
        print(df.to_string())
        print("-" * 60)
        
        return df

def main():
    """测试对比工具"""
    print("=" * 60)
    print("算法对比工具测试")
    print("=" * 60)
    
    # 构造模拟数据（不同算法在同一场景下的结果）
    mock_results = [
        {
            "metadata": {"algorithm": "GeneticAlgorithm", "scenario": "test"},
            "metrics": {
                "task_completion_rate": 0.85,
                "total_value": 12000,
                "runtime_seconds": 120,
                "targets_covered": 850,
                "completion_time_hours": 18.5,
                "resource_utilization": {"avg_storage_usage": 0.6, "avg_energy_usage": 0.7}
            }
        },
        {
            "metadata": {"algorithm": "TabuSearch", "scenario": "test"},
            "metrics": {
                "task_completion_rate": 0.78,
                "total_value": 11000,
                "runtime_seconds": 45,
                "targets_covered": 780,
                "completion_time_hours": 20.0,
                "resource_utilization": {"avg_storage_usage": 0.5, "avg_energy_usage": 0.6}
            }
        }
    ]
    
    comparator = AlgorithmComparator()
    comparator.generate_comparison_report("test_scenario", mock_results)
    
    print("\n" + "=" * 60)
    print("✓ 测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    main()
