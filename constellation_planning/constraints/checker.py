# -*- coding: utf-8 -*-
"""约束检查器"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from ..models.observation import ObservationWindow


@dataclass
class ConstraintViolation:
    """约束违反记录"""
    constraint_type: str
    observation_id: str
    message: str
    severity: float = 1.0  # 违反严重程度


class BaseConstraint:
    """约束基类"""
    
    def __init__(self, enabled: bool = True, weight: float = 1.0):
        self.enabled = enabled
        self.weight = weight
    
    def check(self, observation: ObservationWindow, **kwargs) -> Optional[ConstraintViolation]:
        """检查约束，返回违反记录或 None"""
        if not self.enabled:
            return None
        return self._check_impl(observation, **kwargs)
    
    def _check_impl(self, observation: ObservationWindow, **kwargs) -> Optional[ConstraintViolation]:
        """子类实现具体检查逻辑"""
        raise NotImplementedError


class ConstraintChecker:
    """
    约束检查器
    整合所有约束进行统一检查
    """
    
    def __init__(self):
        self.constraints: List[BaseConstraint] = []
    
    def add_constraint(self, constraint: BaseConstraint) -> None:
        """添加约束"""
        self.constraints.append(constraint)
    
    def check_observation(
        self, 
        observation: ObservationWindow,
        **kwargs
    ) -> List[ConstraintViolation]:
        """检查单个观测机会的所有约束"""
        violations = []
        for constraint in self.constraints:
            violation = constraint.check(observation, **kwargs)
            if violation:
                violations.append(violation)
        return violations
    
    def is_feasible(
        self, 
        observation: ObservationWindow,
        **kwargs
    ) -> bool:
        """检查观测是否可行（无约束违反）"""
        return len(self.check_observation(observation, **kwargs)) == 0
    
    def check_all(
        self,
        observations: List[ObservationWindow],
        **kwargs
    ) -> Dict[str, List[ConstraintViolation]]:
        """检查所有观测"""
        result = {}
        for obs in observations:
            violations = self.check_observation(obs, **kwargs)
            if violations:
                result[obs.id] = violations
        return result
