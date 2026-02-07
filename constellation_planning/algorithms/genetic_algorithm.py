# -*- coding: utf-8 -*-
"""遗传算法"""

import random
from typing import List, Any, Tuple
from .base import PlanningAlgorithm, Solution, AlgorithmConfig


class GeneticAlgorithm(PlanningAlgorithm):
    """遗传算法"""
    
    def __init__(
        self,
        config: AlgorithmConfig = None,
        population_size: int = 50,
        crossover_rate: float = 0.8,
        mutation_rate: float = 0.1,
        elitism_count: int = 2
    ):
        super().__init__(config)
        self.population_size = population_size
        self.crossover_rate = crossover_rate
        self.mutation_rate = mutation_rate
        self.elitism_count = elitism_count
    
    def get_name(self) -> str:
        return f"GA(pop={self.population_size}, cx={self.crossover_rate}, mut={self.mutation_rate})"
    
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
        # 建立 ID 到 分数的映射
        self.score_map = {
            obs.id: getattr(obs, 'score', getattr(obs, 'priority', 1.0)) 
            for obs in obs_list
        }
        
        # 初始化种群
        population = [
            self._generate_random_solution(obs_list, satellites) 
            for _ in range(self.population_size)
        ]
        
        for generation in range(self.config.max_iterations):
            if self._is_time_exceeded():
                break
            
            # 评估
            for ind in population:
                self._update_best(ind)
            
            # 排序
            population.sort(key=lambda x: x.objective_value, reverse=True)
            
            # 精英保留
            new_population = population[:self.elitism_count]
            
            # 生成新个体
            while len(new_population) < self.population_size:
                # 选择
                parent1 = self._tournament_selection(population)
                parent2 = self._tournament_selection(population)
                
                # 交叉
                if random.random() < self.crossover_rate:
                    child1, child2 = self._crossover(parent1, parent2, obs_list)
                else:
                    child1, child2 = parent1.copy(), parent2.copy()
                
                # 变异
                self._mutate(child1, obs_list, satellites)
                self._mutate(child2, obs_list, satellites)
                
                new_population.extend([child1, child2])
            
            population = new_population[:self.population_size]
            if self.best_solution:
                self.history.append(self.best_solution.objective_value)
        
        return self.best_solution
    
    def _calculate_score(self, solution: Solution) -> float:
        """计算解的总分"""
        return sum(self.score_map.get(obs_id, 1.0) for obs_id in solution.assignments)

    def _generate_random_solution(
        self,
        observations: List[Any],
        satellites: List[Any]
    ) -> Solution:
        """生成随机解"""
        solution = Solution()
        for obs in observations:
            if random.random() > 0.5 and hasattr(obs, 'satellite_id'):
                solution.assignments[obs.id] = obs.satellite_id
        solution.objective_value = self._calculate_score(solution)
        return solution
    
    def _tournament_selection(
        self,
        population: List[Solution],
        tournament_size: int = 3
    ) -> Solution:
        """锦标赛选择"""
        candidates = random.sample(population, min(tournament_size, len(population)))
        return max(candidates, key=lambda x: x.objective_value)
    
    def _crossover(
        self,
        parent1: Solution,
        parent2: Solution,
        observations: List[Any]
    ) -> Tuple[Solution, Solution]:
        """单点交叉"""
        child1 = Solution()
        child2 = Solution()
        
        crossover_point = random.randint(0, len(observations))
        
        for i, obs in enumerate(observations):
            if i < crossover_point:
                if obs.id in parent1.assignments:
                    child1.assignments[obs.id] = parent1.assignments[obs.id]
                if obs.id in parent2.assignments:
                    child2.assignments[obs.id] = parent2.assignments[obs.id]
            else:
                if obs.id in parent2.assignments:
                    child1.assignments[obs.id] = parent2.assignments[obs.id]
                if obs.id in parent1.assignments:
                    child2.assignments[obs.id] = parent1.assignments[obs.id]
        
        child1.objective_value = self._calculate_score(child1)
        child2.objective_value = self._calculate_score(child2)
        return child1, child2
    
    def _mutate(
        self,
        solution: Solution,
        observations: List[Any],
        satellites: List[Any]
    ) -> None:
        """变异"""
        for obs in observations:
            if random.random() < self.mutation_rate:
                if obs.id in solution.assignments:
                    del solution.assignments[obs.id]
                else:
                    if hasattr(obs, 'satellite_id'):
                        solution.assignments[obs.id] = obs.satellite_id
        
        solution.objective_value = self._calculate_score(solution)
