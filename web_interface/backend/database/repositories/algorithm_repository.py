# -*- coding: utf-8 -*-
"""
算法配置数据仓库
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from .base import BaseRepository
from database.models import AlgorithmConfig, AlgorithmTypeEnum


class AlgorithmRepository(BaseRepository[AlgorithmConfig]):
    """算法配置数据仓库"""

    def __init__(self):
        super().__init__(AlgorithmConfig)

    async def get_by_type(
        self,
        db: AsyncSession,
        algorithm_type: str
    ) -> List[AlgorithmConfig]:
        """根据类型获取算法配置"""
        result = await db.execute(
            select(AlgorithmConfig)
            .where(AlgorithmConfig.algorithm_type == AlgorithmTypeEnum(algorithm_type))
            .order_by(AlgorithmConfig.created_at.desc())
        )
        return result.scalars().all()

    async def get_presets(self, db: AsyncSession) -> List[AlgorithmConfig]:
        """获取预设配置"""
        result = await db.execute(
            select(AlgorithmConfig)
            .where(AlgorithmConfig.is_preset == True)
            .order_by(AlgorithmConfig.algorithm_type, AlgorithmConfig.name)
        )
        return result.scalars().all()

    async def get_by_name(
        self,
        db: AsyncSession,
        name: str
    ) -> Optional[AlgorithmConfig]:
        """根据名称获取配置"""
        result = await db.execute(
            select(AlgorithmConfig).where(AlgorithmConfig.name == name)
        )
        return result.scalar_one_or_none()

    async def create_preset(
        self,
        db: AsyncSession,
        *,
        name: str,
        algorithm_type: str,
        config: Dict[str, Any],
        description: str = ""
    ) -> AlgorithmConfig:
        """创建预设配置"""
        return await self.create(db, obj_in={
            "name": name,
            "algorithm_type": AlgorithmTypeEnum(algorithm_type),
            "config_json": config,
            "description": description,
            "is_preset": True,
            "max_iterations": config.get("max_iterations"),
            "time_limit_seconds": config.get("time_limit_seconds"),
            "random_seed": config.get("random_seed"),
        })

    async def search(
        self,
        db: AsyncSession,
        *,
        algorithm_type: Optional[str] = None,
        is_preset: Optional[bool] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[AlgorithmConfig]:
        """搜索算法配置"""
        query = select(AlgorithmConfig)

        if algorithm_type:
            query = query.where(
                AlgorithmConfig.algorithm_type == AlgorithmTypeEnum(algorithm_type)
            )

        if is_preset is not None:
            query = query.where(AlgorithmConfig.is_preset == is_preset)

        query = query.offset(skip).limit(limit).order_by(AlgorithmConfig.created_at.desc())

        result = await db.execute(query)
        return result.scalars().all()
