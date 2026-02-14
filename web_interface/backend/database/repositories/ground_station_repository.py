# -*- coding: utf-8 -*-
"""
地面站数据仓库
"""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from .base import BaseRepository
from database.models import GroundStation


class GroundStationRepository(BaseRepository[GroundStation]):
    """地面站数据仓库"""

    def __init__(self):
        super().__init__(GroundStation)

    async def get_by_location(
        self,
        db: AsyncSession,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float
    ) -> List[GroundStation]:
        """根据地理位置范围获取地面站"""
        result = await db.execute(
            select(GroundStation)
            .where(
                GroundStation.latitude >= min_lat,
                GroundStation.latitude <= max_lat,
                GroundStation.longitude >= min_lon,
                GroundStation.longitude <= max_lon
            )
        )
        return result.scalars().all()

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[GroundStation]:
        """根据名称获取地面站"""
        result = await db.execute(
            select(GroundStation).where(GroundStation.name == name)
        )
        return result.scalar_one_or_none()

    async def get_all_sorted_by_location(self, db: AsyncSession) -> List[GroundStation]:
        """按位置排序获取所有地面站"""
        result = await db.execute(
            select(GroundStation)
            .order_by(GroundStation.latitude, GroundStation.longitude)
        )
        return result.scalars().all()
