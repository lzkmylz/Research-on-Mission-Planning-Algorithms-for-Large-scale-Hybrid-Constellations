# -*- coding: utf-8 -*-
"""
卫星数据仓库

提供卫星的CRUD操作。
"""

from typing import Optional, List, Any
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Satellite
from .base import BaseRepository


class SatelliteRepository(BaseRepository[Satellite]):
    """卫星数据仓库"""

    def __init__(self):
        super().__init__(Satellite)

    async def get_by_name(self, db: AsyncSession, name: str) -> Optional[Satellite]:
        """根据名称获取卫星

        Args:
            db: 数据库会话
            name: 卫星名称

        Returns:
            卫星对象或None
        """
        result = await db.execute(
            select(self.model).where(self.model.name == name)
        )
        return result.scalar_one_or_none()

    async def get_by_norad_id(self, db: AsyncSession, norad_id: str) -> Optional[Satellite]:
        """根据NORAD ID获取卫星

        Args:
            db: 数据库会话
            norad_id: NORAD ID

        Returns:
            卫星对象或None
        """
        result = await db.execute(
            select(self.model).where(self.model.norad_id == norad_id)
        )
        return result.scalar_one_or_none()

    async def get_by_constellation(
        self,
        db: AsyncSession,
        constellation_name: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Satellite]:
        """根据星座名称获取卫星列表

        Args:
            db: 数据库会话
            constellation_name: 星座名称
            skip: 跳过记录数
            limit: 返回记录数上限

        Returns:
            卫星列表
        """
        result = await db.execute(
            select(self.model)
            .where(self.model.constellation_name == constellation_name)
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search(
        self,
        db: AsyncSession,
        query: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Satellite]:
        """搜索卫星

        Args:
            db: 数据库会话
            query: 搜索关键词
            skip: 跳过记录数
            limit: 返回记录数上限

        Returns:
            卫星列表
        """
        from sqlalchemy import func as sql_func
        search_pattern = f"%{query}%"
        result = await db.execute(
            select(self.model)
            .where(
                or_(
                    sql_func.lower(self.model.name).like(sql_func.lower(search_pattern)),
                    sql_func.lower(self.model.norad_id).like(sql_func.lower(search_pattern)),
                    sql_func.lower(self.model.satellite_code).like(sql_func.lower(search_pattern)),
                    sql_func.lower(self.model.constellation_name).like(sql_func.lower(search_pattern))
                )
            )
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def count_search(self, db: AsyncSession, query: str) -> int:
        """获取搜索结果总数

        Args:
            db: 数据库会话
            query: 搜索关键词

        Returns:
            记录总数
        """
        from sqlalchemy import func as sql_func
        search_pattern = f"%{query}%"
        result = await db.execute(
            select(func.count())
            .select_from(self.model)
            .where(
                or_(
                    sql_func.lower(self.model.name).like(sql_func.lower(search_pattern)),
                    sql_func.lower(self.model.norad_id).like(sql_func.lower(search_pattern)),
                    sql_func.lower(self.model.satellite_code).like(sql_func.lower(search_pattern)),
                    sql_func.lower(self.model.constellation_name).like(sql_func.lower(search_pattern))
                )
            )
        )
        return result.scalar()

    async def get_multi_with_total(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> tuple[List[Satellite], int]:
        """获取多个实体（分页）并返回总数

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数上限
            order_by: 排序字段

        Returns:
            (实体列表, 总数) 元组
        """
        # 获取总数
        total = await self.count(db)

        # 获取分页数据
        query = select(self.model)

        if order_by:
            if hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                query = query.order_by(order_column.desc())

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        items = result.scalars().all()

        return items, total
