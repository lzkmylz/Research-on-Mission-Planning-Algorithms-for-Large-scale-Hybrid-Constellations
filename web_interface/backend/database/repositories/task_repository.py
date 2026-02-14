# -*- coding: utf-8 -*-
"""
规划任务数据仓库
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import joinedload

from .base import BaseRepository
from database.models import PlanningTask, TaskStatusEnum


class TaskRepository(BaseRepository[PlanningTask]):
    """规划任务数据仓库"""

    def __init__(self):
        super().__init__(PlanningTask)

    async def get_with_details(
        self,
        db: AsyncSession,
        id: str
    ) -> Optional[PlanningTask]:
        """获取任务及其关联信息"""
        result = await db.execute(
            select(PlanningTask)
            .options(
                joinedload(PlanningTask.scenario),
                joinedload(PlanningTask.algorithm_config)
            )
            .where(PlanningTask.id == id)
        )
        return result.scalar_one_or_none()

    async def get_by_status(
        self,
        db: AsyncSession,
        status: TaskStatusEnum
    ) -> List[PlanningTask]:
        """根据状态获取任务"""
        result = await db.execute(
            select(PlanningTask)
            .where(PlanningTask.status == status)
            .order_by(PlanningTask.created_at.desc())
        )
        return result.scalars().all()

    async def get_running_tasks(self, db: AsyncSession) -> List[PlanningTask]:
        """获取正在运行的任务"""
        return await self.get_by_status(db, TaskStatusEnum.RUNNING)

    async def get_by_scenario(
        self,
        db: AsyncSession,
        scenario_id: str
    ) -> List[PlanningTask]:
        """根据场景获取任务"""
        result = await db.execute(
            select(PlanningTask)
            .where(PlanningTask.scenario_id == scenario_id)
            .order_by(PlanningTask.created_at.desc())
        )
        return result.scalars().all()

    async def update_progress(
        self,
        db: AsyncSession,
        task_id: str,
        progress_pct: int,
        current_iteration: Optional[int] = None,
        best_value: Optional[float] = None
    ) -> Optional[PlanningTask]:
        """更新任务进度"""
        task = await self.get(db, task_id)
        if not task:
            return None

        task.progress_pct = progress_pct
        if current_iteration is not None:
            task.current_iteration = current_iteration
        if best_value is not None:
            task.best_value = best_value

        await db.flush()
        await db.refresh(task)
        return task

    async def mark_completed(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[PlanningTask]:
        """标记任务完成"""
        task = await self.get(db, task_id)
        if not task:
            return None

        task.status = TaskStatusEnum.COMPLETED
        task.progress_pct = 100
        task.completed_at = datetime.now()

        await db.flush()
        await db.refresh(task)
        return task

    async def mark_failed(
        self,
        db: AsyncSession,
        task_id: str,
        error_message: str
    ) -> Optional[PlanningTask]:
        """标记任务失败"""
        task = await self.get(db, task_id)
        if not task:
            return None

        task.status = TaskStatusEnum.FAILED
        task.error_message = error_message
        task.completed_at = datetime.now()

        await db.flush()
        await db.refresh(task)
        return task

    async def start_task(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[PlanningTask]:
        """启动任务"""
        task = await self.get(db, task_id)
        if not task:
            return None

        task.status = TaskStatusEnum.RUNNING
        task.started_at = datetime.now()
        task.progress_pct = 0

        await db.flush()
        await db.refresh(task)
        return task

    async def cancel_running_tasks(self, db: AsyncSession) -> int:
        """取消所有运行中的任务（用于系统重启等情况）"""
        from sqlalchemy import update

        result = await db.execute(
            update(PlanningTask)
            .where(PlanningTask.status == TaskStatusEnum.RUNNING)
            .values(
                status=TaskStatusEnum.FAILED,
                error_message="Task cancelled due to system restart",
                completed_at=datetime.now()
            )
        )
        await db.flush()
        return result.rowcount
