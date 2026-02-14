# -*- coding: utf-8 -*-
"""
目标数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload

from .base import BaseRepository
from database.models import Target, ScenarioTarget, TargetTypeEnum


class TargetRepository(BaseRepository[Target]):
    """目标数据仓库"""

    def __init__(self):
        super().__init__(Target)

    async def get_by_type(self, db: AsyncSession, target_type: str) -> List[Target]:
        """根据类型获取目标"""
        result = await db.execute(
            select(Target).where(Target.target_type == TargetTypeEnum(target_type))
        )
        return result.scalars().all()

    async def get_by_priority(
        self,
        db: AsyncSession,
        min_priority: int = 1,
        max_priority: int = 10
    ) -> List[Target]:
        """根据优先级范围获取目标"""
        result = await db.execute(
            select(Target)
            .where(
                and_(
                    Target.priority >= min_priority,
                    Target.priority <= max_priority
                )
            )
            .order_by(Target.priority.desc())
        )
        return result.scalars().all()

    async def get_by_location(
        self,
        db: AsyncSession,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float
    ) -> List[Target]:
        """根据地理位置范围获取目标"""
        result = await db.execute(
            select(Target)
            .where(
                Target.latitude >= min_lat,
                Target.latitude <= max_lat,
                Target.longitude >= min_lon,
                Target.longitude <= max_lon
            )
        )
        return result.scalars().all()

    async def get_by_scenario(self, db: AsyncSession, scenario_id: str) -> List[Target]:
        """获取场景中的所有目标"""
        result = await db.execute(
            select(Target)
            .join(ScenarioTarget)
            .where(ScenarioTarget.scenario_id == scenario_id)
        )
        return result.scalars().all()

    async def create_batch(
        self,
        db: AsyncSession,
        targets_data: List[Dict[str, Any]]
    ) -> List[Target]:
        """批量创建目标"""
        targets = []
        for data in targets_data:
            target = Target(**data)
            db.add(target)
            targets.append(target)

        await db.flush()
        return targets

    async def add_to_scenario(
        self,
        db: AsyncSession,
        scenario_id: str,
        target_id: str
    ) -> ScenarioTarget:
        """将目标添加到场景"""
        link = ScenarioTarget(
            scenario_id=scenario_id,
            target_id=target_id
        )
        db.add(link)
        await db.flush()
        return link

    async def remove_from_scenario(
        self,
        db: AsyncSession,
        scenario_id: str,
        target_id: str
    ) -> bool:
        """从场景中移除目标"""
        from sqlalchemy import delete

        result = await db.execute(
            delete(ScenarioTarget)
            .where(
                ScenarioTarget.scenario_id == scenario_id,
                ScenarioTarget.target_id == target_id
            )
        )
        await db.flush()
        return result.rowcount > 0
