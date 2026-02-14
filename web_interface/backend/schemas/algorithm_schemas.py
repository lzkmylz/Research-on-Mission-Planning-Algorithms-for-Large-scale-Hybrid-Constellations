# -*- coding: utf-8 -*-
"""
算法配置相关Pydantic Schema
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

from database.models import AlgorithmTypeEnum


# ========== 算法配置Schema ==========

class AlgorithmConfigBase(BaseModel):
    """算法配置基础Schema"""
    name: str
    algorithm_type: AlgorithmTypeEnum
    max_iterations: Optional[int] = None
    time_limit_seconds: Optional[int] = None
    random_seed: Optional[int] = None
    config_json: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_preset: Optional[bool] = False


class AlgorithmConfigCreate(AlgorithmConfigBase):
    """创建算法配置请求"""
    pass


class AlgorithmConfigUpdate(BaseModel):
    """更新算法配置请求"""
    name: Optional[str] = None
    algorithm_type: Optional[AlgorithmTypeEnum] = None
    max_iterations: Optional[int] = None
    time_limit_seconds: Optional[int] = None
    random_seed: Optional[int] = None
    config_json: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_preset: Optional[bool] = None


class AlgorithmConfigResponse(AlgorithmConfigBase):
    """算法配置响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    created_at: datetime


class AlgorithmConfigList(BaseModel):
    """算法配置列表响应"""
    total: int
    items: List[AlgorithmConfigResponse]


# ========== 遗传算法专用配置Schema ==========

class GAConfigBase(BaseModel):
    """遗传算法配置基础"""
    population_size: int = Field(default=50, ge=10, le=500)
    crossover_rate: float = Field(default=0.8, ge=0.0, le=1.0)
    mutation_rate: float = Field(default=0.1, ge=0.0, le=1.0)
    elitism_count: int = Field(default=2, ge=0)
    selection_method: str = "tournament"  # tournament, roulette, rank
    tournament_size: int = Field(default=3, ge=2)


class GAConfigCreate(GAConfigBase):
    """创建遗传算法配置请求"""
    pass


class GAConfigResponse(GAConfigBase):
    """遗传算法配置响应"""
    model_config = ConfigDict(from_attributes=True)


# ========== 禁忌搜索专用配置Schema ==========

class TabuConfigBase(BaseModel):
    """禁忌搜索配置基础"""
    tabu_list_size: int = Field(default=50, ge=10, le=500)
    neighborhood_size: int = Field(default=20, ge=5, le=100)
    aspiration_criteria: bool = True
    diversification_iterations: int = Field(default=100, ge=0)


class TabuConfigCreate(TabuConfigBase):
    """创建禁忌搜索配置请求"""
    pass


class TabuConfigResponse(TabuConfigBase):
    """禁忌搜索配置响应"""
    model_config = ConfigDict(from_attributes=True)


# ========== 模拟退火专用配置Schema ==========

class SAConfigBase(BaseModel):
    """模拟退火配置基础"""
    initial_temperature: float = Field(default=1000.0, gt=0)
    cooling_rate: float = Field(default=0.995, gt=0, lt=1)
    min_temperature: float = Field(default=0.001, gt=0)
    iterations_per_temp: int = Field(default=100, ge=1)


class SAConfigCreate(SAConfigBase):
    """创建模拟退火配置请求"""
    pass


class SAConfigResponse(SAConfigBase):
    """模拟退火配置响应"""
    model_config = ConfigDict(from_attributes=True)


# ========== 蚁群算法专用配置Schema ==========

class ACOConfigBase(BaseModel):
    """蚁群算法配置基础"""
    num_ants: int = Field(default=30, ge=5, le=200)
    alpha: float = Field(default=1.0, ge=0)  # 信息素重要性
    beta: float = Field(default=2.0, ge=0)   # 启发函数重要性
    rho: float = Field(default=0.5, ge=0, le=1)  # 信息素蒸发率
    q: float = Field(default=100.0, gt=0)    # 信息素增量常数


class ACOConfigCreate(ACOConfigBase):
    """创建蚁群算法配置请求"""
    pass


class ACOConfigResponse(ACOConfigBase):
    """蚁群算法配置响应"""
    model_config = ConfigDict(from_attributes=True)


# ========== AWCSAT专用配置Schema ==========

class AWCSATConfigBase(BaseModel):
    """AWCSAT算法配置基础"""
    max_clause_weight: int = Field(default=1000, ge=100)
    weight_update_factor: float = Field(default=1.1, gt=1.0)
    noise_parameter: float = Field(default=0.1, ge=0, le=1)


class AWCSATConfigCreate(AWCSATConfigBase):
    """创建AWCSAT配置请求"""
    pass


class AWCSATConfigResponse(AWCSATConfigBase):
    """AWCSAT配置响应"""
    model_config = ConfigDict(from_attributes=True)


# ========== 算法比较Schema ==========

class AlgorithmComparisonRequest(BaseModel):
    """算法比较请求"""
    scenario_id: str
    algorithm_config_ids: List[str]
    run_count: int = Field(default=1, ge=1, le=10)


class AlgorithmComparisonResult(BaseModel):
    """单个算法比较结果"""
    algorithm_config_id: str
    algorithm_type: str
    avg_completion_rate: float
    avg_runtime_seconds: float
    avg_total_value: float
    best_value: float
    worst_value: float
    std_deviation: float


class AlgorithmComparisonResponse(BaseModel):
    """算法比较响应"""
    scenario_id: str
    run_count: int
    results: List[AlgorithmComparisonResult]
    best_algorithm_id: Optional[str] = None
