# -*- coding: utf-8 -*-
"""
结果查询业务逻辑服务
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import ResultRepository
from schemas.result_schemas import ResultComparisonRequest


class ResultService:
    """结果查询业务服务"""

    def __init__(self):
        self.repo = ResultRepository()

    async def get_result(
        self,
        db: AsyncSession,
        result_id: str
    ) -> Optional[Any]:
        """获取结果详情"""
        return await self.repo.get_with_details(db, id=result_id)

    async def get_result_by_task(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[Any]:
        """根据任务ID获取结果"""
        return await self.repo.get_by_task(db, task_id)

    async def list_results(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """获取结果列表"""
        return await self.repo.get_multi(db, skip=skip, limit=limit)

    async def get_results_by_algorithm(
        self,
        db: AsyncSession,
        algorithm_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """根据算法类型获取结果"""
        return await self.repo.get_by_algorithm(
            db,
            algorithm_type,
            skip=skip,
            limit=limit
        )

    async def get_top_results(
        self,
        db: AsyncSession,
        metric: str = "task_completion_rate",
        limit: int = 10
    ) -> List[Any]:
        """获取最优结果"""
        return await self.repo.get_top_results(db, metric=metric, limit=limit)

    async def compare_results(
        self,
        db: AsyncSession,
        data: ResultComparisonRequest
    ) -> Dict[str, Any]:
        """对比多个结果"""
        results = await self.repo.compare_results(db, data.result_ids)

        # 构建对比数据
        comparisons = []
        if data.metrics:
            for metric in data.metrics:
                metric_data = {
                    "metric_name": metric,
                    "values": {},
                    "best_result_id": None
                }
                best_value = None
                best_id = None

                for result in results:
                    value = getattr(result, metric, None)
                    if value is not None:
                        metric_data["values"][result.id] = value
                        if best_value is None or value > best_value:
                            best_value = value
                            best_id = result.id

                metric_data["best_result_id"] = best_id
                comparisons.append(metric_data)

        # 确定总体最优
        overall_best = None
        if results:
            overall_best = max(results, key=lambda r: r.task_completion_rate or 0).id

        return {
            "results": results,
            "comparisons": comparisons,
            "overall_best_id": overall_best
        }

    async def get_results_by_scenario(
        self,
        db: AsyncSession,
        scenario_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """根据场景名称获取结果"""
        return await self.repo.get_results_by_scenario(
            db,
            scenario_name,
            skip=skip,
            limit=limit
        )

    async def delete_result(
        self,
        db: AsyncSession,
        result_id: str
    ) -> bool:
        """删除结果"""
        return await self.repo.delete(db, id=result_id)

    async def get_result_statistics(
        self,
        db: AsyncSession,
        result_id: str
    ) -> Optional[Dict[str, Any]]:
        """获取结果统计信息"""
        result = await self.repo.get_with_details(db, id=result_id)
        if not result:
            return None

        # 计算统计信息
        total_observations = len(result.observations) if result.observations else 0
        total_downlinks = len(result.downlink_plans) if result.downlink_plans else 0
        total_uplinks = len(result.uplink_plans) if result.uplink_plans else 0
        total_violations = len(result.violations) if result.violations else 0

        critical_violations = sum(
            1 for v in result.violations
            if v.severity.value == "error"
        ) if result.violations else 0

        warning_violations = total_violations - critical_violations

        # 计算卫星利用率
        satellite_utilization = {}
        if result.observations:
            from collections import Counter
            sat_counter = Counter(obs.satellite_id for obs in result.observations)
            total = sum(sat_counter.values())
            if total > 0:
                satellite_utilization = {
                    sat_id: count / total
                    for sat_id, count in sat_counter.items()
                }

        # 计算地面站利用率
        ground_station_utilization = {}
        if result.downlink_plans:
            from collections import Counter
            station_counter = Counter(dl.station_id for dl in result.downlink_plans)
            total = sum(station_counter.values())
            if total > 0:
                ground_station_utilization = {
                    station_id: count / total
                    for station_id, count in station_counter.items()
                }

        # 计算平均观测时长
        avg_observation_duration = 0
        if result.observations:
            durations = [
                obs.duration_sec for obs in result.observations
                if obs.duration_sec
            ]
            if durations:
                avg_observation_duration = sum(durations) / len(durations)

        # 计算总数据量
        total_data_volume = 0
        if result.downlink_plans:
            total_data_volume = sum(
                dl.data_volume_gb or 0
                for dl in result.downlink_plans
            )

        # 计算观测覆盖率
        observation_coverage = 0
        if result.targets_total and result.targets_total > 0:
            observation_coverage = (result.targets_covered or 0) / result.targets_total

        return {
            "result_id": result_id,
            "total_observations": total_observations,
            "total_downlinks": total_downlinks,
            "total_uplinks": total_uplinks,
            "total_violations": total_violations,
            "critical_violations": critical_violations,
            "warning_violations": warning_violations,
            "observation_coverage_percent": observation_coverage * 100,
            "total_data_volume_gb": total_data_volume,
            "avg_observation_duration_sec": avg_observation_duration,
            "satellite_utilization": satellite_utilization,
            "ground_station_utilization": ground_station_utilization,
        }


# 全局服务实例
result_service = ResultService()
