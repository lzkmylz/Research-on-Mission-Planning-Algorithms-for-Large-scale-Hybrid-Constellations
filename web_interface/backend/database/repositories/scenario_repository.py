# -*- coding: utf-8 -*-
"""
场景数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .base import BaseRepository
from database.models import Scenario, ScenarioTarget, Target


class ScenarioRepository(BaseRepository[Scenario]):
    """场景数据仓库"""

    def __init__(self):
        super().__init__(Scenario)

    async def get_with_targets(self, db: AsyncSession, id: str) -> Optional[Scenario]:
        """获取场景及其目标列表"""
        result = await db.execute(
            select(Scenario)
            .options(
                joinedload(Scenario.targets).joinedload(ScenarioTarget.target)
            )
            .where(Scenario.id == id)
        )
        return result.scalar_one_or_none()

    async def get_with_constellation(self, db: AsyncSession, id: str) -> Optional[Scenario]:
        """获取场景及其星座信息"""
        result = await db.execute(
            select(Scenario)
            .options(
                joinedload(Scenario.constellation),
                joinedload(Scenario.targets).joinedload(ScenarioTarget.target)
            )
            .where(Scenario.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi_with_details(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Scenario]:
        """获取多个场景及其详细信息"""
        result = await db.execute(
            select(Scenario)
            .options(
                joinedload(Scenario.constellation),
                joinedload(Scenario.targets)
            )
            .offset(skip)
            .limit(limit)
            .order_by(Scenario.created_at.desc())
        )
        return result.scalars().unique().all()

    async def create_with_targets(
        self,
        db: AsyncSession,
        *,
        obj_in: Dict[str, Any],
        target_ids: List[str]
    ) -> Scenario:
        """创建场景并添加目标"""
        # 创建场景
        scenario = await self.create(db, obj_in=obj_in)

        # 添加目标关联
        for target_id in target_ids:
            link = ScenarioTarget(
                scenario_id=scenario.id,
                target_id=target_id
            )
            db.add(link)

        await db.flush()
        await db.refresh(scenario)
        return scenario

    async def get_by_constellation(
        self,
        db: AsyncSession,
        constellation_id: str
    ) -> List[Scenario]:
        """根据星座获取场景"""
        result = await db.execute(
            select(Scenario)
            .where(Scenario.constellation_id == constellation_id)
            .order_by(Scenario.created_at.desc())
        )
        return result.scalars().all()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Scenario]:
        """根据名称获取场景"""
        result = await db.execute(
            select(Scenario).where(Scenario.name == name)
        )
        return result.scalar_one_or_none()

    async def add_target(
        self,
        db: AsyncSession,
        scenario_id: str,
        target_id: str
    ) -> ScenarioTarget:
        """向场景添加目标"""
        # 检查是否已存在
        existing = await db.execute(
            select(ScenarioTarget).where(
                ScenarioTarget.scenario_id == scenario_id,
                ScenarioTarget.target_id == target_id
            )
        )
        if existing.scalar_one_or_none():
            raise ValueError("Target already exists in scenario")

        link = ScenarioTarget(
            scenario_id=scenario_id,
            target_id=target_id
        )
        db.add(link)
        await db.flush()
        return link

    async def get_target_count(self, db: AsyncSession, scenario_id: str) -> int:
        """获取场景中的目标数量"""
        from sqlalchemy import func

        result = await db.execute(
            select(func.count())
            .select_from(ScenarioTarget)
            .where(ScenarioTarget.scenario_id == scenario_id)
        )
        return result.scalar()
