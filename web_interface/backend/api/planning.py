# -*- coding: utf-8 -*-
"""
规划任务API（包含WebSocket）
"""

import asyncio
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from services.planning_service import planning_service
from schemas.planning_schemas import (
    PlanningTaskCreate, PlanningTaskUpdate, PlanningTaskResponse, PlanningTaskList,
    PlanningTaskDetailResponse, TaskControlRequest, TaskControlResponse,
    TaskFilterRequest, TaskStatisticsResponse, BatchTaskCreateRequest,
    BatchTaskCreateResponse, BatchTaskControlRequest, BatchTaskControlResponse,
    TaskProgressUpdateRequest, TaskStatusUpdateRequest
)
from database.models import TaskStatusEnum

router = APIRouter()

# WebSocket连接管理器
class ConnectionManager:
    """WebSocket连接管理器"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}
        self.task_subscribers: dict[str, set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        """接受WebSocket连接"""
        await websocket.accept()
        self.active_connections[client_id] = websocket

    def disconnect(self, client_id: str):
        """断开WebSocket连接"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]

        # 从所有任务订阅中移除
        for task_id, subscribers in self.task_subscribers.items():
            subscribers.discard(client_id)

    def subscribe_to_task(self, client_id: str, task_id: str):
        """订阅任务更新"""
        if task_id not in self.task_subscribers:
            self.task_subscribers[task_id] = set()
        self.task_subscribers[task_id].add(client_id)

    def unsubscribe_from_task(self, client_id: str, task_id: str):
        """取消订阅任务更新"""
        if task_id in self.task_subscribers:
            self.task_subscribers[task_id].discard(client_id)

    async def send_to_client(self, client_id: str, message: dict):
        """发送消息给指定客户端"""
        if client_id in self.active_connections:
            try:
                await self.active_connections[client_id].send_json(message)
            except Exception:
                pass

    async def broadcast_to_task(self, task_id: str, message: dict):
        """广播消息给所有订阅该任务的客户端"""
        if task_id in self.task_subscribers:
            for client_id in list(self.task_subscribers[task_id]):
                await self.send_to_client(client_id, message)

    async def broadcast_progress(self, task_id: str, progress: int, iteration: int, best_value: Optional[float] = None):
        """广播任务进度"""
        await self.broadcast_to_task(task_id, {
            "type": "progress",
            "task_id": task_id,
            "progress_pct": progress,
            "current_iteration": iteration,
            "best_value": best_value,
            "timestamp": datetime.now().isoformat()
        })

    async def broadcast_status(self, task_id: str, status: str, message: str = ""):
        """广播任务状态变更"""
        await self.broadcast_to_task(task_id, {
            "type": "status",
            "task_id": task_id,
            "status": status,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })


# 全局连接管理器实例
manager = ConnectionManager()


# ========== REST API端点 ==========

@router.get("", response_model=PlanningTaskList)
async def list_planning_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[TaskStatusEnum] = None,
    scenario_id: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取规划任务列表"""
    if status:
        tasks = await planning_service.get_tasks_by_status(db, status.value)
    elif scenario_id:
        tasks = await planning_service.get_tasks_by_scenario(db, scenario_id)
    else:
        tasks = await planning_service.list_tasks(db, skip=skip, limit=limit)

    return {
        "total": len(tasks),
        "items": tasks
    }


@router.post("", response_model=PlanningTaskResponse)
async def create_planning_task(
    task: PlanningTaskCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建规划任务"""
    try:
        db_task = await planning_service.create_task(db, task)
        return db_task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}", response_model=PlanningTaskDetailResponse)
async def get_planning_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取规划任务详情"""
    task = await planning_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    return {
        "id": task.id,
        "scenario_id": task.scenario_id,
        "algorithm_config_id": task.algorithm_config_id,
        "status": task.status,
        "progress_pct": task.progress_pct,
        "current_iteration": task.current_iteration,
        "best_value": task.best_value,
        "started_at": task.started_at,
        "completed_at": task.completed_at,
        "error_message": task.error_message,
        "created_at": task.created_at,
        "scenario": None,  # 需要时从关联对象获取
        "algorithm_config": None,
        "result": None,
        "logs": []
    }


@router.put("/{task_id}", response_model=PlanningTaskResponse)
async def update_planning_task(
    task_id: str,
    task_update: PlanningTaskUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新规划任务"""
    # 这里应该实现更新逻辑
    task = await planning_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 只允许更新特定字段
    if task_update.progress_pct is not None:
        progress_data = TaskProgressUpdateRequest(
            progress_pct=task_update.progress_pct,
            current_iteration=task_update.current_iteration or 0,
            best_value=task_update.best_value
        )
        updated = await planning_service.update_progress(db, task_id, progress_data)
        if updated:
            # 广播进度更新
            await manager.broadcast_progress(
                task_id,
                task_update.progress_pct,
                task_update.current_iteration or 0,
                task_update.best_value
            )

    return await planning_service.get_task(db, task_id)


@router.delete("/{task_id}")
async def delete_planning_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除规划任务"""
    task = await planning_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    # 如果任务正在运行，先取消
    if task.status == TaskStatusEnum.RUNNING:
        raise HTTPException(status_code=400, detail="任务正在运行，请先取消")

    deleted = await planning_service.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=500, detail="删除失败")

    return {"message": "任务已删除"}


# ========== 任务控制端点 ==========

@router.post("/{task_id}/start", response_model=PlanningTaskResponse)
async def start_planning_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """启动规划任务"""
    task = await planning_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status not in [TaskStatusEnum.PENDING, TaskStatusEnum.FAILED]:
        raise HTTPException(status_code=400, detail=f"任务状态为 {task.status}，无法启动")

    started = await planning_service.start_task(db, task_id)
    if not started:
        raise HTTPException(status_code=500, detail="启动任务失败")

    # 广播状态变更
    await manager.broadcast_status(task_id, "running", "任务已启动")

    return started


@router.post("/{task_id}/cancel", response_model=TaskControlResponse)
async def cancel_planning_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """取消规划任务"""
    task = await planning_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    if task.status not in [TaskStatusEnum.PENDING, TaskStatusEnum.RUNNING]:
        raise HTTPException(status_code=400, detail=f"任务状态为 {task.status}，无法取消")

    cancelled = await planning_service.cancel_task(db, task_id)
    if not cancelled:
        raise HTTPException(status_code=500, detail="取消任务失败")

    # 广播状态变更
    await manager.broadcast_status(task_id, "cancelled", "任务已取消")

    return {
        "task_id": task_id,
        "action": "cancel",
        "success": True,
        "message": "任务已取消",
        "new_status": TaskStatusEnum.FAILED
    }


@router.post("/{task_id}/complete", response_model=PlanningTaskResponse)
async def complete_planning_task(
    task_id: str,
    db: AsyncSession = Depends(get_db)
):
    """标记任务完成（内部使用）"""
    task = await planning_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    completed = await planning_service.mark_completed(db, task_id)
    if not completed:
        raise HTTPException(status_code=500, detail="标记完成失败")

    # 广播状态变更
    await manager.broadcast_status(task_id, "completed", "任务已完成")

    return completed


@router.post("/{task_id}/fail", response_model=PlanningTaskResponse)
async def fail_planning_task(
    task_id: str,
    error_message: str = "任务执行失败",
    db: AsyncSession = Depends(get_db)
):
    """标记任务失败（内部使用）"""
    task = await planning_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")

    failed = await planning_service.mark_failed(db, task_id, error_message)
    if not failed:
        raise HTTPException(status_code=500, detail="标记失败状态失败")

    # 广播状态变更
    await manager.broadcast_status(task_id, "failed", error_message)

    return failed


# ========== 批量操作端点 ==========

@router.post("/batch", response_model=BatchTaskCreateResponse)
async def batch_create_tasks(
    request: BatchTaskCreateRequest,
    db: AsyncSession = Depends(get_db)
):
    """批量创建规划任务"""
    result = await planning_service.create_batch_tasks(
        db, request.scenario_id, request.algorithm_config_ids
    )
    return {
        "created_count": result["created_count"],
        "task_ids": result["task_ids"],
        "errors": result["errors"]
    }


@router.post("/batch/control", response_model=BatchTaskControlResponse)
async def batch_control_tasks(
    request: BatchTaskControlRequest,
    db: AsyncSession = Depends(get_db)
):
    """批量控制任务"""
    success_count = 0
    errors = []

    for task_id in request.task_ids:
        try:
            task = await planning_service.get_task(db, task_id)
            if not task:
                errors.append({"task_id": task_id, "error": "任务不存在"})
                continue

            if request.action == "cancel":
                if task.status in [TaskStatusEnum.PENDING, TaskStatusEnum.RUNNING]:
                    await planning_service.cancel_task(db, task_id)
                    await manager.broadcast_status(task_id, "cancelled", "任务已取消")
                    success_count += 1
                else:
                    errors.append({"task_id": task_id, "error": f"任务状态为 {task.status}，无法取消"})
            elif request.action == "delete":
                if task.status == TaskStatusEnum.RUNNING:
                    errors.append({"task_id": task_id, "error": "任务正在运行，请先取消"})
                else:
                    await planning_service.delete_task(db, task_id)
                    success_count += 1
            else:
                errors.append({"task_id": task_id, "error": f"未知操作: {request.action}"})

        except Exception as e:
            errors.append({"task_id": task_id, "error": str(e)})

    return {
        "success_count": success_count,
        "failed_count": len(errors),
        "errors": errors
    }


# ========== 统计端点 ==========

@router.get("/statistics", response_model=TaskStatisticsResponse)
async def get_task_statistics(
    db: AsyncSession = Depends(get_db)
):
    """获取任务统计信息"""
    stats = await planning_service.get_task_statistics(db)

    return {
        "total_count": stats["total_count"],
        "pending_count": stats["pending_count"],
        "running_count": stats["running_count"],
        "completed_count": stats["completed_count"],
        "failed_count": stats["failed_count"],
        "avg_runtime_seconds": None,  # 需要计算
        "avg_completion_rate": None
    }


@router.get("/running", response_model=PlanningTaskList)
async def get_running_tasks(
    db: AsyncSession = Depends(get_db)
):
    """获取正在运行的任务"""
    tasks = await planning_service.get_running_tasks(db)
    return {
        "total": len(tasks),
        "items": tasks
    }


# ========== WebSocket端点 ==========

@router.websocket("/ws/{task_id}")
async def task_websocket(websocket: WebSocket, task_id: str):
    """任务进度WebSocket"""
    client_id = f"{task_id}_{id(websocket)}"
    await manager.connect(websocket, client_id)
    manager.subscribe_to_task(client_id, task_id)

    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "task_id": task_id,
            "message": "已连接到任务进度服务"
        })

        while True:
            # 接收客户端消息
            data = await websocket.receive_json()

            if data.get("action") == "subscribe":
                # 订阅任务
                task_id_to_subscribe = data.get("task_id", task_id)
                manager.subscribe_to_task(client_id, task_id_to_subscribe)
                await websocket.send_json({
                    "type": "subscribed",
                    "task_id": task_id_to_subscribe
                })

            elif data.get("action") == "unsubscribe":
                # 取消订阅
                task_id_to_unsubscribe = data.get("task_id", task_id)
                manager.unsubscribe_from_task(client_id, task_id_to_unsubscribe)
                await websocket.send_json({
                    "type": "unsubscribed",
                    "task_id": task_id_to_unsubscribe
                })

            elif data.get("action") == "ping":
                # 心跳响应
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        manager.disconnect(client_id)
        raise


@router.websocket("/ws")
async def general_websocket(websocket: WebSocket):
    """通用WebSocket连接（可订阅多个任务）"""
    client_id = f"general_{id(websocket)}"
    await manager.connect(websocket, client_id)

    try:
        await websocket.send_json({
            "type": "connected",
            "message": "已连接到规划任务服务"
        })

        while True:
            data = await websocket.receive_json()

            if data.get("action") == "subscribe":
                task_id = data.get("task_id")
                if task_id:
                    manager.subscribe_to_task(client_id, task_id)
                    await websocket.send_json({
                        "type": "subscribed",
                        "task_id": task_id
                    })

            elif data.get("action") == "unsubscribe":
                task_id = data.get("task_id")
                if task_id:
                    manager.unsubscribe_from_task(client_id, task_id)
                    await websocket.send_json({
                        "type": "unsubscribed",
                        "task_id": task_id
                    })

            elif data.get("action") == "ping":
                await websocket.send_json({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                })

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        manager.disconnect(client_id)
        raise
