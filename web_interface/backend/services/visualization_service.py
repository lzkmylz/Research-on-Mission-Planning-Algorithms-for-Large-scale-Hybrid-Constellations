# -*- coding: utf-8 -*-
"""
可视化数据业务逻辑服务
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import ResultRepository, ScenarioRepository
from schemas.visualization_schemas import (
    SatellitePosition,
    GroundTrack,
    CoverageData,
    ObservationVisualization,
    VisualizationData,
)


class VisualizationService:
    """可视化数据业务服务"""

    def __init__(self):
        self.result_repo = ResultRepository()
        self.scenario_repo = ScenarioRepository()

    async def get_satellite_positions(
        self,
        db: AsyncSession,
        scenario_id: str,
        timestamp: Optional[datetime] = None
    ) -> List[SatellitePosition]:
        """获取卫星位置数据（模拟实现）"""
        # 获取场景及其星座信息
        scenario = await self.scenario_repo.get_with_constellation(db, id=scenario_id)
        if not scenario or not scenario.constellation:
            return []

        # 这里应该调用轨道计算引擎获取真实位置
        # 目前返回模拟数据
        positions = []
        # 根据星座配置生成模拟位置
        num_satellites = (
            (scenario.constellation.walker_planes or 6) *
            (scenario.constellation.walker_sats_per_plane or 10)
        )

        for i in range(num_satellites):
            # 模拟轨道位置计算
            import math
            angle = (i / num_satellites) * 2 * math.pi
            lat = math.degrees(math.sin(angle)) * 60  # 倾角约60度
            lon = math.degrees(angle * 2) % 360 - 180
            alt = scenario.constellation.walker_altitude_km or 500

            positions.append(SatellitePosition(
                satellite_id=f"sat_{i}",
                name=f"卫星 {i}",
                latitude=lat,
                longitude=lon,
                altitude_km=alt,
                timestamp=timestamp or datetime.now()
            ))

        return positions

    async def get_ground_tracks(
        self,
        db: AsyncSession,
        scenario_id: str,
        duration_minutes: int = 90
    ) -> List[GroundTrack]:
        """获取卫星地面轨迹（模拟实现）"""
        scenario = await self.scenario_repo.get_with_constellation(db, id=scenario_id)
        if not scenario or not scenario.constellation:
            return []

        tracks = []
        num_satellites = (
            (scenario.constellation.walker_planes or 6) *
            (scenario.constellation.walker_sats_per_plane or 10)
        )

        for i in range(min(num_satellites, 10)):  # 限制轨迹数量
            points = []
            import math
            for t in range(duration_minutes):
                angle = ((i + t / duration_minutes) / num_satellites) * 2 * math.pi
                lat = math.degrees(math.sin(angle)) * 60
                lon = math.degrees(angle * 2 + t / 60) % 360 - 180
                alt = scenario.constellation.walker_altitude_km or 500
                points.append({
                    "lat": lat,
                    "lon": lon,
                    "alt": alt,
                    "time": t
                })

            tracks.append(GroundTrack(
                satellite_id=f"sat_{i}",
                name=f"卫星 {i}",
                points=points
            ))

        return tracks

    async def get_coverage_data(
        self,
        db: AsyncSession,
        scenario_id: str,
        timestamp: Optional[datetime] = None
    ) -> List[CoverageData]:
        """获取卫星覆盖数据（模拟实现）"""
        scenario = await self.scenario_repo.get_with_constellation(db, id=scenario_id)
        if not scenario or not scenario.constellation:
            return []

        coverage_list = []
        num_satellites = (
            (scenario.constellation.walker_planes or 6) *
            (scenario.constellation.walker_sats_per_plane or 10)
        )

        for i in range(min(num_satellites, 5)):  # 限制覆盖区域数量
            import math
            angle = (i / num_satellites) * 2 * math.pi
            center_lat = math.degrees(math.sin(angle)) * 60
            center_lon = math.degrees(angle * 2) % 360 - 180

            # 生成近似圆形的覆盖区域
            footprint = []
            for j in range(8):
                fp_angle = (j / 8) * 2 * math.pi
                radius = 10  # 覆盖半径约10度
                fp_lat = center_lat + radius * math.cos(fp_angle)
                fp_lon = center_lon + radius * math.sin(fp_angle) / math.cos(math.radians(center_lat))
                footprint.append({"lat": fp_lat, "lon": fp_lon})

            coverage_list.append(CoverageData(
                satellite_id=f"sat_{i}",
                footprint=footprint,
                center_lat=center_lat,
                center_lon=center_lon,
                start_time=timestamp or datetime.now(),
                end_time=timestamp or datetime.now()
            ))

        return coverage_list

    async def get_observation_visualization(
        self,
        db: AsyncSession,
        result_id: str
    ) -> List[ObservationVisualization]:
        """获取观测可视化数据"""
        result = await self.result_repo.get_with_details(db, id=result_id)
        if not result or not result.observations:
            return []

        observations = []
        for obs in result.observations:
            # 根据优先级确定颜色
            color_map = {
                10: "#FF0000",  # 红色 - 最高优先级
                9: "#FF4400",
                8: "#FF8800",
                7: "#FFCC00",
                6: "#FFFF00",
                5: "#CCFF00",  # 黄色 - 中等优先级
                4: "#88FF00",
                3: "#44FF00",
                2: "#00FF00",
                1: "#00FF44",  # 绿色 - 最低优先级
            }
            color = color_map.get(obs.target_priority or 5, "#CCFF00")

            observations.append(ObservationVisualization(
                observation_id=obs.id,
                target_id=obs.target_id,
                target_name=f"目标 {obs.target_id[:8]}",
                satellite_id=obs.satellite_id,
                target_lat=obs.target_latitude or 0,
                target_lon=obs.target_longitude or 0,
                observation_time=obs.observation_time or datetime.now(),
                duration_sec=obs.duration_sec or 0,
                priority=obs.target_priority or 5,
                color=color
            ))

        return observations

    async def get_full_visualization_data(
        self,
        db: AsyncSession,
        scenario_id: str,
        result_id: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> VisualizationData:
        """获取完整可视化数据"""
        satellites = await self.get_satellite_positions(db, scenario_id, timestamp)
        ground_tracks = await self.get_ground_tracks(db, scenario_id)
        coverage = await self.get_coverage_data(db, scenario_id, timestamp)

        observations = []
        if result_id:
            observations = await self.get_observation_visualization(db, result_id)

        # 获取地面站信息
        scenario = await self.scenario_repo.get_with_constellation(db, id=scenario_id)
        ground_stations = []
        if scenario and scenario.constellation:
            # 这里应该从数据库获取地面站信息
            # 目前返回空列表
            pass

        return VisualizationData(
            scenario_id=scenario_id,
            timestamp=timestamp or datetime.now(),
            satellites=satellites,
            ground_tracks=ground_tracks,
            coverage=coverage,
            observations=observations if observations else None,
            ground_stations=ground_stations if ground_stations else None
        )

    async def get_observation_timeline(
        self,
        db: AsyncSession,
        result_id: str
    ) -> List[Dict[str, Any]]:
        """获取观测时间线数据"""
        result = await self.result_repo.get_with_details(db, id=result_id)
        if not result or not result.observations:
            return []

        timeline = []
        for obs in result.observations:
            timeline.append({
                "id": obs.id,
                "target_id": obs.target_id,
                "satellite_id": obs.satellite_id,
                "time": obs.observation_time.isoformat() if obs.observation_time else None,
                "duration": obs.duration_sec,
                "priority": obs.target_priority,
                "data_volume": obs.data_volume_gb,
            })

        # 按时间排序
        timeline.sort(key=lambda x: x["time"] or "")
        return timeline

    async def get_satellite_utilization_timeline(
        self,
        db: AsyncSession,
        result_id: str
    ) -> Dict[str, Any]:
        """获取卫星利用率时间线"""
        result = await self.result_repo.get_with_details(db, id=result_id)
        if not result:
            return {}

        from collections import defaultdict

        # 按卫星分组统计
        satellite_stats = defaultdict(lambda: {
            "observation_count": 0,
            "total_duration": 0,
            "total_data_volume": 0,
        })

        if result.observations:
            for obs in result.observations:
                stats = satellite_stats[obs.satellite_id]
                stats["observation_count"] += 1
                stats["total_duration"] += obs.duration_sec or 0
                stats["total_data_volume"] += obs.data_volume_gb or 0

        return {
            "result_id": result_id,
            "satellite_stats": dict(satellite_stats),
            "total_observations": len(result.observations) if result.observations else 0,
        }


# 全局服务实例
visualization_service = VisualizationService()
