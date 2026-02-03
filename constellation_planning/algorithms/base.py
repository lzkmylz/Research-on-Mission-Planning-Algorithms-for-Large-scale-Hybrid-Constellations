# -*- coding: utf-8 -*-
"""算法基类与解表示"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
import time


@dataclass
class Solution:
    """规划解"""
    # 任务分配: {observation_id: satellite_id}
    assignments: Dict[str, str] = field(default_factory=dict)
    
    # 目标函数值
    objective_value: float = 0.0
    
    # 约束违反
    constraint_violations: List[str] = field(default_factory=list)
    
    # 是否可行
    is_feasible: bool = True
    
    def copy(self) -> "Solution":
        """复制解"""
        return Solution(
            assignments=self.assignments.copy(),
            objective_value=self.objective_value,
            constraint_violations=self.constraint_violations.copy(),
            is_feasible=self.is_feasible
        )


@dataclass
class AlgorithmConfig:
    """算法配置"""
    max_iterations: int = 1000
    time_limit_sec: float = 300.0
    random_seed: Optional[int] = None
    
    # 收敛判断
    convergence_threshold: float = 1e-6
    convergence_patience: int = 100  # 连续多少代无改善则停止


class PlanningAlgorithm(ABC):
    """规划算法基类"""
    
    def __init__(self, config: AlgorithmConfig = None):
        self.config = config or AlgorithmConfig()
        self.best_solution: Optional[Solution] = None
        self.history: List[float] = []  # 目标值收敛历史
        self.iteration_times: List[float] = []  # 每次迭代时间
        self._start_time: float = 0.0
    
    @abstractmethod
    def solve(
        self,
        observations: List[Any],
        satellites: List[Any],
        **kwargs
    ) -> Solution:
        """求解任务规划问题"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """算法名称"""
        pass
    
    def _start_timer(self) -> None:
        """启动计时器"""
        self._start_time = time.time()
    
    def _elapsed_time(self) -> float:
        """返回已用时间（秒）"""
        return time.time() - self._start_time
    
    def _is_time_exceeded(self) -> bool:
        """检查是否超时"""
        return self._elapsed_time() >= self.config.time_limit_sec
    
    def _update_best(self, solution: Solution) -> bool:
        """更新最优解，返回是否有改善"""
        if self.best_solution is None or \
           solution.objective_value > self.best_solution.objective_value:
            self.best_solution = solution.copy()
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """返回统计信息"""
        return {
            "algorithm": self.get_name(),
            "iterations": len(self.history),
            "best_objective": self.best_solution.objective_value if self.best_solution else None,
            "total_time": sum(self.iteration_times),
            "avg_iteration_time": sum(self.iteration_times) / len(self.iteration_times) if self.iteration_times else 0,
        }
