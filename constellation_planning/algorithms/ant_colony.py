# -*- coding: utf-8 -*-
"""蚁群算法"""

import random
import math
from typing import List, Any, Dict
from .base import PlanningAlgorithm, Solution, AlgorithmConfig


class AntColonyOptimization(PlanningAlgorithm):
    """蚁群算法"""
    
    def __init__(
        self,
        config: AlgorithmConfig = None,
        num_ants: int = 20,
        alpha: float = 1.0,       # 信息素重要程度
        beta: float = 2.0,        # 启发式信息重要程度
        rho: float = 0.5,         # 信息素蒸发率
        q: float = 100.0          # 信息素强度
    ):
        super().__init__(config)
        self.num_ants = num_ants
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.q = q
        self.pheromone: Dict[str, float] = {}
    
    def get_name(self) -> str:
        return f"ACO(ants={self.num_ants}, α={self.alpha}, β={self.beta})"
    
    def solve(
        self,
        observations: List[Any],
        satellites: List[Any],
        **kwargs
    ) -> Solution:
        self._start_timer()
        
        if self.config.random_seed:
            random.seed(self.config.random_seed)
        
        obs_list = list(observations)
        
        # 初始化信息素
        self._init_pheromone(obs_list)
        
        for iteration in range(self.config.max_iterations):
            if self._is_time_exceeded():
                break
            
            # 每只蚂蚁构建解
            ant_solutions = []
            for _ in range(self.num_ants):
                solution = self._construct_solution(obs_list, satellites)
                ant_solutions.append(solution)
                self._update_best(solution)
            
            # 更新信息素
            self._update_pheromone(ant_solutions)
            
            self.history.append(self.best_solution.objective_value)
        
        return self.best_solution
    
    def _init_pheromone(self, observations: List[Any]) -> None:
        """初始化信息素"""
        initial_value = 1.0
        for obs in observations:
            self.pheromone[obs.id] = initial_value
    
    def _construct_solution(
        self,
        observations: List[Any],
        satellites: List[Any]
    ) -> Solution:
        """蚂蚁构建解"""
        solution = Solution()
        
        for obs in observations:
            # 计算选择概率
            tau = self.pheromone.get(obs.id, 1.0)  # 信息素
            eta = getattr(obs, 'priority', 1.0)     # 启发式信息
            
            prob = (tau ** self.alpha) * (eta ** self.beta)
            threshold = prob / (prob + 1)  # 归一化
            
            if random.random() < threshold:
                if hasattr(obs, 'satellite_id'):
                    solution.assignments[obs.id] = obs.satellite_id
        
        solution.objective_value = len(solution.assignments)
        return solution
    
    def _update_pheromone(self, solutions: List[Solution]) -> None:
        """更新信息素"""
        # 蒸发
        for key in self.pheromone:
            self.pheromone[key] *= (1 - self.rho)
        
        # 增强
        for solution in solutions:
            deposit = self.q / (1 + len(solution.assignments))
            for obs_id in solution.assignments:
                self.pheromone[obs_id] = self.pheromone.get(obs_id, 0) + deposit
