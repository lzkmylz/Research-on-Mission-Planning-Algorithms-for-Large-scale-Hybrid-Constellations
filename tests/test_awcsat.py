# -*- coding: utf-8 -*-
"""AWCSAT算法单元测试"""

import pytest
import numpy as np
import math
from unittest.mock import Mock

import sys
sys.path.insert(0, '/Users/zhaolin/Documents/职称论文/Paper1')

from constellation_planning.algorithms.awcsat_solution import AWCSATSolution, generate_initial_solutions
from constellation_planning.algorithms.neighborhood_operators import (
    MoveOperator,
    SamePositionExchangeOperator,
    RandomExchangeOperator,
    WholeRowExchangeOperator,
    NeighborhoodOperatorSet,
)
from constellation_planning.algorithms.awcsat import AWCSAT, AWCSATConfig


class TestAWCSATSolution:
    """AWCSATSolution测试类"""
    
    def test_random_creation(self):
        """测试随机解生成"""
        num_tasks = 10
        sol = AWCSATSolution.random(num_tasks)
        
        assert sol.num_tasks == num_tasks
        assert sol.encoding.shape == (num_tasks, 3)
        assert np.all(sol.encoding >= 0)
        assert np.all(sol.encoding <= 1)
    
    def test_zeros_creation(self):
        """测试全零解生成"""
        num_tasks = 5
        sol = AWCSATSolution.zeros(num_tasks)
        
        assert sol.num_tasks == num_tasks
        assert np.all(sol.encoding == 0)
    
    def test_copy(self):
        """测试解复制"""
        sol = AWCSATSolution.random(5)
        sol.objective_value = 100.0
        
        copied = sol.copy()
        
        assert np.array_equal(copied.encoding, sol.encoding)
        assert copied.objective_value == sol.objective_value
        
        # 修改复制后的解不应影响原解
        copied.encoding[0, 0] = 999
        assert sol.encoding[0, 0] != 999
    
    def test_decode_imaging_opportunity(self):
        """测试成像机会解码"""
        sol = AWCSATSolution.zeros(3)
        sol.encoding[0, 0] = 0.5  # v_i1 = 0.5
        sol.encoding[1, 0] = 1.0  # v_i1 = 1.0
        sol.encoding[2, 0] = 0.1  # v_i1 = 0.1
        
        # ⌈0.5 × 10⌉ = 5
        assert sol.decode_imaging_opportunity(0, 10) == 5
        # ⌈1.0 × 10⌉ = 10
        assert sol.decode_imaging_opportunity(1, 10) == 10
        # ⌈0.1 × 10⌉ = 1
        assert sol.decode_imaging_opportunity(2, 10) == 1
    
    def test_decode_strip_extension_rate(self):
        """测试条带延长率解码"""
        sol = AWCSATSolution.zeros(2)
        sol.encoding[0, 2] = 0.0  # v_i3 = 0
        sol.encoding[1, 2] = 1.0  # v_i3 = 1
        
        # r_max - v_i3 × (r_max - r_min) = 1.0 - 0 × (1.0 - 0) = 1.0
        assert sol.decode_strip_extension_rate(0, r_max=1.0, r_min=0.0) == 1.0
        # r_max - v_i3 × (r_max - r_min) = 1.0 - 1.0 × (1.0 - 0) = 0.0
        assert sol.decode_strip_extension_rate(1, r_max=1.0, r_min=0.0) == 0.0
    
    def test_generate_initial_solutions(self):
        """测试初始解集生成"""
        solutions = generate_initial_solutions(num_tasks=10, n=5)
        
        assert len(solutions) == 5
        for sol in solutions:
            assert sol.num_tasks == 10


class TestNeighborhoodOperators:
    """邻域算子测试类"""
    
    def test_move_operator(self):
        """测试移动算子"""
        np.random.seed(42)
        sol = AWCSATSolution.random(5)
        original_encoding = sol.encoding.copy()
        
        op = MoveOperator()
        neighbor = op.apply(sol)
        
        # 原解不应被修改
        assert np.array_equal(sol.encoding, original_encoding)
        
        # 邻域解应该只有一个位置不同
        diff = neighbor.encoding != sol.encoding
        assert diff.sum() == 1
    
    def test_same_position_exchange_operator(self):
        """测试同位交换算子"""
        np.random.seed(42)
        sol = AWCSATSolution.random(5)
        original_encoding = sol.encoding.copy()
        
        op = SamePositionExchangeOperator()
        neighbor = op.apply(sol)
        
        # 原解不应被修改
        assert np.array_equal(sol.encoding, original_encoding)
        
        # 邻域解应该有两个位置不同（同一列的两个值交换）
        diff = neighbor.encoding != sol.encoding
        assert diff.sum() == 2
    
    def test_random_exchange_operator(self):
        """测试随机交换算子"""
        np.random.seed(42)
        sol = AWCSATSolution.random(5)
        original_encoding = sol.encoding.copy()
        
        op = RandomExchangeOperator()
        neighbor = op.apply(sol)
        
        # 原解不应被修改
        assert np.array_equal(sol.encoding, original_encoding)
    
    def test_whole_row_exchange_operator(self):
        """测试整行交换算子"""
        np.random.seed(42)
        sol = AWCSATSolution.random(5)
        original_encoding = sol.encoding.copy()
        
        op = WholeRowExchangeOperator()
        neighbor = op.apply(sol)
        
        # 原解不应被修改
        assert np.array_equal(sol.encoding, original_encoding)
        
        # 邻域解应该有两行被交换
        diff_rows = np.any(neighbor.encoding != sol.encoding, axis=1)
        assert diff_rows.sum() == 2
    
    def test_operator_set_random_select(self):
        """测试算子集随机选择"""
        op_set = NeighborhoodOperatorSet()
        
        # 应该有4种算子
        assert len(op_set) == 4
        
        # 随机选择应返回有效算子
        for _ in range(10):
            op = op_set.random_select()
            assert isinstance(op, (
                MoveOperator,
                SamePositionExchangeOperator,
                RandomExchangeOperator,
                WholeRowExchangeOperator
            ))


class TestAWCSATTemperature:
    """AWCSAT温度计算测试类"""
    
    def test_initial_temperature_formula(self):
        """测试初始温度公式: T0 = -ΔE / ln(q)"""
        # 模拟参数
        delta_E = 100.0
        q = 0.9
        
        # 期望值: T0 = -100 / ln(0.9) ≈ 948.68
        expected_T0 = -delta_E / math.log(q)
        
        assert expected_T0 > 0
        assert abs(expected_T0 - 948.68) < 1.0
    
    def test_metropolis_accept_better_solution(self):
        """测试Metropolis准则：更好的解直接接受"""
        config = AWCSATConfig(outer_loops=10, initial_inner_loops=5)
        algo = AWCSAT(config)
        
        # 设置算法状态
        algo.T0 = 100.0
        algo.current_temp = 50.0
        algo.E_avg = 50.0
        algo.E_min = 0.0
        
        # 创建当前解和更好的邻域解
        current = AWCSATSolution.random(5)
        current.objective_value = 10.0
        algo.current_solution = current
        
        neighbor = AWCSATSolution.random(5)
        neighbor.objective_value = 20.0  # 更好
        
        # 更好的解应该直接接受
        assert algo._metropolis_accept(neighbor) == True
    
    def test_metropolis_accept_worse_solution_probability(self):
        """测试Metropolis准则：较差的解概率接受"""
        np.random.seed(42)
        config = AWCSATConfig(outer_loops=10, initial_inner_loops=5)
        algo = AWCSAT(config)
        
        # 设置高温
        algo.T0 = 1000.0
        algo.current_temp = 500.0
        algo.E_avg = 50.0
        algo.E_min = 0.0
        
        current = AWCSATSolution.random(5)
        current.objective_value = 20.0
        algo.current_solution = current
        
        neighbor = AWCSATSolution.random(5)
        neighbor.objective_value = 18.0  # 稍差
        
        # 高温下应该有较高概率接受较差解
        accept_count = sum(
            algo._metropolis_accept(neighbor) 
            for _ in range(100)
        )
        
        # 应该有一定比例被接受
        assert accept_count > 0


class TestAWCSATAlgorithm:
    """AWCSAT算法集成测试类"""
    
    def test_algorithm_creation(self):
        """测试算法创建"""
        config = AWCSATConfig(
            outer_loops=100,
            initial_inner_loops=10,
            tabu_tenure=5
        )
        algo = AWCSAT(config)
        
        assert algo.awcsat_config.outer_loops == 100
        assert algo.awcsat_config.initial_inner_loops == 10
        assert algo.awcsat_config.tabu_tenure == 5
    
    def test_algorithm_solve_simple(self):
        """测试算法求解简单问题"""
        np.random.seed(42)
        
        # 创建模拟任务
        class MockTask:
            def __init__(self, task_id):
                self.id = str(task_id)
                self.priority = np.random.random()
        
        class MockSatellite:
            def __init__(self, sat_id):
                self.id = str(sat_id)
        
        tasks = [MockTask(i) for i in range(20)]
        satellites = [MockSatellite(i) for i in range(3)]
        
        # 创建算法（小规模测试）
        config = AWCSATConfig(
            outer_loops=50,
            initial_inner_loops=10,
            random_seed=42
        )
        algo = AWCSAT(config)
        
        # 求解
        result = algo.solve(tasks, satellites)
        
        # 验证返回有效解
        assert result is not None
        assert result.objective_value >= 0
        
        # 验证收敛历史
        assert len(algo.history) > 0
    
    def test_algorithm_with_custom_objective(self):
        """测试自定义目标函数"""
        np.random.seed(42)
        
        # 自定义目标函数：编码值之和
        def custom_objective(solution: AWCSATSolution) -> float:
            return float(np.sum(solution.encoding))
        
        config = AWCSATConfig(outer_loops=20, initial_inner_loops=5)
        algo = AWCSAT(config, objective_func=custom_objective)
        
        class MockTask:
            def __init__(self, task_id):
                self.id = str(task_id)
        
        tasks = [MockTask(i) for i in range(10)]
        
        result = algo.solve(tasks, [])
        
        assert result is not None
    
    def test_algorithm_statistics(self):
        """测试算法统计信息"""
        config = AWCSATConfig(outer_loops=10, initial_inner_loops=5)
        algo = AWCSAT(config)
        
        class MockTask:
            def __init__(self, task_id):
                self.id = str(task_id)
        
        tasks = [MockTask(i) for i in range(5)]
        algo.solve(tasks, [])
        
        stats = algo.get_statistics()
        
        assert "initial_temperature" in stats
        assert "final_temperature" in stats
        assert "delta_E" in stats
        assert "tabu_tenure" in stats


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
