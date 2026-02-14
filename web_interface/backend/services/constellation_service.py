# -*- coding: utf-8 -*-
"""
星座业务逻辑服务
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import ConstellationRepository, SatelliteTemplateRepository
from schemas.constellation_schemas import (
    ConstellationCreate,
    ConstellationUpdate,
    SatelliteTemplateCreate,
)


class ConstellationService:
    """星座业务服务"""

    def __init__(self):
        self.repo = ConstellationRepository()
        self.satellite_repo = SatelliteTemplateRepository()

    async def create_constellation(
        self,
        db: AsyncSession,
        data: ConstellationCreate
    ) -> Any:
        """创建星座"""
        obj_in = data.model_dump(exclude={"satellite_configs"})
        satellite_configs = data.satellite_configs or []
        return await self.repo.create_with_satellites(
            db,
            obj_in=obj_in,
            satellite_configs=satellite_configs
        )

    async def get_constellation(
        self,
        db: AsyncSession,
        constellation_id: str
    ) -> Optional[Any]:
        """获取星座详情"""
        return await self.repo.get_with_satellites(db, id=constellation_id)

    async def list_constellations(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """获取星座列表"""
        return await self.repo.get_multi_with_satellites(db, skip=skip, limit=limit)

    async def update_constellation(
        self,
        db: AsyncSession,
        constellation_id: str,
        data: ConstellationUpdate
    ) -> Optional[Any]:
        """更新星座"""
        db_obj = await self.repo.get(db, constellation_id)
        if not db_obj:
            return None
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def delete_constellation(
        self,
        db: AsyncSession,
        constellation_id: str
    ) -> bool:
        """删除星座"""
        return await self.repo.delete(db, id=constellation_id)

    async def get_constellation_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[Any]:
        """根据名称获取星座"""
        return await self.repo.get_by_name(db, name=name)

    # ========== 卫星模板方法 ==========

    async def create_satellite_template(
        self,
        db: AsyncSession,
        data: SatelliteTemplateCreate
    ) -> Any:
        """创建卫星模板"""
        return await self.satellite_repo.create(db, obj_in=data.model_dump())

    async def get_satellite_template(
        self,
        db: AsyncSession,
        template_id: str
    ) -> Optional[Any]:
        """获取卫星模板"""
        return await self.satellite_repo.get(db, template_id)

    async def list_satellite_templates(
        self,
        db: AsyncSession,
        sat_type: Optional[str] = None
    ) -> List[Any]:
        """获取卫星模板列表"""
        if sat_type:
            return await self.satellite_repo.get_by_type(db, sat_type)
        return await self.satellite_repo.get_all(db)

    async def delete_satellite_template(
        self,
        db: AsyncSession,
        template_id: str
    ) -> bool:
        """删除卫星模板"""
        return await self.satellite_repo.delete(db, id=template_id)


# 全局服务实例
constellation_service = ConstellationService()
