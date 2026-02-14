# 快速启动指南

## 项目概述

星座任务规划系统 Web界面 - 基于FastAPI + Vue 3 + CesiumJS的三维可视化平台。

## 环境要求

- Python 3.11+
- Node.js 18+
- MySQL 8.0

## 快速启动

### 1. 启动数据库

```bash
# macOS
brew install mysql
brew services start mysql

# 创建数据库
mysql -u root -p -e "CREATE DATABASE constellation_planning CHARACTER SET utf8mb4;"
mysql -u root -p -e "CREATE USER 'planning_user'@'localhost' IDENTIFIED BY 'planning_password';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON constellation_planning.* TO 'planning_user'@'localhost';"
```

### 2. 启动后端

```bash
cd web_interface/backend

# 安装依赖（首次）
pip install -r requirements.txt

# 设置环境变量
export DB_HOST=localhost
export DB_PORT=3306
export DB_USER=planning_user
export DB_PASSWORD=planning_password
export DB_NAME=constellation_planning

# 启动服务
uvicorn main:app --reload --port 8000
```

后端服务启动后访问：
- API文档: http://localhost:8000/docs
- API端点: http://localhost:8000/api

### 3. 启动前端

```bash
cd web_interface/frontend

# 安装依赖（首次）
npm install

# 启动开发服务器
npm run dev
```

前端访问：http://localhost:5173

## Docker一键启动

```bash
cd web_interface
docker-compose up -d
```

访问：http://localhost

## 项目结构

```
web_interface/
├── backend/              # FastAPI后端
│   ├── api/              # API路由 (8个模块, 97个端点)
│   ├── services/         # 业务逻辑 (8个服务)
│   ├── schemas/          # Pydantic模型 (10个模块)
│   ├── database/         # 数据库层
│   │   ├── models.py     # SQLAlchemy模型
│   │   └── repositories/ # 数据仓库 (8个)
│   └── main.py           # 应用入口
└── frontend/             # Vue 3前端
    ├── src/
    │   ├── components/   # 可视化组件 (7个)
    │   ├── views/        # 页面视图 (4个)
    │   ├── api/          # API客户端 (8个)
    │   └── stores/       # Pinia状态管理 (3个)
    └── package.json
```

## API模块

| 模块 | 端点数 | 说明 |
|------|--------|------|
| constellations | 7 | 星座管理 |
| ground-stations | 6 | 地面站管理 |
| targets | 14 | 目标管理 |
| scenarios | 10 | 场景管理 |
| algorithms | 13 | 算法配置 |
| planning | 13 | 规划任务 (含WebSocket) |
| results | 17 | 结果查询 |
| visualization | 11 | 可视化数据 |

## 功能特性

1. **星座设计器** - 三维地球显示，卫星轨道可视化
2. **目标管理** - 点/区域/动态目标管理，批量导入
3. **算法配置** - GA/Tabu/SA/ACO算法，参数预设
4. **规划执行** - 场景选择，实时进度更新
5. **结果可视化** - 轨道动画，甘特图，资源图表

## 常见问题

### 数据库连接失败
检查环境变量是否正确设置，MySQL服务是否启动。

### 前端无法连接后端
检查后端是否运行在8000端口，前端vite.config.js中的代理配置。

### Cesium显示问题
确保浏览器支持WebGL，检查网络连接。

## 开发文档

- 后端API文档: http://localhost:8000/docs
- 数据库模型: `backend/database/models.py`
- 前端组件: `frontend/src/components/`
