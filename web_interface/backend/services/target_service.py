# -*- coding: utf-8 -*-
"""
目标管理业务逻辑服务
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import TargetRepository
from schemas.target_schemas import TargetCreate, TargetUpdate, TargetBatchImportItem


class TargetService:
    """目标管理业务服务"""

    def __init__(self):
        self.repo = TargetRepository()

    async def create_target(
        self,
        db: AsyncSession,
        data: TargetCreate
    ) -> Any:
        """创建目标"""
        return await self.repo.create(db, obj_in=data.model_dump())

    async def create_targets_batch(
        self,
        db: AsyncSession,
        targets: List[TargetBatchImportItem]
    ) -> Dict[str, Any]:
        """批量创建目标"""
        targets_data = [t.model_dump() for t in targets]
        created = await self.repo.create_batch(db, targets_data=targets_data)
        return {
            "success_count": len(created),
            "failed_count": len(targets) - len(created),
            "errors": [],
            "created_ids": [t.id for t in created]
        }

    async def get_target(
        self,
        db: AsyncSession,
        target_id: str
    ) -> Optional[Any]:
        """获取目标详情"""
        return await self.repo.get(db, target_id)

    async def list_targets(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """获取目标列表"""
        return await self.repo.get_multi(db, skip=skip, limit=limit)

    async def update_target(
        self,
        db: AsyncSession,
        target_id: str,
        data: TargetUpdate
    ) -> Optional[Any]:
        """更新目标"""
        db_obj = await self.repo.get(db, target_id)
        if not db_obj:
            return None
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def delete_target(
        self,
        db: AsyncSession,
        target_id: str
    ) -> bool:
        """删除目标"""
        return await self.repo.delete(db, id=target_id)

    async def get_targets_by_type(
        self,
        db: AsyncSession,
        target_type: str
    ) -> List[Any]:
        """根据类型获取目标"""
        return await self.repo.get_by_type(db, target_type)

    async def get_targets_by_priority(
        self,
        db: AsyncSession,
        min_priority: int = 1,
        max_priority: int = 10
    ) -> List[Any]:
        """根据优先级范围获取目标"""
        return await self.repo.get_by_priority(
            db,
            min_priority=min_priority,
            max_priority=max_priority
        )

    async def get_targets_by_location(
        self,
        db: AsyncSession,
        min_lat: float,
        max_lat: float,
        min_lon: float,
        max_lon: float
    ) -> List[Any]:
        """根据地理位置范围获取目标"""
        return await self.repo.get_by_location(
            db,
            min_lat=min_lat,
            max_lat=max_lat,
            min_lon=min_lon,
            max_lon=max_lon
        )

    async def get_targets_by_scenario(
        self,
        db: AsyncSession,
        scenario_id: str
    ) -> List[Any]:
        """获取场景中的所有目标"""
        return await self.repo.get_by_scenario(db, scenario_id)

    async def add_target_to_scenario(
        self,
        db: AsyncSession,
        scenario_id: str,
        target_id: str
    ) -> Any:
        """将目标添加到场景"""
        return await self.repo.add_to_scenario(db, scenario_id, target_id)

    async def remove_target_from_scenario(
        self,
        db: AsyncSession,
        scenario_id: str,
        target_id: str
    ) -> bool:
        """从场景中移除目标"""
        return await self.repo.remove_from_scenario(db, scenario_id, target_id)


# 全局服务实例
target_service = TargetService()
