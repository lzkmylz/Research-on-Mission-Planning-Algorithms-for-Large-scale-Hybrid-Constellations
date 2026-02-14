# -*- coding: utf-8 -*-
"""
基础数据仓库类

提供通用的CRUD操作。
"""

from typing import Generic, TypeVar, Type, Optional, List, Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from sqlalchemy.orm import joinedload

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """基础数据仓库

    提供通用的数据库操作方法。
    """

    def __init__(self, model: Type[ModelType]):
        """
        Args:
            model: SQLAlchemy模型类
        """
        self.model = model

    async def get(self, db: AsyncSession, id: str) -> Optional[ModelType]:
        """根据ID获取单个实体

        Args:
            db: 数据库会话
            id: 实体ID

        Returns:
            实体对象或None
        """
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[ModelType]:
        """获取多个实体（分页）

        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 返回记录数上限
            order_by: 排序字段

        Returns:
            实体列表
        """
        query = select(self.model)

        if order_by:
            if hasattr(self.model, order_by):
                order_column = getattr(self.model, order_by)
                query = query.order_by(order_column.desc())

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_all(self, db: AsyncSession) -> List[ModelType]:
        """获取所有实体

        Args:
            db: 数据库会话

        Returns:
            实体列表
        """
        result = await db.execute(select(self.model))
        return result.scalars().all()

    async def create(self, db: AsyncSession, *, obj_in: Dict[str, Any]) -> ModelType:
        """创建新实体

        Args:
            db: 数据库会话
            obj_in: 实体数据字典

        Returns:
            创建的实体
        """
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Dict[str, Any]
    ) -> ModelType:
        """更新实体

        Args:
            db: 数据库会话
            db_obj: 现有实体对象
            obj_in: 更新的数据

        Returns:
            更新后的实体
        """
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)

        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, *, id: str) -> bool:
        """删除实体

        Args:
            db: 数据库会话
            id: 实体ID

        Returns:
            是否成功删除
        """
        result = await db.execute(
            delete(self.model).where(self.model.id == id)
        )
        await db.flush()
        return result.rowcount > 0

    async def count(self, db: AsyncSession) -> int:
        """获取记录总数

        Args:
            db: 数据库会话

        Returns:
            记录总数
        """
        result = await db.execute(select(func.count()).select_from(self.model))
        return result.scalar()

    async def exists(self, db: AsyncSession, *, id: str) -> bool:
        """检查实体是否存在

        Args:
            db: 数据库会话
            id: 实体ID

        Returns:
            是否存在
        """
        result = await db.execute(
            select(func.count()).select_from(self.model).where(self.model.id == id)
        )
        return result.scalar() > 0
