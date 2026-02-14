# -*- coding: utf-8 -*-
"""
数据库初始化脚本

用于在现有MySQL实例中创建数据库和表结构。
"""

import asyncio
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 加载 .env 文件
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✓ 已加载环境变量: {env_path}")
except ImportError:
    pass

from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from database.models import Base


async def create_database_if_not_exists():
    """创建数据库（如果不存在）"""
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "constellation_planning")

    # 连接到mysql数据库（不指定具体数据库）
    DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/mysql?charset=utf8mb4"

    engine = create_async_engine(DATABASE_URL, echo=False)

    async with engine.connect() as conn:
        # 检查数据库是否存在
        result = await conn.execute(
            text("SELECT 1 FROM information_schema.schemata WHERE schema_name = :name"),
            {"name": DB_NAME}
        )
        exists = result.scalar() is not None

        if exists:
            print(f"✓ 数据库 '{DB_NAME}' 已存在")
        else:
            # 创建数据库
            await conn.execute(text(f"CREATE DATABASE {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
            print(f"✓ 数据库 '{DB_NAME}' 创建成功")

    await engine.dispose()


async def create_tables():
    """创建所有表结构"""
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "constellation_planning")

    DATABASE_URL = f"mysql+asyncmy://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

    engine = create_async_engine(DATABASE_URL, echo=True)

    print("\n正在创建表结构...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✓ 所有表创建成功")

    # 列出创建的表
    async with engine.connect() as conn:
        result = await conn.execute(
            text("SELECT table_name FROM information_schema.tables WHERE table_schema = :name"),
            {"name": DB_NAME}
        )
        tables = [row[0] for row in result.fetchall()]
        print(f"\n共创建 {len(tables)} 个表:")
        for table in sorted(tables):
            print(f"  - {table}")

    await engine.dispose()


async def main():
    """主函数"""
    print("=" * 60)
    print("星座任务规划系统 - 数据库初始化")
    print("=" * 60)

    # 显示当前配置
    print("\n当前数据库配置:")
    print(f"  主机: {os.getenv('DB_HOST', 'localhost')}")
    print(f"  端口: {os.getenv('DB_PORT', '3306')}")
    print(f"  用户: {os.getenv('DB_USER', 'root')}")
    print(f"  数据库: {os.getenv('DB_NAME', 'constellation_planning')}")
    print()

    # 步骤1: 创建数据库
    await create_database_if_not_exists()

    # 步骤2: 创建表
    await create_tables()

    print("\n" + "=" * 60)
    print("✓ 数据库初始化完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
