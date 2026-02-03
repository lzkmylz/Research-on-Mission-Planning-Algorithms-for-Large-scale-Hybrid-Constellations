# -*- coding: utf-8 -*-
"""模拟退火算法"""

import random
import math
from typing import List, Any
from .base import PlanningAlgorithm, Solution, AlgorithmConfig


class SimulatedAnnealing(PlanningAlgorithm):
    """模拟退火算法"""
    
    def __init__(
        self,
        config: AlgorithmConfig = None,
        initial_temp: float = 100.0,
        cooling_rate: float = 0.995,
        min_temp: float = 0.01
    ):
        super().__init__(config)
        self.initial_temp = initial_temp
        self.cooling_rate = cooling_rate
        self.min_temp = min_temp
    
    def get_name(self) -> str:
        return f"SA(T0={self.initial_temp}, α={self.cooling_rate})"
    
    def solve(
        self,
        observations: List[Any],
        satellites: List[Any],
        **kwargs
    ) -> Solution:
        self._start_timer()
        
        if self.config.random_seed:
            random.seed(self.config.random_seed)
        
        # 初始解
        current = self._generate_initial_solution(observations, satellites)
        self._update_best(current)
        
        temp = self.initial_temp
        
        for iteration in range(self.config.max_iterations):
            if self._is_time_exceeded() or temp < self.min_temp:
                break
            
            # 生成邻域解
            neighbor = self._generate_neighbor(current, observations, satellites)
            
            # 计算能量差
            delta = neighbor.objective_value - current.objective_value
            
            # 接受准则
            if delta > 0:
                current = neighbor
            else:
                prob = math.exp(delta / temp)
                if random.random() < prob:
                    current = neighbor
            
            self._update_best(current)
            self.history.append(self.best_solution.objective_value)
            
            # 降温
            temp *= self.cooling_rate
        
        return self.best_solution
    
    def _generate_initial_solution(
        self,
        observations: List[Any],
        satellites: List[Any]
    ) -> Solution:
        """生成初始解"""
        solution = Solution()
        for obs in observations:
            if random.random() > 0.5 and hasattr(obs, 'satellite_id'):
                solution.assignments[obs.id] = obs.satellite_id
        solution.objective_value = len(solution.assignments)
        return solution
    
    def _generate_neighbor(
        self,
        current: Solution,
        observations: List[Any],
        satellites: List[Any]
    ) -> Solution:
        """生成邻域解"""
        neighbor = current.copy()
        obs = random.choice(list(observations))
        
        if obs.id in neighbor.assignments:
            del neighbor.assignments[obs.id]
        else:
            if hasattr(obs, 'satellite_id'):
                neighbor.assignments[obs.id] = obs.satellite_id
        
        neighbor.objective_value = len(neighbor.assignments)
        return neighbor
