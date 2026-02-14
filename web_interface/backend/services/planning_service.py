# -*- coding: utf-8 -*-
"""
规划任务业务逻辑服务
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from database.repositories import TaskRepository, ScenarioRepository
from database.models import TaskStatusEnum
from schemas.planning_schemas import PlanningTaskCreate, TaskProgressUpdateRequest


class PlanningService:
    """规划任务业务服务"""

    def __init__(self):
        self.repo = TaskRepository()
        self.scenario_repo = ScenarioRepository()

    async def create_task(
        self,
        db: AsyncSession,
        data: PlanningTaskCreate
    ) -> Any:
        """创建规划任务"""
        # 验证场景存在
        scenario = await self.scenario_repo.get(db, data.scenario_id)
        if not scenario:
            raise ValueError(f"场景不存在: {data.scenario_id}")

        return await self.repo.create(db, obj_in=data.model_dump())

    async def get_task(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[Any]:
        """获取任务详情"""
        return await self.repo.get_with_details(db, id=task_id)

    async def list_tasks(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100
    ) -> List[Any]:
        """获取任务列表"""
        return await self.repo.get_multi(db, skip=skip, limit=limit)

    async def get_tasks_by_status(
        self,
        db: AsyncSession,
        status: str
    ) -> List[Any]:
        """根据状态获取任务"""
        status_enum = TaskStatusEnum(status)
        return await self.repo.get_by_status(db, status_enum)

    async def get_running_tasks(
        self,
        db: AsyncSession
    ) -> List[Any]:
        """获取正在运行的任务"""
        return await self.repo.get_running_tasks(db)

    async def get_tasks_by_scenario(
        self,
        db: AsyncSession,
        scenario_id: str
    ) -> List[Any]:
        """根据场景获取任务"""
        return await self.repo.get_by_scenario(db, scenario_id)

    async def start_task(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[Any]:
        """启动任务"""
        return await self.repo.start_task(db, task_id)

    async def update_progress(
        self,
        db: AsyncSession,
        task_id: str,
        data: TaskProgressUpdateRequest
    ) -> Optional[Any]:
        """更新任务进度"""
        return await self.repo.update_progress(
            db,
            task_id=task_id,
            progress_pct=data.progress_pct,
            current_iteration=data.current_iteration,
            best_value=data.best_value
        )

    async def mark_completed(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[Any]:
        """标记任务完成"""
        return await self.repo.mark_completed(db, task_id)

    async def mark_failed(
        self,
        db: AsyncSession,
        task_id: str,
        error_message: str
    ) -> Optional[Any]:
        """标记任务失败"""
        return await self.repo.mark_failed(db, task_id, error_message)

    async def cancel_task(
        self,
        db: AsyncSession,
        task_id: str
    ) -> Optional[Any]:
        """取消任务"""
        return await self.repo.mark_failed(db, task_id, "Task cancelled by user")

    async def delete_task(
        self,
        db: AsyncSession,
        task_id: str
    ) -> bool:
        """删除任务"""
        return await self.repo.delete(db, id=task_id)

    async def cancel_running_tasks(
        self,
        db: AsyncSession
    ) -> int:
        """取消所有运行中的任务（用于系统重启等情况）"""
        return await self.repo.cancel_running_tasks(db)

    async def create_batch_tasks(
        self,
        db: AsyncSession,
        scenario_id: str,
        algorithm_config_ids: List[str]
    ) -> Dict[str, Any]:
        """批量创建任务"""
        created_tasks = []
        errors = []

        for config_id in algorithm_config_ids:
            try:
                task_data = PlanningTaskCreate(
                    scenario_id=scenario_id,
                    algorithm_config_id=config_id
                )
                task = await self.create_task(db, task_data)
                created_tasks.append(task.id)
            except Exception as e:
                errors.append({
                    "algorithm_config_id": config_id,
                    "error": str(e)
                })

        return {
            "created_count": len(created_tasks),
            "task_ids": created_tasks,
            "errors": errors
        }

    async def get_task_statistics(
        self,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """获取任务统计信息"""
        pending = await self.repo.get_by_status(db, TaskStatusEnum.PENDING)
        running = await self.repo.get_by_status(db, TaskStatusEnum.RUNNING)
        completed = await self.repo.get_by_status(db, TaskStatusEnum.COMPLETED)
        failed = await self.repo.get_by_status(db, TaskStatusEnum.FAILED)

        return {
            "total_count": len(pending) + len(running) + len(completed) + len(failed),
            "pending_count": len(pending),
            "running_count": len(running),
            "completed_count": len(completed),
            "failed_count": len(failed),
        }


# 全局服务实例
planning_service = PlanningService()
