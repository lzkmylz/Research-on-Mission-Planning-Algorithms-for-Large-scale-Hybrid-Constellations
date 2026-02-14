# -*- coding: utf-8 -*-
"""
规划结果数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import joinedload

from .base import BaseRepository
from database.models import (
    PlanningResult, Observation, DownlinkPlan, UplinkPlan,
    ConstraintViolation, ResourceTimeline
)


class ResultRepository(BaseRepository[PlanningResult]):
    """规划结果数据仓库"""

    def __init__(self):
        super().__init__(PlanningResult)

    async def get_with_details(
        self,
        db: AsyncSession,
        id: str
    ) -> Optional[PlanningResult]:
        """获取结果及其所有详细信息"""
        result = await db.execute(
            select(PlanningResult)
            .options(
                joinedload(PlanningResult.task),
                joinedload(PlanningResult.observations),
                joinedload(PlanningResult.downlink_plans),
                joinedload(PlanningResult.uplink_plans),
                joinedload(PlanningResult.violations)
            )
            .where(PlanningResult.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_task(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[PlanningResult]:
        """根据任务ID获取结果"""
        result = await db.execute(
            select(PlanningResult)
            .where(PlanningResult.task_id == task_id)
        )
        return result.scalar_one_or_none()

    async def get_by_algorithm(
        self,
        db: AsyncSession,
        algorithm_type: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[PlanningResult]:
        """根据算法类型获取结果"""
        result = await db.execute(
            select(PlanningResult)
            .where(PlanningResult.algorithm_type == algorithm_type)
            .order_by(desc(PlanningResult.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_top_results(
        self,
        db: AsyncSession,
        metric: str = "task_completion_rate",
        *,
        limit: int = 10
    ) -> List[PlanningResult]:
        """获取最优结果"""
        order_column = getattr(PlanningResult, metric, PlanningResult.task_completion_rate)

        result = await db.execute(
            select(PlanningResult)
            .order_by(desc(order_column))
            .limit(limit)
        )
        return result.scalars().all()

    async def create_full_result(
        self,
        db: AsyncSession,
        *,
        task_id: str,
        result_data: Dict[str, Any]
    ) -> PlanningResult:
        """创建完整的规划结果及其关联数据"""
        # 创建主结果记录
        result_obj = await self.create(db, obj_in={
            "task_id": task_id,
            "algorithm_type": result_data.get("metadata", {}).get("algorithm"),
            "scenario_name": result_data.get("metadata", {}).get("scenario"),
            "runtime_seconds": result_data.get("execution", {}).get("runtime_seconds"),
            "iterations_completed": result_data.get("execution", {}).get("iterations_completed"),
            "task_completion_rate": result_data.get("metrics", {}).get("task_completion_rate"),
            "total_value": result_data.get("metrics", {}).get("total_value"),
            "targets_covered": result_data.get("metrics", {}).get("targets_covered"),
            "targets_total": result_data.get("metrics", {}).get("targets_total"),
            "avg_storage_usage": result_data.get("metrics", {}).get("avg_storage_usage"),
            "max_storage_usage": result_data.get("metrics", {}).get("max_storage_usage"),
            "avg_energy_usage": result_data.get("metrics", {}).get("avg_energy_usage"),
            "max_energy_usage": result_data.get("metrics", {}).get("max_energy_usage"),
            "completion_time_hours": result_data.get("metrics", {}).get("completion_time_hours"),
            "is_feasible": result_data.get("constraint_check", {}).get("is_feasible", True),
            "result_json": result_data,
        })

        # 创建观测记录
        for obs_data in result_data.get("enhanced_observations", []):
            obs = Observation(
                result_id=result_obj.id,
                target_id=obs_data.get("target_id"),
                satellite_id=obs_data.get("satellite_id"),
                satellite_type=obs_data.get("satellite_type"),
                observation_time=obs_data.get("observation_time"),
                duration_sec=obs_data.get("duration"),
                elevation_deg=obs_data.get("elevation_deg"),
                off_nadir_deg=obs_data.get("off_nadir_deg"),
                data_volume_gb=obs_data.get("data_volume_gb"),
                imaging_mode=obs_data.get("imaging_mode"),
                target_latitude=obs_data.get("target_latitude"),
                target_longitude=obs_data.get("target_longitude"),
                target_priority=obs_data.get("target_priority"),
                required_uplink=obs_data.get("required_uplink"),
            )
            db.add(obs)

        # 创建数传计划记录
        for dl_data in result_data.get("downlink_plans", []):
            dl = DownlinkPlan(
                result_id=result_obj.id,
                satellite_id=dl_data.get("satellite_id"),
                task_id=dl_data.get("task_id"),
                station_id=dl_data.get("station_id"),
                station_name=dl_data.get("station_name"),
                station_latitude=dl_data.get("station_latitude"),
                station_longitude=dl_data.get("station_longitude"),
                antenna_id=dl_data.get("antenna_id"),
                start_time=dl_data.get("start_time"),
                end_time=dl_data.get("end_time"),
                duration_sec=dl_data.get("duration_sec"),
                data_volume_gb=dl_data.get("data_volume_gb"),
                data_rate_mbps=dl_data.get("data_rate_mbps"),
                is_segmented=dl_data.get("is_segmented", False),
                is_aggregated=dl_data.get("is_aggregated", False),
                segment_number=dl_data.get("segment_number", 0),
                total_segments=dl_data.get("total_segments", 0),
            )
            db.add(dl)

        # 创建上注计划记录
        for ul_data in result_data.get("uplink_plans", []):
            ul = UplinkPlan(
                result_id=result_obj.id,
                satellite_id=ul_data.get("satellite_id"),
                station_id=ul_data.get("station_id"),
                station_name=ul_data.get("station_name"),
                antenna_id=ul_data.get("antenna_id"),
                start_time=ul_data.get("start_time"),
                end_time=ul_data.get("end_time"),
                duration_sec=ul_data.get("duration_sec"),
                num_tasks=ul_data.get("num_tasks"),
                task_ids_json=ul_data.get("task_ids", []),
            )
            db.add(ul)

        # 创建约束违规记录
        for viol_data in result_data.get("constraint_check", {}).get("violations", []):
            viol = ConstraintViolation(
                result_id=result_obj.id,
                constraint_type=viol_data.get("constraint_type"),
                severity=viol_data.get("severity"),
                message=viol_data.get("message"),
                action1_id=viol_data.get("action1_id"),
                action2_id=viol_data.get("action2_id"),
                required_gap=viol_data.get("required_gap"),
                actual_gap=viol_data.get("actual_gap"),
            )
            db.add(viol)

        await db.flush()
        await db.refresh(result_obj)
        return result_obj

    async def compare_results(
        self,
        db: AsyncSession,
        result_ids: List[str]
    ) -> List[PlanningResult]:
        """获取多个结果用于对比"""
        result = await db.execute(
            select(PlanningResult)
            .where(PlanningResult.id.in_(result_ids))
            .order_by(desc(PlanningResult.task_completion_rate))
        )
        return result.scalars().all()

    async def get_results_by_scenario(
        self,
        db: AsyncSession,
        scenario_name: str,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[PlanningResult]:
        """根据场景名称获取结果"""
        result = await db.execute(
            select(PlanningResult)
            .where(PlanningResult.scenario_name == scenario_name)
            .order_by(desc(PlanningResult.created_at))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()
