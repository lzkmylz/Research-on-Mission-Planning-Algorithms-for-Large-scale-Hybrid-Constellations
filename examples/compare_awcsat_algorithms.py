#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AWCSAT算法对比演示

比较AWCSAT与SA、TS算法在模拟任务规划问题上的性能
"""

import sys
import time
import random
import numpy as np
from dataclasses import dataclass

sys.path.insert(0, '/Users/zhaolin/Documents/职称论文/Paper1')

from constellation_planning.algorithms import (
    AWCSAT, AWCSATConfig, AWCSATSolution,
    SimulatedAnnealing, TabuSearch,
    AlgorithmConfig
)


@dataclass
class MockTask:
    """模拟观测任务"""
    id: str
    priority: float
    imaging_opportunities: int  # 可用的成像机会数
    transmission_opportunities: int  # 可用的数传机会数
    
    @classmethod
    def random(cls, task_id: int) -> 'MockTask':
        return cls(
            id=str(task_id),
            priority=random.random(),
            imaging_opportunities=random.randint(1, 10),
            transmission_opportunities=random.randint(1, 5)
        )


@dataclass
class MockSatellite:
    """模拟卫星"""
    id: str
    capacity: float
    
    @classmethod
    def random(cls, sat_id: int) -> 'MockSatellite':
        return cls(
            id=str(sat_id),
            capacity=random.uniform(50, 100)
        )


def create_objective_function(tasks: list) -> callable:
    """创建目标函数
    
    模拟论文中的收益模型：
    - 点群目标：任务完成收益之和
    - 考虑任务优先级和成像/数传机会分配
    """
    def objective(solution: AWCSATSolution) -> float:
        total_reward = 0.0
        
        for i, task in enumerate(tasks):
            if i >= solution.num_tasks:
                break
            
            # 获取编码值
            imaging_code = solution.get_imaging_code(i)
            trans_code = solution.get_transmission_code(i)
            extension_rate = solution.decode_strip_extension_rate(i)
            
            # 解码成像和数传机会
            imaging_opp = solution.decode_imaging_opportunity(i, task.imaging_opportunities)
            trans_opp = solution.decode_transmission_opportunity(i, task.transmission_opportunities)
            
            # 只有成像和数传都有效才计算收益
            if imaging_opp > 0 and trans_opp > 0:
                # 基础收益 = 优先级
                base_reward = task.priority
                
                # 条带延长率奖励（模拟点群目标合并效果）
                extension_bonus = extension_rate * 0.2
                
                # 总收益
                total_reward += base_reward + extension_bonus
        
        return total_reward
    
    return objective


def run_comparison(num_tasks: int = 50, num_satellites: int = 5, seed: int = 42):
    """运行算法对比实验
    
    Args:
        num_tasks: 任务数量
        num_satellites: 卫星数量
        seed: 随机种子
    """
    print("=" * 60)
    print("AWCSAT算法对比实验")
    print("=" * 60)
    print(f"任务数量: {num_tasks}")
    print(f"卫星数量: {num_satellites}")
    print(f"随机种子: {seed}")
    print()
    
    # 设置随机种子
    random.seed(seed)
    np.random.seed(seed)
    
    # 生成测试数据
    tasks = [MockTask.random(i) for i in range(num_tasks)]
    satellites = [MockSatellite.random(i) for i in range(num_satellites)]
    
    # 创建目标函数
    objective_func = create_objective_function(tasks)
    
    # 配置参数（论文推荐参数的缩小版，用于快速演示）
    iterations = 500
    results = {}
    
    # 1. AWCSAT算法
    print("运行 AWCSAT 算法...")
    awcsat_config = AWCSATConfig(
        outer_loops=iterations,
        initial_inner_loops=20,
        tabu_tenure=5,
        initial_temp_coef=0.9,
        random_seed=seed
    )
    awcsat = AWCSAT(awcsat_config, objective_func=objective_func)
    
    start_time = time.time()
    awcsat_result = awcsat.solve(tasks, satellites)
    awcsat_time = time.time() - start_time
    
    awcsat_best = awcsat.best_awcsat_solution.objective_value if awcsat.best_awcsat_solution else 0
    results['AWCSAT'] = {
        'best': awcsat_best,
        'time': awcsat_time,
        'iterations': len(awcsat.history)
    }
    print(f"  最优收益: {awcsat_best:.4f}")
    print(f"  耗时: {awcsat_time:.2f}s")
    print()
    
    # 2. SA算法
    print("运行 SA 算法...")
    sa_config = AlgorithmConfig(
        max_iterations=iterations * 20,  # SA每次迭代更新一次
        random_seed=seed
    )
    sa = SimulatedAnnealing(
        config=sa_config,
        initial_temp=100.0,
        cooling_rate=0.995,
        min_temp=0.01
    )
    
    start_time = time.time()
    sa_result = sa.solve(tasks, satellites)
    sa_time = time.time() - start_time
    
    results['SA'] = {
        'best': sa_result.objective_value,
        'time': sa_time,
        'iterations': len(sa.history)
    }
    print(f"  最优收益: {sa_result.objective_value:.4f}")
    print(f"  耗时: {sa_time:.2f}s")
    print()
    
    # 3. TS算法
    print("运行 TS 算法...")
    ts_config = AlgorithmConfig(
        max_iterations=iterations * 20,
        random_seed=seed
    )
    ts = TabuSearch(
        config=ts_config,
        tabu_tenure=10,
        neighborhood_size=20
    )
    
    start_time = time.time()
    ts_result = ts.solve(tasks, satellites)
    ts_time = time.time() - start_time
    
    results['TS'] = {
        'best': ts_result.objective_value,
        'time': ts_time,
        'iterations': len(ts.history)
    }
    print(f"  最优收益: {ts_result.objective_value:.4f}")
    print(f"  耗时: {ts_time:.2f}s")
    print()
    
    # 结果汇总
    print("=" * 60)
    print("结果汇总")
    print("=" * 60)
    print(f"{'算法':<12} {'最优收益':<15} {'耗时(s)':<12} {'迭代次数':<12}")
    print("-" * 60)
    for algo, data in results.items():
        print(f"{algo:<12} {data['best']:<15.4f} {data['time']:<12.2f} {data['iterations']:<12}")
    print()
    
    # 找出最优算法
    best_algo = max(results.keys(), key=lambda x: results[x]['best'])
    print(f"最优算法: {best_algo} (收益: {results[best_algo]['best']:.4f})")
    
    return results


if __name__ == "__main__":
    # 运行对比实验
    results = run_comparison(num_tasks=50, num_satellites=5, seed=42)
    
    print("\n" + "=" * 60)
    print("注意：这是简化的演示实验")
    print("论文中的完整实验使用更大规模的场景和更多迭代次数")
    print("=" * 60)
