# -*- coding: utf-8 -*-
"""
算法配置业务逻辑服务
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import AlgorithmRepository
from schemas.algorithm_schemas import AlgorithmConfigCreate, AlgorithmConfigUpdate


class AlgorithmService:
    """算法配置业务服务"""

    def __init__(self):
        self.repo = AlgorithmRepository()

    async def create_config(
        self,
        db: AsyncSession,
        data: AlgorithmConfigCreate
    ) -> Any:
        """创建算法配置"""
        return await self.repo.create(db, obj_in=data.model_dump())

    async def create_preset(
        self,
        db: AsyncSession,
        name: str,
        algorithm_type: str,
        config: Dict[str, Any],
        description: str = ""
    ) -> Any:
        """创建预设配置"""
        return await self.repo.create_preset(
            db,
            name=name,
            algorithm_type=algorithm_type,
            config=config,
            description=description
        )

    async def get_config(
        self,
        db: AsyncSession,
        config_id: str
    ) -> Optional[Any]:
        """获取算法配置详情"""
        return await self.repo.get(db, config_id)

    async def list_configs(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """获取算法配置列表"""
        return await self.repo.get_multi(db, skip=skip, limit=limit)

    async def list_presets(
        self,
        db: AsyncSession
    ) -> List[Any]:
        """获取所有预设配置"""
        return await self.repo.get_presets(db)

    async def get_configs_by_type(
        self,
        db: AsyncSession,
        algorithm_type: str
    ) -> List[Any]:
        """根据类型获取算法配置"""
        return await self.repo.get_by_type(db, algorithm_type)

    async def update_config(
        self,
        db: AsyncSession,
        config_id: str,
        data: AlgorithmConfigUpdate
    ) -> Optional[Any]:
        """更新算法配置"""
        db_obj = await self.repo.get(db, config_id)
        if not db_obj:
            return None
        update_data = data.model_dump(exclude_unset=True)
        return await self.repo.update(db, db_obj=db_obj, obj_in=update_data)

    async def delete_config(
        self,
        db: AsyncSession,
        config_id: str
    ) -> bool:
        """删除算法配置"""
        return await self.repo.delete(db, id=config_id)

    async def get_config_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[Any]:
        """根据名称获取算法配置"""
        return await self.repo.get_by_name(db, name=name)

    async def search_configs(
        self,
        db: AsyncSession,
        algorithm_type: Optional[str] = None,
        is_preset: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """搜索算法配置"""
        return await self.repo.search(
            db,
            algorithm_type=algorithm_type,
            is_preset=is_preset,
            skip=skip,
            limit=limit
        )

    async def get_default_presets(self) -> List[Dict[str, Any]]:
        """获取默认预设配置"""
        return [
            {
                "name": "遗传算法-默认",
                "algorithm_type": "GA",
                "config": {
                    "max_iterations": 500,
                    "population_size": 50,
                    "crossover_rate": 0.8,
                    "mutation_rate": 0.1,
                    "elitism_count": 2,
                },
                "description": "遗传算法默认配置"
            },
            {
                "name": "禁忌搜索-默认",
                "algorithm_type": "TABU",
                "config": {
                    "max_iterations": 1000,
                    "tabu_list_size": 50,
                    "neighborhood_size": 20,
                },
                "description": "禁忌搜索默认配置"
            },
            {
                "name": "模拟退火-默认",
                "algorithm_type": "SA",
                "config": {
                    "max_iterations": 1000,
                    "initial_temperature": 1000.0,
                    "cooling_rate": 0.995,
                    "min_temperature": 0.001,
                },
                "description": "模拟退火默认配置"
            },
            {
                "name": "蚁群算法-默认",
                "algorithm_type": "ACO",
                "config": {
                    "max_iterations": 500,
                    "num_ants": 30,
                    "alpha": 1.0,
                    "beta": 2.0,
                    "rho": 0.5,
                },
                "description": "蚁群算法默认配置"
            },
        ]


# 全局服务实例
algorithm_service = AlgorithmService()
