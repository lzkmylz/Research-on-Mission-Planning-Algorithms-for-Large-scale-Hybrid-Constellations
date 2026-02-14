# -*- coding: utf-8 -*-
"""
星座数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from .base import BaseRepository
from database.models import Constellation, ConstellationSatellite, SatelliteTemplate


class ConstellationRepository(BaseRepository[Constellation]):
    """星座数据仓库"""

    def __init__(self):
        super().__init__(Constellation)

    async def get_with_satellites(self, db: AsyncSession, id: str) -> Optional[Constellation]:
        """获取星座及其卫星列表"""
        result = await db.execute(
            select(Constellation)
            .options(joinedload(Constellation.satellites))
            .where(Constellation.id == id)
        )
        return result.scalar_one_or_none()

    async def get_multi_with_satellites(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[Constellation]:
        """获取多个星座及其卫星列表"""
        result = await db.execute(
            select(Constellation)
            .options(joinedload(Constellation.satellites))
            .offset(skip)
            .limit(limit)
            .order_by(Constellation.created_at.desc())
        )
        return result.scalars().unique().all()

    async def create_with_satellites(
        self,
        db: AsyncSession,
        *,
        obj_in: Dict[str, Any],
        satellite_configs: List[Dict[str, Any]]
    ) -> Constellation:
        """创建星座及其卫星配置"""
        # 创建星座
        constellation = await self.create(db, obj_in=obj_in)

        # 创建卫星关联
        for sat_config in satellite_configs:
            sat_link = ConstellationSatellite(
                constellation_id=constellation.id,
                satellite_template_id=sat_config["template_id"],
                plane_number=sat_config.get("plane_number"),
                sat_number_in_plane=sat_config.get("sat_number_in_plane"),
            )
            db.add(sat_link)

        await db.flush()
        await db.refresh(constellation)
        return constellation

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Constellation]:
        """根据名称获取星座"""
        result = await db.execute(
            select(Constellation).where(Constellation.name == name)
        )
        return result.scalar_one_or_none()


class SatelliteTemplateRepository(BaseRepository[SatelliteTemplate]):
    """卫星模板数据仓库"""

    def __init__(self):
        super().__init__(SatelliteTemplate)

    async def get_by_type(
        self,
        db: AsyncSession,
        sat_type: str
    ) -> List[SatelliteTemplate]:
        """根据类型获取卫星模板"""
        from models import SatelliteTypeEnum

        result = await db.execute(
            select(SatelliteTemplate)
            .where(SatelliteTemplate.sat_type == SatelliteTypeEnum(sat_type))
        )
        return result.scalars().all()
