# -*- coding: utf-8 -*-
"""
数据库连接管理

提供异步MySQL数据库连接池和会话管理。
"""

import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# 加载 .env 文件 - 确保在配置之前加载
from dotenv import load_dotenv

# 获取项目根目录（backend目录）
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
env_path = os.path.join(backend_dir, '.env')

if os.path.exists(env_path):
    load_dotenv(env_path, override=True)  # override=True 确保 .env 文件覆盖现有环境变量
    print(f"✓ 已加载环境变量: {env_path}")
else:
    print(f"⚠ 未找到 .env 文件: {env_path}")

# 数据库配置
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "planning_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "planning_password")
DB_NAME = os.getenv("DB_NAME", "constellation_planning")

# 构建异步数据库URL
DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# 创建异步引擎
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # 生产环境设为False
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # 连接健康检查
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 声明性基类
Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """获取数据库会话的依赖函数

    用于FastAPI的依赖注入。

    Yields:
        AsyncSession: 异步数据库会话
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """初始化数据库

    创建所有表结构。
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_db():
    """删除所有表（仅用于测试）

    警告：这将删除所有数据！
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
