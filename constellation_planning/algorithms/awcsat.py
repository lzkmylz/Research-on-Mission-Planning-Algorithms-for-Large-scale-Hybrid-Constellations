# -*- coding: utf-8 -*-
"""AWCSAT算法 - 自适应波动温控禁忌模拟退火算法

基于论文《面向点群与大区域目标的成像卫星任务规划模型与算法研究》
(系统工程与电子技术)

AWCSAT = Adaptive Wave-Controlled Simulated Annealing with Tabu

核心特点:
1. 波动温控 - 整体降温与局部重升温
2. 自适应调整 - 温度和内循环次数动态调整
3. 禁忌策略 - 避免重复搜索
"""

import math
import random
import numpy as np
from dataclasses import dataclass, field
from typing import List, Any, Optional, Callable, Tuple
from collections import deque

from .base import PlanningAlgorithm, Solution, AlgorithmConfig
from .awcsat_solution import AWCSATSolution, generate_initial_solutions
from .neighborhood_operators import NeighborhoodOperatorSet


@dataclass
class AWCSATConfig:
    """AWCSAT算法专用配置
    
    论文推荐参数:
    - 外循环次数K: 3000
    - 初始内循环次数L0: 200
    - 禁忌任期: 5
    - 初始温度系数q: 0.9 (范围[0.75, 0.95])
    - 常数n: 1
    - 常数C: 0.25
    """
    # 外循环参数
    outer_loops: int = 3000          # K: 外循环次数
    
    # 内循环参数
    initial_inner_loops: int = 200   # L0: 初始内循环次数
    
    # 禁忌参数
    tabu_tenure: int = 5             # 禁忌任期
    
    # 温度参数
    initial_temp_coef: float = 0.9   # q: 初始温度系数, 范围[0.75, 0.95]
    
    # 波动温控常数
    n: float = 1.0                   # 常数n
    C: float = 0.25                  # 常数C
    
    # 初始解采样数量（用于计算ΔE）
    initial_sample_size: int = 10    # N: 随机初始解数量
    
    # 其他配置
    random_seed: Optional[int] = None
    time_limit_sec: float = 300.0
    
    # 条带延长率范围
    r_max: float = 1.0               # 最大延长率
    r_min: float = 0.0               # 最小延长率


class AWCSAT(PlanningAlgorithm):
    """自适应波动温控禁忌模拟退火算法
    
    算法流程:
    1. 初始化: 采样初始解，计算初始温度
    2. 内循环(等温搜索): 
       - 随机选择邻域算子生成邻域解
       - 将邻域解存入禁忌列表
       - 根据改进Metropolis准则接受或拒绝
    3. 外循环(退火降温):
       - 通过波动温度控制函数更新温度
       - 根据公式更新内循环次数
    4. 终止判断: 达到终止温度或外循环次数则输出最优解
    """
    
    def __init__(
        self,
        config: AWCSATConfig = None,
        objective_func: Callable[[AWCSATSolution], float] = None
    ):
        """初始化AWCSAT算法
        
        Args:
            config: AWCSAT专用配置
            objective_func: 目标函数，输入解输出目标值（最大化）
        """
        self.awcsat_config = config or AWCSATConfig()
        
        # 转换为基类配置
        base_config = AlgorithmConfig(
            max_iterations=self.awcsat_config.outer_loops,
            time_limit_sec=self.awcsat_config.time_limit_sec,
            random_seed=self.awcsat_config.random_seed
        )
        super().__init__(base_config)
        
        self.objective_func = objective_func
        
        # 邻域算子集合
        self.operators = NeighborhoodOperatorSet()
        
        # 禁忌列表
        self.tabu_list = deque(maxlen=self.awcsat_config.tabu_tenure)
        
        # 算法状态
        self.current_solution: Optional[AWCSATSolution] = None
        self.best_awcsat_solution: Optional[AWCSATSolution] = None
        
        # 温度参数
        self.T0: float = 0.0          # 初始温度
        self.current_temp: float = 0.0 # 当前温度
        self.delta_E: float = 0.0     # ΔE: 目标函数差值
        self.E_avg: float = 0.0       # 目标函数平均值
        self.E_min: float = 0.0       # 目标函数最小值
        
        # 内循环状态
        self.current_inner_loops: int = self.awcsat_config.initial_inner_loops
        
        # 统计信息
        self.improved_count: int = 0   # G_k: 质量改进的邻域解个数
        self.accepted_count: int = 0   # J_k: 接受的邻域解个数
    
    def get_name(self) -> str:
        return f"AWCSAT(K={self.awcsat_config.outer_loops}, L0={self.awcsat_config.initial_inner_loops})"
    
    def solve(
        self,
        observations: List[Any],
        satellites: List[Any],
        **kwargs
    ) -> Solution:
        """求解任务规划问题
        
        Args:
            observations: 观测任务列表
            satellites: 卫星列表
            **kwargs: 其他参数
            
        Returns:
            最优解
        """
        self._start_timer()
        
        if self.awcsat_config.random_seed is not None:
            random.seed(self.awcsat_config.random_seed)
            np.random.seed(self.awcsat_config.random_seed)
        
        num_tasks = len(observations)
        if num_tasks == 0:
            return Solution()
        
        # 保存任务和卫星引用
        self._observations = observations
        self._satellites = satellites
        
        # 步骤1: 初始化 - 生成初始解并计算初始温度
        self._initialize(num_tasks)
        
        # 步骤2-5: 主循环
        for k in range(self.awcsat_config.outer_loops):
            if self._is_time_exceeded():
                break
            
            # 重置内循环统计
            self.improved_count = 0
            self.accepted_count = 0
            
            # 步骤2: 内循环（等温搜索）
            for _ in range(self.current_inner_loops):
                self._inner_loop_step()
            
            # 步骤3: 退火降温 - 更新温度
            self._update_temperature(k)
            
            # 步骤4: 更新内循环次数
            self._update_inner_loops(k)
            
            # 记录历史
            if self.best_awcsat_solution:
                self.history.append(self.best_awcsat_solution.objective_value)
        
        # 转换为基类Solution格式返回
        return self._convert_to_base_solution()
    
    def _initialize(self, num_tasks: int) -> None:
        """初始化算法
        
        1. 生成N个随机初始解
        2. 计算目标函数统计量（ΔE, E_avg, E_min）
        3. 计算初始温度T0
        4. 设置当前解和最优解
        """
        # 生成初始解
        initial_solutions = generate_initial_solutions(
            num_tasks, 
            self.awcsat_config.initial_sample_size
        )
        
        # 计算目标函数值
        obj_values = []
        for sol in initial_solutions:
            sol.objective_value = self._evaluate(sol)
            obj_values.append(sol.objective_value)
        
        # 计算统计量
        self.E_avg = np.mean(obj_values)
        self.E_min = np.min(obj_values)
        E_max = np.max(obj_values)
        self.delta_E = E_max - self.E_min
        
        # 计算初始温度: T0 = -ΔE / ln(q)
        q = self.awcsat_config.initial_temp_coef
        if self.delta_E > 0 and 0 < q < 1:
            self.T0 = -self.delta_E / math.log(q)
        else:
            self.T0 = 100.0  # 默认值
        
        self.current_temp = self.T0
        
        # 选择最优初始解作为当前解
        best_idx = np.argmax(obj_values)
        self.current_solution = initial_solutions[best_idx]
        self.best_awcsat_solution = self.current_solution.copy()
        
        # 初始化禁忌列表
        self.tabu_list.clear()
        
        # 初始化内循环次数
        self.current_inner_loops = self.awcsat_config.initial_inner_loops
    
    def _inner_loop_step(self) -> None:
        """内循环单步
        
        1. 随机选择邻域算子生成邻域解
        2. 将邻域解存入禁忌列表
        3. 根据改进Metropolis准则接受或拒绝
        """
        # 生成邻域解
        neighbor, op_name = self.operators.apply_random(self.current_solution)
        
        # 评估目标值
        neighbor.objective_value = self._evaluate(neighbor)
        
        # 获取邻域解的哈希值（用于禁忌）
        neighbor_hash = neighbor.get_hash()
        
        # 检查是否在禁忌列表中
        if neighbor_hash in self.tabu_list:
            # 特赦条件：比历史最优更好
            if neighbor.objective_value > self.best_awcsat_solution.objective_value:
                self._accept_solution(neighbor, neighbor_hash)
            return
        
        # 将邻域解加入禁忌列表
        self.tabu_list.append(neighbor_hash)
        
        # 改进Metropolis准则判断
        if self._metropolis_accept(neighbor):
            self._accept_solution(neighbor, neighbor_hash)
    
    def _accept_solution(self, neighbor: AWCSATSolution, neighbor_hash: str) -> None:
        """接受邻域解"""
        # 判断是否改进
        if neighbor.objective_value > self.current_solution.objective_value:
            self.improved_count += 1
        
        # 更新当前解
        self.current_solution = neighbor
        self.accepted_count += 1
        
        # 更新最优解
        if neighbor.objective_value > self.best_awcsat_solution.objective_value:
            self.best_awcsat_solution = neighbor.copy()
    
    def _metropolis_accept(self, neighbor: AWCSATSolution) -> bool:
        """改进的Metropolis准则
        
        公式:
        - 若 E(X_new) >= E(X_old): p = 1
        - 否则: p = exp(-(E(X_new) - E(X_old)) / (S * T))
        
        其中: S = exp(-(E_avg - E_min) / T0)
        """
        E_new = neighbor.objective_value
        E_old = self.current_solution.objective_value
        
        # 新解更好，直接接受
        if E_new >= E_old:
            return True
        
        # 计算接受概率
        # S = exp(-(E_avg - E_min) / T0)
        if self.T0 > 0:
            S = math.exp(-(self.E_avg - self.E_min) / self.T0)
        else:
            S = 1.0
        
        # 避免除零
        if S * self.current_temp <= 0:
            return False
        
        # p = exp(-(E_new - E_old) / (S * T))
        # 注意：E_new < E_old，所以 -(E_new - E_old) > 0
        delta = E_new - E_old  # 负值
        prob = math.exp(delta / (S * self.current_temp))
        
        return random.random() < prob
    
    def _update_temperature(self, k: int) -> None:
        """更新温度 - 波动温度控制策略
        
        公式:
        T_k = (T0 * (K-k) / K) / (C*k + 1) + (L_k / (1+G_k)) * cos²(J_k / (n*T0))
        
        其中:
        - K: 外循环总次数
        - L_k: 第k次内循环的搜索次数
        - G_k: 第k次内循环中质量改进的邻域解个数
        - J_k: 第k次内循环中接受的邻域解个数
        - n, C: 可调常数
        """
        K = self.awcsat_config.outer_loops
        L_k = self.current_inner_loops
        G_k = self.improved_count
        J_k = self.accepted_count
        n = self.awcsat_config.n
        C = self.awcsat_config.C
        
        # 第一项：线性降温项
        term1 = (self.T0 * (K - k) / K) / (C * k + 1)
        
        # 第二项：波动项
        if n * self.T0 > 0:
            cos_val = math.cos(J_k / (n * self.T0))
        else:
            cos_val = 1.0
        term2 = (L_k / (1 + G_k)) * (cos_val ** 2)
        
        # 更新温度
        self.current_temp = term1 + term2
        
        # 确保温度为正
        self.current_temp = max(self.current_temp, 1e-10)
    
    def _update_inner_loops(self, k: int) -> None:
        """更新内循环次数
        
        公式:
        - 若 T_k >= T_{k+1}: L_{k+1} = L_k * int(T_{k+1} / T_k)
        - 若 T_k < T_{k+1}: L_{k+1} = int(L_k / int(T_{k+1} / T_k))
        
        简化实现：根据温度变化趋势调整
        """
        # 保存旧温度用于比较
        T_old = self.current_temp
        
        # 预计算下一步温度
        K = self.awcsat_config.outer_loops
        k_next = k + 1
        if k_next >= K:
            return
        
        # 简化处理：根据改进比例调整
        improve_ratio = self.improved_count / max(self.current_inner_loops, 1)
        
        if improve_ratio < 0.1:
            # 改进较少，增加内循环次数
            self.current_inner_loops = min(
                int(self.current_inner_loops * 1.1),
                self.awcsat_config.initial_inner_loops * 2
            )
        elif improve_ratio > 0.5:
            # 改进较多，减少内循环次数
            self.current_inner_loops = max(
                int(self.current_inner_loops * 0.9),
                self.awcsat_config.initial_inner_loops // 2
            )
    
    def _evaluate(self, solution: AWCSATSolution) -> float:
        """评估解的目标函数值
        
        如果提供了自定义目标函数则使用，否则使用默认评估
        """
        if self.objective_func is not None:
            return self.objective_func(solution)
        
        # 默认评估：简单计算任务完成数量
        return self._default_objective(solution)
    
    def _default_objective(self, solution: AWCSATSolution) -> float:
        """默认目标函数
        
        简化实现：计算编码值的加权和作为目标值
        实际应用中应替换为论文中的收益模型
        """
        # 简化：使用编码值的平均值作为目标
        # 实际应用中需要实现完整的约束检查和收益计算
        if solution.encoding is None or solution.num_tasks == 0:
            return 0.0
        
        # 模拟目标函数：基于编码值计算
        obj = 0.0
        for i in range(solution.num_tasks):
            # 成像机会和数传机会的编码值越高表示选择越后的机会
            # 条带延长率的编码值会影响任务合并
            imaging = solution.get_imaging_code(i)
            transmission = solution.get_transmission_code(i)
            
            # 简化收益：假设每个有效分配的任务贡献1分
            if imaging > 0 and transmission > 0:
                obj += 1.0
        
        return obj
    
    def _convert_to_base_solution(self) -> Solution:
        """将AWCSAT解转换为基类Solution格式"""
        base_sol = Solution()
        
        if self.best_awcsat_solution is not None:
            base_sol.objective_value = self.best_awcsat_solution.objective_value
            base_sol.is_feasible = self.best_awcsat_solution.is_feasible
            
            # 将编码转换为任务分配
            for i in range(self.best_awcsat_solution.num_tasks):
                if i < len(self._observations):
                    obs = self._observations[i]
                    obs_id = getattr(obs, 'id', str(i))
                    
                    # 根据编码确定卫星分配
                    imaging_code = self.best_awcsat_solution.get_imaging_code(i)
                    if imaging_code > 0 and len(self._satellites) > 0:
                        sat_idx = int(imaging_code * len(self._satellites)) % len(self._satellites)
                        sat = self._satellites[sat_idx]
                        sat_id = getattr(sat, 'id', str(sat_idx))
                        base_sol.assignments[obs_id] = sat_id
        
        return base_sol
    
    def get_awcsat_solution(self) -> Optional[AWCSATSolution]:
        """获取AWCSAT格式的最优解"""
        return self.best_awcsat_solution
    
    def get_statistics(self) -> dict:
        """返回统计信息"""
        stats = super().get_statistics()
        stats.update({
            "initial_temperature": self.T0,
            "final_temperature": self.current_temp,
            "delta_E": self.delta_E,
            "tabu_tenure": self.awcsat_config.tabu_tenure,
            "outer_loops": self.awcsat_config.outer_loops,
            "initial_inner_loops": self.awcsat_config.initial_inner_loops,
        })
        return stats
