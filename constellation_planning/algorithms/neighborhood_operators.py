# -*- coding: utf-8 -*-
"""AWCSAT算法邻域操作算子

基于论文《面向点群与大区域目标的成像卫星任务规划模型与算法研究》
实现4种邻域操作算子:
1. 移动算子 (Move Operator)
2. 同位交换算子 (Same-Position Exchange Operator)
3. 随机交换算子 (Random Exchange Operator)
4. 整行交换算子 (Whole Row Exchange Operator)
"""

import random
import numpy as np
from abc import ABC, abstractmethod
from typing import Tuple, Optional
from .awcsat_solution import AWCSATSolution


class NeighborhoodOperator(ABC):
    """邻域算子基类"""
    
    @abstractmethod
    def apply(self, solution: AWCSATSolution) -> AWCSATSolution:
        """应用算子生成邻域解
        
        Args:
            solution: 当前解
            
        Returns:
            邻域解
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取算子名称"""
        pass


class MoveOperator(NeighborhoodOperator):
    """移动算子
    
    随机选择一个任务，随机选择其中一个编码位，
    将该编码值替换为[0,1]范围内的随机值。
    
    示例：
    原始: [v11, v12=0.2, v13]  ->  [v11, v12=0.4, v13]
    """
    
    def apply(self, solution: AWCSATSolution) -> AWCSATSolution:
        """应用移动算子"""
        neighbor = solution.copy()
        
        # 随机选择一个任务
        task_idx = random.randint(0, neighbor.num_tasks - 1)
        
        # 随机选择一个编码位 (0: 成像, 1: 数传, 2: 条带延长率)
        code_idx = random.randint(0, 2)
        
        # 生成新的随机值
        neighbor.encoding[task_idx, code_idx] = random.random()
        
        return neighbor
    
    def get_name(self) -> str:
        return "MoveOperator"


class SamePositionExchangeOperator(NeighborhoodOperator):
    """同位交换算子
    
    随机选择两个不同的任务，交换它们在同一位置的编码值。
    
    示例：
    任务1: [v11, v12, v13]    任务1: [v11, v12, v13]
    任务2: [v21, v22, v23]  -> 任务2: [v21, v22, v23]
    （交换位置1的值）
    """
    
    def apply(self, solution: AWCSATSolution) -> AWCSATSolution:
        """应用同位交换算子"""
        neighbor = solution.copy()
        
        if neighbor.num_tasks < 2:
            return neighbor
        
        # 随机选择两个不同的任务
        task1, task2 = random.sample(range(neighbor.num_tasks), 2)
        
        # 随机选择一个编码位
        code_idx = random.randint(0, 2)
        
        # 交换两个任务在该位置的编码值
        neighbor.encoding[task1, code_idx], neighbor.encoding[task2, code_idx] = \
            neighbor.encoding[task2, code_idx], neighbor.encoding[task1, code_idx]
        
        return neighbor
    
    def get_name(self) -> str:
        return "SamePositionExchangeOperator"


class RandomExchangeOperator(NeighborhoodOperator):
    """随机交换算子
    
    随机选择两个不同的任务，分别随机选择它们的某个编码位，交换这两个值。
    
    示例：
    任务1: [v11, v12, v13]    任务1: [v11, v23, v13]
    任务2: [v21, v22, v23]  -> 任务2: [v21, v22, v12]
    （交换任务1位置1和任务2位置2的值）
    """
    
    def apply(self, solution: AWCSATSolution) -> AWCSATSolution:
        """应用随机交换算子"""
        neighbor = solution.copy()
        
        if neighbor.num_tasks < 2:
            return neighbor
        
        # 随机选择两个不同的任务
        task1, task2 = random.sample(range(neighbor.num_tasks), 2)
        
        # 分别随机选择编码位
        code_idx1 = random.randint(0, 2)
        code_idx2 = random.randint(0, 2)
        
        # 交换两个值
        neighbor.encoding[task1, code_idx1], neighbor.encoding[task2, code_idx2] = \
            neighbor.encoding[task2, code_idx2], neighbor.encoding[task1, code_idx1]
        
        return neighbor
    
    def get_name(self) -> str:
        return "RandomExchangeOperator"


class WholeRowExchangeOperator(NeighborhoodOperator):
    """整行交换算子
    
    随机选择两个不同的任务，交换它们的全部编码值（整行交换）。
    
    示例：
    任务1: [v11, v12, v13]    任务1: [v21, v22, v23]
    任务2: [v21, v22, v23]  -> 任务2: [v11, v12, v13]
    """
    
    def apply(self, solution: AWCSATSolution) -> AWCSATSolution:
        """应用整行交换算子"""
        neighbor = solution.copy()
        
        if neighbor.num_tasks < 2:
            return neighbor
        
        # 随机选择两个不同的任务
        task1, task2 = random.sample(range(neighbor.num_tasks), 2)
        
        # 交换整行
        neighbor.encoding[task1], neighbor.encoding[task2] = \
            neighbor.encoding[task2].copy(), neighbor.encoding[task1].copy()
        
        return neighbor
    
    def get_name(self) -> str:
        return "WholeRowExchangeOperator"


class NeighborhoodOperatorSet:
    """邻域算子集合
    
    管理多个邻域算子，支持随机选择算子
    """
    
    def __init__(self, operators: Optional[list] = None):
        """初始化算子集合
        
        Args:
            operators: 算子列表，默认使用全部4种算子
        """
        if operators is None:
            self.operators = [
                MoveOperator(),
                SamePositionExchangeOperator(),
                RandomExchangeOperator(),
                WholeRowExchangeOperator()
            ]
        else:
            self.operators = operators
    
    def random_select(self) -> NeighborhoodOperator:
        """随机选择一个算子"""
        return random.choice(self.operators)
    
    def apply_random(self, solution: AWCSATSolution) -> Tuple[AWCSATSolution, str]:
        """随机选择算子并应用
        
        Args:
            solution: 当前解
            
        Returns:
            (邻域解, 使用的算子名称)
        """
        operator = self.random_select()
        neighbor = operator.apply(solution)
        return neighbor, operator.get_name()
    
    def __len__(self) -> int:
        return len(self.operators)
    
    def __repr__(self) -> str:
        names = [op.get_name() for op in self.operators]
        return f"NeighborhoodOperatorSet({names})"
