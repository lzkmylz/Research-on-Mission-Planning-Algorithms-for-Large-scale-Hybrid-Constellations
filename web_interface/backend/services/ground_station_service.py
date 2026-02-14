# -*- coding: utf-8 -*-
"""
地面站业务逻辑服务
"""

from typing import List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import GroundStationRepository
from schemas.ground_station_schemas import GroundStationCreate, GroundStationUpdate


class GroundStationService:
    """地面站业务服务"""

    def __init__(self):
        self.repo = GroundStationRepository()

    async def create_ground_station(
        self,
        db: AsyncSession,
        data: GroundStationCreate
    ) -> Any:
        """创建地面站"""
        return await self.repo.create(db, obj_in=data.model_dump())

    async def get_ground_station(
        self,
        db: AsyncSession,
        station_id: str
    ) -> Optional[Any]:
        """获取地面站详情"""
        return await self.repo.get(db, station_id)

    async def list_ground_stations(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """获取地面站列表"""
        return await self.repo.get_multi(db, skip=skip, limit=limit)

    async def update_ground_station(
        self,
        db: AsyncSession,
        station_id: str,
        data: GroundStationUpdate
    ) -> Optional[Any]:
        """更新地面站"""
        db_obj = await self.repo.get(db, station_id)
        if not db_obj:
            return None
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def delete_ground_station(
        self,
        db: AsyncSession,
        station_id: str
    ) -> bool:
        """删除地面站"""
        return await self.repo.delete(db, id=station_id)

    async def get_ground_stations_by_location(
        self,
        db: AsyncSession,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float
    ) -> List[Any]:
        """根据地理位置范围获取地面站"""
        return await self.repo.get_by_location(
            db,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon
        )

    async def get_ground_station_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[Any]:
        """根据名称获取地面站"""
        return await self.repo.get_by_name(db, name=name)

    async def list_all_sorted_by_location(
        self,
        db: AsyncSession
    ) -> List[Any]:
        """按位置排序获取所有地面站"""
        return await self.repo.get_all_sorted_by_location(db)


# 全局服务实例
ground_station_service = GroundStationService()
