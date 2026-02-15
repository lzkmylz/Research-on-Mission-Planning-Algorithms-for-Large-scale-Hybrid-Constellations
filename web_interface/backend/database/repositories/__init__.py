# -*- coding: utf-8 -*-
"""
数据仓库模块

提供各实体的CRUD操作。
"""

from .base import BaseRepository
from .constellation_repository import ConstellationRepository, SatelliteTemplateRepository
from .ground_station_repository import GroundStationRepository
from .target_repository import TargetRepository
from .scenario_repository import ScenarioRepository
from .algorithm_repository import AlgorithmRepository
from .task_repository import TaskRepository
from .result_repository import ResultRepository
from .satellite_repository import SatelliteRepository

__all__ = [
    "BaseRepository",
    "ConstellationRepository",
    "GroundStationRepository",
    "TargetRepository",
    "ScenarioRepository",
    "AlgorithmRepository",
    "TaskRepository",
    "ResultRepository",
    "SatelliteRepository",
]
