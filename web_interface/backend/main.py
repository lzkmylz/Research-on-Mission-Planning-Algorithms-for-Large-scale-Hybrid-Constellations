# -*- coding: utf-8 -*-
"""
FastAPI后端主应用

提供REST API和WebSocket服务。
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database.connection import init_db
from api import constellations, ground_stations, targets, scenarios, algorithms, planning, results, visualization


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    await init_db()
    print("✓ 数据库初始化完成")
    yield
    # 关闭时清理资源
    print("✓ 应用关闭")


# 创建FastAPI应用
app = FastAPI(
    title="星座任务规划系统 API",
    description="大规模成像星座任务规划框架的Web接口",
    version="1.0.0",
    lifespan=lifespan,
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(
    constellations.router,
    prefix="/api/constellations",
    tags=["星座管理"]
)

app.include_router(
    ground_stations.router,
    prefix="/api/ground-stations",
    tags=["地面站管理"]
)

app.include_router(
    targets.router,
    prefix="/api/targets",
    tags=["目标管理"]
)

app.include_router(
    scenarios.router,
    prefix="/api/scenarios",
    tags=["场景管理"]
)

app.include_router(
    algorithms.router,
    prefix="/api/algorithms",
    tags=["算法配置"]
)

app.include_router(
    planning.router,
    prefix="/api/planning",
    tags=["规划任务"]
)

app.include_router(
    results.router,
    prefix="/api/results",
    tags=["结果查询"]
)

app.include_router(
    visualization.router,
    prefix="/api/visualization",
    tags=["可视化数据"]
)

# 静态文件服务（用于前端构建输出）
frontend_dir = os.path.join(os.path.dirname(__file__), "../frontend/dist")
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")


@app.get("/api/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/api")
async def api_info():
    """API信息"""
    return {
        "name": "星座任务规划系统 API",
        "version": "1.0.0",
        "endpoints": {
            "constellations": "/api/constellations",
            "ground_stations": "/api/ground-stations",
            "targets": "/api/targets",
            "scenarios": "/api/scenarios",
            "algorithms": "/api/algorithms",
            "planning": "/api/planning",
            "results": "/api/results",
            "visualization": "/api/visualization",
        }
    }
