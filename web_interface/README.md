# 星座任务规划系统 Web界面

基于FastAPI + Vue 3 + CesiumJS的三维可视化Web界面，用于大规模成像星座任务规划。

## 功能特性

### 1. 星座设计器
- 三维地球显示（Cesium）
- 卫星轨道可视化
- Walker星座参数编辑器
- 卫星类型配置（光学/SAR）

### 2. 目标管理
- 点目标、区域目标、动态目标管理
- 目标优先级设置
- 批量导入/导出

### 3. 算法配置
- 支持GA/Tabu/SA/ACO算法
- 参数预设保存/加载
- 算法对比分析

### 4. 规划执行
- 场景选择和算法配置
- 实时进度更新（WebSocket）
- 中间结果展示

### 5. 结果可视化
- 卫星轨道动画
- 观测覆盖范围
- 甘特图时间线
- 资源使用图表

## 快速开始

### 方式一：本地开发环境

#### 1. 数据库准备

```bash
# 安装MySQL（如未安装）
brew install mysql  # macOS
# 或
sudo apt-get install mysql-server  # Ubuntu

# 创建数据库
mysql -u root -p -e "CREATE DATABASE constellation_planning CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "CREATE USER 'planning_user'@'localhost' IDENTIFIED BY 'planning_password';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON constellation_planning.* TO 'planning_user'@'localhost';"
```

#### 2. 启动后端

```bash
cd backend

# 安装依赖（如未安装）
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

后端API文档：http://localhost:8000/docs

#### 3. 启动前端

```bash
cd frontend

# 安装依赖（如未安装）
npm install

# 启动开发服务器
npm run dev
```

访问：http://localhost:5173

### 方式二：Docker部署

```bash
# 启动所有服务
docker-compose up -d

# 访问Web界面
open http://localhost
```

## 项目结构

```
web_interface/
├── docker-compose.yml          # Docker编排配置
├── backend/                    # FastAPI后端
│   ├── main.py                 # 应用入口
│   ├── requirements.txt        # Python依赖
│   ├── Dockerfile              # 后端镜像
│   ├── api/                    # API路由
│   │   ├── constellations.py   # 星座管理
│   │   ├── ground_stations.py  # 地面站管理
│   │   ├── targets.py          # 目标管理
│   │   ├── scenarios.py        # 场景管理
│   │   ├── algorithms.py       # 算法配置
│   │   ├── planning.py         # 规划任务
│   │   ├── results.py          # 结果查询
│   │   └── visualization.py    # 可视化数据
│   ├── services/               # 业务逻辑层
│   ├── schemas/                # Pydantic模型
│   └── database/               # 数据持久层
│       ├── models.py           # SQLAlchemy模型
│       ├── repositories/       # 数据仓库
│       └── connection.py       # 数据库连接
└── frontend/                   # Vue 3前端
    ├── package.json            # Node依赖
    ├── Dockerfile              # 前端镜像
    ├── nginx.conf              # Nginx配置
    ├── vite.config.js          # Vite配置
    ├── src/
    │   ├── main.js             # 应用入口
    │   ├── App.vue             # 根组件
    │   ├── api/                # API客户端
    │   ├── components/         # 可复用组件
    │   │   ├── CesiumViewer.vue
    │   │   ├── SatelliteEditor.vue
    │   │   ├── TargetManager.vue
    │   │   ├── AlgorithmPanel.vue
    │   │   ├── ResultViewer.vue
    │   │   ├── TimelineChart.vue
    │   │   └── ResourceChart.vue
    │   ├── views/              # 页面视图
    │   │   ├── Home.vue
    │   │   ├── ConstellationDesigner.vue
    │   │   ├── Planning.vue
    │   │   └── Results.vue
    │   ├── stores/             # Pinia状态管理
    │   ├── router/             # 路由配置
    │   └── utils/              # 工具函数
    └── index.html
```

## API端点

### 星座管理
- `GET /api/constellations` - 获取星座列表
- `POST /api/constellations` - 创建星座
- `GET /api/constellations/{id}` - 获取星座详情
- `PUT /api/constellations/{id}` - 更新星座
- `DELETE /api/constellations/{id}` - 删除星座

### 目标管理
- `GET /api/targets` - 获取目标列表
- `POST /api/targets` - 创建目标
- `POST /api/targets/batch` - 批量创建目标
- `GET /api/targets/{id}` - 获取目标详情

### 场景管理
- `GET /api/scenarios` - 获取场景列表
- `POST /api/scenarios` - 创建场景
- `GET /api/scenarios/{id}` - 获取场景详情
- `POST /api/scenarios/{id}/clone` - 复制场景

### 算法配置
- `GET /api/algorithms` - 获取算法配置列表
- `POST /api/algorithms` - 创建算法配置
- `GET /api/algorithms/presets` - 获取预设配置

### 规划任务
- `GET /api/planning` - 获取任务列表
- `POST /api/planning` - 创建任务
- `POST /api/planning/{id}/start` - 启动任务
- `POST /api/planning/{id}/cancel` - 取消任务
- `WS /api/planning/ws/{id}` - 任务进度WebSocket

### 结果查询
- `GET /api/results` - 获取结果列表
- `GET /api/results/{id}` - 获取结果详情
- `GET /api/results/{id}/observations` - 获取观测记录
- `GET /api/results/{id}/downlinks` - 获取数传计划
- `GET /api/results/{id}/violations` - 获取约束违规

### 可视化数据
- `GET /api/visualization/satellites/{scenario_id}` - 卫星位置
- `GET /api/visualization/observations/{result_id}` - 观测可视化
- `GET /api/visualization/timeline/observations/{result_id}` - 观测时间线

## 技术栈

### 后端
- **框架**: FastAPI (Python 3.11+)
- **数据库**: MySQL 8.0 + SQLAlchemy 2.0 (异步)
- **迁移**: Alembic
- **WebSocket**: python-socketio

### 前端
- **框架**: Vue 3 + Vite
- **UI组件**: Element Plus
- **三维可视化**: CesiumJS
- **图表**: ECharts
- **状态管理**: Pinia
- **路由**: Vue Router

## 开发说明

### 后端开发

```bash
cd backend

# 安装开发依赖
pip install -r requirements.txt

# 数据库迁移
alembic init migrations
alembic revision --autogenerate -m "initial"
alembic upgrade head

# 运行开发服务器
uvicorn main:app --reload --port 8000
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 运行开发服务器
npm run dev

# 构建生产版本
npm run build
```

## 注意事项

1. **数据库连接**: 确保MySQL服务已启动且配置正确
2. **Cesium Token**: 如需使用Cesium ion服务，请在`CesiumViewer.vue`中配置access token
3. **跨域**: 后端已配置CORS允许所有来源，生产环境应限制具体域名

## 许可证

MIT License
