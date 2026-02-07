# -*- coding: utf-8 -*-
"""AWCSAT算法专用解表示

基于论文《面向点群与大区域目标的成像卫星任务规划模型与算法研究》
编码方式：|T|×3矩阵，每个任务有3个编码值
- v_i1: 成像动作执行机会 ∈ [0,1]
- v_i2: 数传动作执行机会 ∈ [0,1]  
- v_i3: 条带延长率 ∈ [0,1]
"""

import math
import numpy as np
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class AWCSATSolution:
    """AWCSAT算法解表示
    
    编码方式：|T|×3矩阵
    每个任务t_i有3个编码值v_i1, v_i2, v_i3，均在[0,1]范围内
    
    Attributes:
        encoding: numpy数组，shape为(num_tasks, 3)
        objective_value: 目标函数值
        is_feasible: 是否可行
        constraint_violations: 约束违反列表
    """
    encoding: np.ndarray
    objective_value: float = 0.0
    is_feasible: bool = True
    constraint_violations: List[str] = field(default_factory=list)
    
    @property
    def num_tasks(self) -> int:
        """任务数量"""
        return self.encoding.shape[0]
    
    def get_imaging_code(self, task_idx: int) -> float:
        """获取任务的成像动作编码值v_i1"""
        return self.encoding[task_idx, 0]
    
    def get_transmission_code(self, task_idx: int) -> float:
        """获取任务的数传动作编码值v_i2"""
        return self.encoding[task_idx, 1]
    
    def get_strip_extension_code(self, task_idx: int) -> float:
        """获取任务的条带延长率编码值v_i3"""
        return self.encoding[task_idx, 2]
    
    def decode_imaging_opportunity(self, task_idx: int, num_opportunities: int) -> int:
        """解码成像机会索引
        
        成像动作在第⌈v_i1 × |X_i|⌉个成像机会执行
        
        Args:
            task_idx: 任务索引
            num_opportunities: 可用的成像机会数量
            
        Returns:
            成像机会索引（1-indexed）
        """
        if num_opportunities <= 0:
            return 0
        v = self.encoding[task_idx, 0]
        return math.ceil(v * num_opportunities)
    
    def decode_transmission_opportunity(self, task_idx: int, num_opportunities: int) -> int:
        """解码数传机会索引
        
        数传动作在第⌈v_i2 × |Y_i|⌉个数传机会执行
        
        Args:
            task_idx: 任务索引
            num_opportunities: 可用的数传机会数量
            
        Returns:
            数传机会索引（1-indexed）
        """
        if num_opportunities <= 0:
            return 0
        v = self.encoding[task_idx, 1]
        return math.ceil(v * num_opportunities)
    
    def decode_strip_extension_rate(
        self, 
        task_idx: int, 
        r_max: float = 1.0, 
        r_min: float = 0.0
    ) -> float:
        """解码条带延长率
        
        条带延长比例为 r_max - v_i3 × (r_max - r_min)
        
        Args:
            task_idx: 任务索引
            r_max: 最大延长率
            r_min: 最小延长率
            
        Returns:
            条带延长率
        """
        v = self.encoding[task_idx, 2]
        return r_max - v * (r_max - r_min)
    
    def copy(self) -> "AWCSATSolution":
        """复制解"""
        return AWCSATSolution(
            encoding=self.encoding.copy(),
            objective_value=self.objective_value,
            is_feasible=self.is_feasible,
            constraint_violations=self.constraint_violations.copy()
        )
    
    def get_hash(self) -> str:
        """获取解的哈希值，用于禁忌列表"""
        # 将编码值四舍五入到2位小数后计算哈希
        rounded = np.round(self.encoding, 2)
        return hash(rounded.tobytes())
    
    @classmethod
    def random(cls, num_tasks: int) -> "AWCSATSolution":
        """生成随机解
        
        Args:
            num_tasks: 任务数量
            
        Returns:
            随机初始化的解
        """
        encoding = np.random.rand(num_tasks, 3)
        return cls(encoding=encoding)
    
    @classmethod
    def zeros(cls, num_tasks: int) -> "AWCSATSolution":
        """生成全零解
        
        Args:
            num_tasks: 任务数量
            
        Returns:
            全零初始化的解
        """
        encoding = np.zeros((num_tasks, 3))
        return cls(encoding=encoding)
    
    def __repr__(self) -> str:
        return (f"AWCSATSolution(num_tasks={self.num_tasks}, "
                f"objective={self.objective_value:.4f}, "
                f"feasible={self.is_feasible})")


def generate_initial_solutions(num_tasks: int, n: int = 10) -> List[AWCSATSolution]:
    """生成N个随机初始解
    
    用于计算初始温度所需的ΔE（目标函数最大值与最小值之差）
    
    Args:
        num_tasks: 任务数量
        n: 生成的初始解数量
        
    Returns:
        初始解列表
    """
    return [AWCSATSolution.random(num_tasks) for _ in range(n)]
