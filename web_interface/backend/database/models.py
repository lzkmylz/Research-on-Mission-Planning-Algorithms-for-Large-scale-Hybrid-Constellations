# -*- coding: utf-8 -*-
"""
SQLAlchemy ORM模型

定义数据库表结构。
"""

import uuid
from datetime import datetime
from typing import Optional, List
from enum import Enum as PyEnum

from sqlalchemy import (
    Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey,
    Enum, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


def generate_uuid() -> str:
    """生成UUID字符串"""
    return str(uuid.uuid4())


# 枚举类型
class SatelliteTypeEnum(PyEnum):
    """卫星类型"""
    OPTICAL = "OPTICAL"
    SAR = "SAR"


class TargetTypeEnum(PyEnum):
    """目标类型"""
    POINT = "POINT"
    GRID = "GRID"
    AREA = "AREA"
    MOVING = "MOVING"


class AlgorithmTypeEnum(PyEnum):
    """算法类型"""
    GA = "GA"
    TABU = "TABU"
    SA = "SA"
    ACO = "ACO"
    AWCSAT = "AWCSAT"


class TaskStatusEnum(PyEnum):
    """任务状态"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class SeverityEnum(PyEnum):
    """违规严重程度"""
    ERROR = "error"
    WARNING = "warning"


# ========== 卫星和星座模型 ==========

class SatelliteTemplate(Base):
    """卫星模板表"""
    __tablename__ = "satellite_templates"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    sat_type = Column(Enum(SatelliteTypeEnum), nullable=False)
    altitude_km = Column(Float, nullable=False)
    inclination_deg = Column(Float, nullable=False)
    max_roll_deg = Column(Float)
    max_pitch_deg = Column(Float)
    storage_capacity_gb = Column(Float)
    power_capacity_wh = Column(Float)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    constellations = relationship("ConstellationSatellite", back_populates="satellite")


class Constellation(Base):
    """星座表"""
    __tablename__ = "constellations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    walker_planes = Column(Integer)
    walker_sats_per_plane = Column(Integer)
    walker_altitude_km = Column(Float)
    walker_inclination_deg = Column(Float)
    configuration_json = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # 关系
    satellites = relationship("ConstellationSatellite", back_populates="constellation", cascade="all, delete-orphan")
    scenarios = relationship("Scenario", back_populates="constellation")


class ConstellationSatellite(Base):
    """星座-卫星关联表"""
    __tablename__ = "constellation_satellites"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    constellation_id = Column(String(36), ForeignKey("constellations.id", ondelete="CASCADE"))
    satellite_template_id = Column(String(36), ForeignKey("satellite_templates.id"))
    plane_number = Column(Integer)
    sat_number_in_plane = Column(Integer)

    # 关系
    constellation = relationship("Constellation", back_populates="satellites")
    satellite = relationship("SatelliteTemplate", back_populates="constellations")


# ========== 地面站模型 ==========

class GroundStation(Base):
    """地面站表"""
    __tablename__ = "ground_stations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    altitude_m = Column(Float, default=0)
    min_elevation_deg = Column(Float, default=5.0)
    max_data_rate_mbps = Column(Float)
    antenna_count = Column(Integer, default=1)
    created_at = Column(DateTime, default=func.now())

    # 关系
    downlink_plans = relationship("DownlinkPlan", back_populates="ground_station")
    uplink_plans = relationship("UplinkPlan", back_populates="ground_station")

    # 索引
    __table_args__ = (
        Index("idx_gs_location", "latitude", "longitude"),
    )


# ========== 目标模型 ==========

class Target(Base):
    """目标表"""
    __tablename__ = "targets"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    target_type = Column(Enum(TargetTypeEnum), nullable=False)
    latitude = Column(Float)
    longitude = Column(Float)
    priority = Column(Integer, default=5)
    required_resolution_m = Column(Float)
    polygon_json = Column(JSON)  # 区域目标的多边形
    path_json = Column(JSON)     # 动态目标的路径
    properties_json = Column(JSON)  # 其他属性
    created_at = Column(DateTime, default=func.now())

    # 关系
    scenarios = relationship("ScenarioTarget", back_populates="target")
    observations = relationship("Observation", back_populates="target")

    # 索引
    __table_args__ = (
        Index("idx_target_location", "latitude", "longitude"),
        Index("idx_target_priority", "priority"),
    )


# ========== 场景模型 ==========

class Scenario(Base):
    """场景表（星座+目标组合）"""
    __tablename__ = "scenarios"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    constellation_id = Column(String(36), ForeignKey("constellations.id"))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    description = Column(Text)
    configuration_json = Column(JSON)
    created_at = Column(DateTime, default=func.now())

    # 关系
    constellation = relationship("Constellation", back_populates="scenarios")
    targets = relationship("ScenarioTarget", back_populates="scenario", cascade="all, delete-orphan")
    tasks = relationship("PlanningTask", back_populates="scenario")


class ScenarioTarget(Base):
    """场景-目标关联表"""
    __tablename__ = "scenario_targets"

    scenario_id = Column(String(36), ForeignKey("scenarios.id", ondelete="CASCADE"), primary_key=True)
    target_id = Column(String(36), ForeignKey("targets.id", ondelete="CASCADE"), primary_key=True)

    # 关系
    scenario = relationship("Scenario", back_populates="targets")
    target = relationship("Target", back_populates="scenarios")


# ========== 算法配置模型 ==========

class AlgorithmConfig(Base):
    """算法配置表"""
    __tablename__ = "algorithm_configs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String(100), nullable=False)
    algorithm_type = Column(Enum(AlgorithmTypeEnum), nullable=False)
    max_iterations = Column(Integer)
    time_limit_seconds = Column(Integer)
    random_seed = Column(Integer)
    config_json = Column(JSON)  # 其他算法专用参数
    description = Column(Text)
    is_preset = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    # 关系
    tasks = relationship("PlanningTask", back_populates="algorithm_config")


# ========== 规划任务和结果模型 ==========

class PlanningTask(Base):
    """规划任务表"""
    __tablename__ = "planning_tasks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    scenario_id = Column(String(36), ForeignKey("scenarios.id"))
    algorithm_config_id = Column(String(36), ForeignKey("algorithm_configs.id"))
    status = Column(Enum(TaskStatusEnum), default=TaskStatusEnum.PENDING)
    progress_pct = Column(Integer, default=0)
    current_iteration = Column(Integer, default=0)
    best_value = Column(Float)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    created_at = Column(DateTime, default=func.now())

    # 关系
    scenario = relationship("Scenario", back_populates="tasks")
    algorithm_config = relationship("AlgorithmConfig", back_populates="tasks")
    result = relationship("PlanningResult", back_populates="task", uselist=False, cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index("idx_task_status", "status"),
        Index("idx_task_scenario", "scenario_id"),
    )


class PlanningResult(Base):
    """规划结果主表"""
    __tablename__ = "planning_results"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    task_id = Column(String(36), ForeignKey("planning_tasks.id", ondelete="CASCADE"), unique=True)
    algorithm_type = Column(String(20))
    scenario_name = Column(String(100))
    runtime_seconds = Column(Float)
    iterations_completed = Column(Integer)

    # 性能指标
    task_completion_rate = Column(Float)
    total_value = Column(Float)
    targets_covered = Column(Integer)
    targets_total = Column(Integer)
    avg_storage_usage = Column(Float)
    max_storage_usage = Column(Float)
    avg_energy_usage = Column(Float)
    max_energy_usage = Column(Float)
    completion_time_hours = Column(Float)
    is_feasible = Column(Boolean, default=True)

    # 详细结果JSON（用于快速访问）
    result_json = Column(JSON)

    created_at = Column(DateTime, default=func.now())

    # 关系
    task = relationship("PlanningTask", back_populates="result")
    observations = relationship("Observation", back_populates="result", cascade="all, delete-orphan")
    downlink_plans = relationship("DownlinkPlan", back_populates="result", cascade="all, delete-orphan")
    uplink_plans = relationship("UplinkPlan", back_populates="result", cascade="all, delete-orphan")
    violations = relationship("ConstraintViolation", back_populates="result", cascade="all, delete-orphan")

    # 索引
    __table_args__ = (
        Index("idx_result_algorithm", "algorithm_type"),
        Index("idx_result_completion_rate", "task_completion_rate"),
    )


class Observation(Base):
    """观测记录表"""
    __tablename__ = "observations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    result_id = Column(String(36), ForeignKey("planning_results.id", ondelete="CASCADE"))
    target_id = Column(String(36), ForeignKey("targets.id"))
    satellite_id = Column(String(36))
    satellite_type = Column(String(20))
    observation_time = Column(DateTime)
    duration_sec = Column(Integer)
    elevation_deg = Column(Float)
    off_nadir_deg = Column(Float)
    data_volume_gb = Column(Float)
    imaging_mode = Column(String(50))
    target_latitude = Column(Float)
    target_longitude = Column(Float)
    target_priority = Column(Integer)
    required_uplink = Column(Boolean, default=False)

    # 关系
    result = relationship("PlanningResult", back_populates="observations")
    target = relationship("Target", back_populates="observations")

    # 索引
    __table_args__ = (
        Index("idx_obs_result", "result_id"),
        Index("idx_obs_satellite", "satellite_id"),
        Index("idx_obs_time", "observation_time"),
    )


class DownlinkPlan(Base):
    """数传计划表"""
    __tablename__ = "downlink_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    result_id = Column(String(36), ForeignKey("planning_results.id", ondelete="CASCADE"))
    satellite_id = Column(String(36))
    task_id = Column(String(36))
    station_id = Column(String(36), ForeignKey("ground_stations.id"))
    station_name = Column(String(100))
    station_latitude = Column(Float)
    station_longitude = Column(Float)
    antenna_id = Column(String(36))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_sec = Column(Float)
    data_volume_gb = Column(Float)
    data_rate_mbps = Column(Float)
    is_segmented = Column(Boolean, default=False)
    is_aggregated = Column(Boolean, default=False)
    segment_number = Column(Integer)
    total_segments = Column(Integer)

    # 关系
    result = relationship("PlanningResult", back_populates="downlink_plans")
    ground_station = relationship("GroundStation", back_populates="downlink_plans")

    # 索引
    __table_args__ = (
        Index("idx_dl_result", "result_id"),
        Index("idx_dl_satellite", "satellite_id"),
        Index("idx_dl_station", "station_id"),
        Index("idx_dl_time", "start_time", "end_time"),
    )


class UplinkPlan(Base):
    """上注计划表"""
    __tablename__ = "uplink_plans"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    result_id = Column(String(36), ForeignKey("planning_results.id", ondelete="CASCADE"))
    satellite_id = Column(String(36))
    station_id = Column(String(36), ForeignKey("ground_stations.id"))
    station_name = Column(String(100))
    antenna_id = Column(String(36))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    duration_sec = Column(Float)
    num_tasks = Column(Integer)
    task_ids_json = Column(JSON)

    # 关系
    result = relationship("PlanningResult", back_populates="uplink_plans")
    ground_station = relationship("GroundStation", back_populates="uplink_plans")

    # 索引
    __table_args__ = (
        Index("idx_ul_result", "result_id"),
        Index("idx_ul_satellite", "satellite_id"),
    )


class ConstraintViolation(Base):
    """约束违规记录表"""
    __tablename__ = "constraint_violations"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    result_id = Column(String(36), ForeignKey("planning_results.id", ondelete="CASCADE"))
    constraint_type = Column(String(50))
    severity = Column(Enum(SeverityEnum))
    message = Column(Text)
    action1_id = Column(String(36))
    action2_id = Column(String(36))
    required_gap = Column(Float)
    actual_gap = Column(Float)

    # 关系
    result = relationship("PlanningResult", back_populates="violations")

    # 索引
    __table_args__ = (
        Index("idx_violation_result", "result_id"),
        Index("idx_violation_type", "constraint_type"),
    )


# ========== 资源时间线模型（可选，用于详细分析） ==========

class ResourceTimeline(Base):
    """资源时间线表"""
    __tablename__ = "resource_timelines"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    result_id = Column(String(36), ForeignKey("planning_results.id", ondelete="CASCADE"))
    satellite_id = Column(String(36))
    timeline_type = Column(String(20))  # "storage" | "energy" | "payload"
    event_time = Column(DateTime)
    event_type = Column(String(50))  # "imaging", "downlink", "uplink", etc.
    value = Column(Float)
    value_max = Column(Float)  # 用于计算百分比
    metadata_json = Column(JSON)

    # 索引
    __table_args__ = (
        Index("idx_timeline_result", "result_id"),
        Index("idx_timeline_satellite", "satellite_id"),
        Index("idx_timeline_time", "event_time"),
    )
