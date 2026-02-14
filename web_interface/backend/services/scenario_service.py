# -*- coding: utf-8 -*-
"""
场景管理业务逻辑服务
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import ScenarioRepository, TargetRepository
from schemas.scenario_schemas import ScenarioCreate, ScenarioUpdate


class ScenarioService:
    """场景管理业务服务"""

    def __init__(self):
        self.repo = ScenarioRepository()
        self.target_repo = TargetRepository()

    async def create_scenario(
        self,
        db: AsyncSession,
        data: ScenarioCreate
    ) -> Any:
        """创建场景并关联目标"""
        obj_in = data.model_dump(exclude={"target_ids"})
        target_ids = data.target_ids or []
        return await self.repo.create_with_targets(
            db,
            obj_in=obj_in,
            target_ids=target_ids
        )

    async def get_scenario(
        self,
        db: AsyncSession,
        scenario_id: str
    ) -> Optional[Any]:
        """获取场景详情（包含目标）"""
        return await self.repo.get_with_targets(db, id=scenario_id)

    async def get_scenario_with_constellation(
        self,
        db: AsyncSession,
        scenario_id: str
    ) -> Optional[Any]:
        """获取场景详情（包含星座和目标）"""
        return await self.repo.get_with_constellation(db, id=scenario_id)

    async def list_scenarios(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """获取场景列表"""
        return await self.repo.get_multi_with_details(db, skip=skip, limit=limit)

    async def update_scenario(
        self,
        db: AsyncSession,
        scenario_id: str,
        data: ScenarioUpdate
    ) -> Optional[Any]:
        """更新场景"""
        db_obj = await self.repo.get(db, scenario_id)
        if not db_obj:
            return None
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def delete_scenario(
        self,
        db: AsyncSession,
        scenario_id: str
    ) -> bool:
        """删除场景"""
        return await self.repo.delete(db, id=scenario_id)

    async def get_scenarios_by_constellation(
        self,
        db: AsyncSession,
        constellation_id: str
    ) -> List[Any]:
        """根据星座获取场景"""
        return await self.repo.get_by_constellation(db, constellation_id)

    async def get_scenario_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[Any]:
        """根据名称获取场景"""
        return await self.repo.get_by_name(db, name=name)

    async def add_target_to_scenario(
        self,
        db: AsyncSession,
        scenario_id: str,
        target_id: str
    ) -> Any:
        """向场景添加目标"""
        return await self.repo.add_target(db, scenario_id, target_id)

    async def remove_target_from_scenario(
        self,
        db: AsyncSession,
        scenario_id: str,
        target_id: str
    ) -> bool:
        """从场景中移除目标"""
        return await self.target_repo.remove_from_scenario(db, scenario_id, target_id)

    async def get_target_count(
        self,
        db: AsyncSession,
        scenario_id: str
    ) -> int:
        """获取场景中的目标数量"""
        return await self.repo.get_target_count(db, scenario_id)

    async def clone_scenario(
        self,
        db: AsyncSession,
        scenario_id: str,
        new_name: Optional[str] = None
    ) -> Optional[Any]:
        """复制场景"""
        original = await self.repo.get_with_targets(db, id=scenario_id)
        if not original:
            return None

        # 创建新场景数据
        obj_in = {
            "name": new_name or f"{original.name} (Copy)",
            "constellation_id": original.constellation_id,
            "start_time": original.start_time,
            "end_time": original.end_time,
            "description": original.description,
            "configuration_json": original.configuration_json,
        }

        # 获取原场景的目标ID列表
        target_ids = [st.target_id for st in original.targets]

        # 创建新场景并关联目标
        return await self.repo.create_with_targets(
            db,
            obj_in=obj_in,
            target_ids=target_ids
        )


# 全局服务实例
scenario_service = ScenarioService()
