# -*- coding: utf-8 -*-
"""禁忌搜索算法"""

import random
from typing import List, Any, Tuple
from collections import deque
from .base import PlanningAlgorithm, Solution, AlgorithmConfig


class TabuSearch(PlanningAlgorithm):
    """禁忌搜索算法"""
    
    def __init__(
        self, 
        config: AlgorithmConfig = None,
        tabu_tenure: int = 10,
        neighborhood_size: int = 20
    ):
        super().__init__(config)
        self.tabu_tenure = tabu_tenure
        self.neighborhood_size = neighborhood_size
        self.tabu_list = deque(maxlen=tabu_tenure)
    
    def get_name(self) -> str:
        return f"TabuSearch(tenure={self.tabu_tenure})"
    
    def solve(
        self,
        observations: List[Any],
        satellites: List[Any],
        **kwargs
    ) -> Solution:
        """求解任务规划问题"""
        self._start_timer()
        
        if self.config.random_seed:
            random.seed(self.config.random_seed)
        
        # 1. 生成初始解
        current = self._generate_initial_solution(observations, satellites)
        self._update_best(current)
        
        # 2. 迭代搜索
        for iteration in range(self.config.max_iterations):
            if self._is_time_exceeded():
                break
            
            # 生成邻域
            neighbors = self._generate_neighborhood(current, observations, satellites)
            
            # 选择最佳非禁忌移动（或满足特赦条件）
            best_neighbor = None
            best_move = None
            
            for neighbor, move in neighbors:
                # 检查禁忌
                if move in self.tabu_list:
                    # 特赦条件：比历史最优更好
                    if neighbor.objective_value > self.best_solution.objective_value:
                        if best_neighbor is None or neighbor.objective_value > best_neighbor.objective_value:
                            best_neighbor = neighbor
                            best_move = move
                else:
                    if best_neighbor is None or neighbor.objective_value > best_neighbor.objective_value:
                        best_neighbor = neighbor
                        best_move = move
            
            if best_neighbor:
                current = best_neighbor
                self.tabu_list.append(best_move)
                self._update_best(current)
            
            self.history.append(self.best_solution.objective_value)
        
        return self.best_solution
    
    def _generate_initial_solution(
        self,
        observations: List[Any],
        satellites: List[Any]
    ) -> Solution:
        """生成初始解（贪婪法）"""
        solution = Solution()
        
        # 简单贪婪：按优先级分配
        sorted_obs = sorted(observations, key=lambda x: getattr(x, 'priority', 1.0), reverse=True)
        
        for obs in sorted_obs:
            # 分配给第一个可用的卫星
            if hasattr(obs, 'satellite_id'):
                solution.assignments[obs.id] = obs.satellite_id
        
        solution.objective_value = len(solution.assignments)
        return solution
    
    def _generate_neighborhood(
        self,
        current: Solution,
        observations: List[Any],
        satellites: List[Any]
    ) -> List[Tuple[Solution, str]]:
        """生成邻域解"""
        neighbors = []
        obs_list = list(observations)
        
        for _ in range(min(self.neighborhood_size, len(obs_list))):
            neighbor = current.copy()
            
            # 随机选择一个观测进行调整
            obs = random.choice(obs_list)
            move = f"flip_{obs.id}"
            
            if obs.id in neighbor.assignments:
                # 移除分配
                del neighbor.assignments[obs.id]
            else:
                # 添加分配
                if hasattr(obs, 'satellite_id'):
                    neighbor.assignments[obs.id] = obs.satellite_id
            
            neighbor.objective_value = len(neighbor.assignments)
            neighbors.append((neighbor, move))
        
        return neighbors
