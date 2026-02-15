# 大规模成像星座任务规划框架

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

卫星任务规划研究的仿真与算法测试框架，支持大规模 Walker 星座的成像任务规划。

## ✨ 核心特性

- 🛰️ **大规模星座**：支持 50-500 颗卫星的 Walker 星座配置
- 📸 **多种成像模式**：光学（推扫/敏捷）+ SAR（条带/聚束/滑动聚束）
- 🎯 **丰富目标类型**：点目标、网格目标、动态目标（车辆/舰船）、区域目标
- 📡 **测控数传站**：多天线调度、上注指令、数据下传统一建模
- ⏱️ **动作转换约束**：成像-成像/成像-数传/站间切换时间约束
- 📈 **优先级感知**：算法自动优化最大化任务总优先级收益（Total Priority Score）
- 🧬 **经典算法**：禁忌搜索、模拟退火、遗传算法、蚁群算法
- ⚡ **跨平台开发**：Mac 上使用 Mock 开发，Windows 上对接 STK 10
- 🌐 **Web可视化界面**：基于 FastAPI + Vue 3 + CesiumJS 的三维可视化平台
- 📊 **增强结果数据**：完整的数传计划、上注计划、资源时间线、约束检查详情

## 📦 安装

```bash
# 克隆项目
git clone <repo-url>
cd Paper1

# 安装依赖
pip install -r requirements.txt

# Windows 额外依赖（用于 STK 10 接口）
pip install pywin32
```

## 🚀 快速开始

### 创建 Walker 星座

```python
from constellation_planning.stk import WalkerConstellationBuilder

builder = WalkerConstellationBuilder(
    name="MySatConstellation",
    altitude_km=500,
    inclination_deg=97.4,  # 太阳同步轨道
    num_planes=6,
    sats_per_plane=10
)
satellites = builder.build()  # 60 颗卫星
print(f"Created {len(satellites)} satellites")
```

### 定义目标

```python
from constellation_planning.models import (
    PointTarget, 
    GridTarget, 
    MovingTarget
)

# 点目标
beijing = PointTarget(
    id="PT001", 
    name="Beijing", 
    latitude=39.9, 
    longitude=116.4,
    priority=0.9
)

# 网格目标 (0.1°×0.1°)
grid = GridTarget(
    id="GT001",
    name="GridCell",
    center_lat=31.2,
    center_lon=121.5,
    priority=0.7
)

# 动态目标（舰船）
ship = MovingTarget.create_ship(
    id="SH001",
    name="CargoShip",
    waypoints=[
        ("2026-01-01T00:00:00Z", 31.0, 122.0),
        ("2026-01-01T06:00:00Z", 32.0, 123.0),
        ("2026-01-01T12:00:00Z", 33.0, 124.0),
    ],
    speed_kmh=20.0
)
```

### 运行规划算法

```python
from constellation_planning.algorithms import (
    GeneticAlgorithm,
    AlgorithmConfig
)

config = AlgorithmConfig(
    max_iterations=500,
    time_limit_sec=60.0,
    random_seed=42
)

ga = GeneticAlgorithm(
    config,
    population_size=50,
    crossover_rate=0.8,
    mutation_rate=0.1
)

solution = ga.solve(observations, satellites)
print(f"Best solution: {solution.objective_value}")
```

### 设置云层遮挡区域

```python
from constellation_planning.constraints import CloudConstraint

cloud = CloudConstraint()
# 添加云层覆盖区域（多边形）
cloud.add_region([
    (30.0, 120.0),
    (30.0, 125.0),
    (35.0, 125.0),
    (35.0, 120.0),
])
```

## � 基准测试数据集

本项目包含一套标准的大规模星座任务规划基准测试数据集（v1.0-baseline），用于算法性能评估与复现。

- **星座**: 200颗混合星座（超高分/高分，光学/SAR）
- **场景**: 4个典型场景（全球均匀/亚太热点/多热点/混合分布），各1000个目标
- **评估**: 6项核心指标（完成率、总收益、资源利用率等）

### 快速运行基准测试

```bash
# 生成数据并在所有场景运行所有算法
python3 -m constellation_planning.benchmark.run_benchmark --run-all

# 查看结果可视化
open benchmark_dataset/evaluation/test_scenario_radar.png
```

详细文档: [benchmark_dataset/README.md](benchmark_dataset/README.md)

## 🌐 Web可视化界面

本项目包含基于 **FastAPI + Vue 3 + CesiumJS** 的 Web 可视化界面，提供三维地球显示、卫星轨道可视化、任务规划交互等功能。

### Web界面特性

- 🌍 **三维地球可视化**：CesiumJS 实时渲染卫星轨道、地面站、观测覆盖范围
- 🛰️ **星座设计器**：Walker 星座参数编辑，实时预览轨道
- 🎯 **目标管理**：点/区域/动态目标管理，支持批量导入
- 🧬 **算法配置**：GA/Tabu/SA/ACO 算法参数配置与预设
- ⏱️ **规划执行**：WebSocket 实时进度更新，任务队列管理
- 📊 **结果可视化**：甘特图时间线、资源利用率图表、统计面板

### Web界面快速开始

```bash
# 1. 启动后端 (需要 MySQL)
cd web_interface/backend
pip install -r requirements.txt
export DB_HOST=localhost DB_USER=planning_user DB_PASSWORD=planning_password
uvicorn main:app --reload --port 8000

# 2. 启动前端
cd web_interface/frontend
npm install
npm run dev

# 3. 访问 http://localhost:5173
```

### Docker一键启动

```bash
cd web_interface
docker-compose up -d
# 访问 http://localhost
```

详细文档: [web_interface/README.md](web_interface/README.md) | [web_interface/QUICKSTART.md](web_interface/QUICKSTART.md)

### 快速启动脚本（推荐）

项目根目录提供了一键启动/停止脚本，无需手动进入各目录：

```bash
# 1. 首次使用：安装依赖
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd web_interface/frontend && npm install && cd ../..

# 2. 启动前后端服务
./start_servers.sh

# 3. 查看服务状态
./status_servers.sh

# 4. 停止服务
./stop_servers.sh
```

**脚本说明：**

| 脚本 | 用途 | 示例 |
|------|------|------|
| `./start_servers.sh` | 同时启动前后端服务 | 启动后端(8000) + 前端(5173) |
| `./stop_servers.sh` | 停止所有服务 | 关闭前后端进程 |
| `./status_servers.sh` | 查看服务运行状态 | 显示PID和访问地址 |

**日志文件：**
- 后端日志：`logs/backend.log`
- 前端日志：`logs/frontend.log`

## 📁 项目结构

```
constellation_planning/
├── benchmark/       # 基准测试数据集与评估工具
│   ├── run_benchmark.py    # 基准测试运行器
│   └── result_enhancer.py  # 增强结果数据生成
├── config/          # 配置管理
├── models/          # 数据模型
│   ├── satellite.py        # 卫星模型
│   ├── satellite_type.py   # 卫星型号配置（转换时间/能源/存储/机动）
│   ├── imaging_mode.py     # 成像模式配置（数据速率/压缩比/功耗）
│   ├── antenna.py          # 天线模型（独立可用时间段）
│   ├── ttc_station.py      # 测控数传站（多天线/上注能力）
│   ├── uplink.py           # 上注/数传动作模型（含分段传输）
│   └── ...                  # 目标、传感器、观测窗口等
├── stk/             # STK 接口层（Mock + STK10 COM + Orekit）
├── decomposition/   # 区域分解策略
├── constraints/     # 约束检查
│   ├── transition.py       # 动作转换时间约束
│   ├── antenna_resource.py # 天线资源互斥约束
│   ├── uplink_precedence.py# 上注前置约束
│   └── ...                  # 云层/可见性/存储/能源/下传
├── scheduling/      # 调度模块
│   ├── ttc_scheduler.py    # 基础测控数传调度器
│   └── advanced_downlink.py# 高级数传（多天线聚合/分段传输）
├── algorithms/      # 优化算法（TS/SA/GA/ACO）
├── objectives/      # 优化目标函数
├── evaluation/      # 性能评估与可视化
└── utils/           # 工具函数

web_interface/           # Web可视化界面（新增）
├── backend/             # FastAPI后端
│   ├── main.py          # 应用入口（97个API端点）
│   ├── api/             # API路由（8个模块）
│   ├── services/        # 业务逻辑服务（8个）
│   ├── schemas/         # Pydantic模型（10个模块）
│   └── database/        # 数据持久层
│       ├── models.py    # SQLAlchemy ORM模型（14个表）
│       └── repositories/# 数据仓库（8个）
├── frontend/            # Vue 3前端
│   ├── src/
│   │   ├── components/  # 可视化组件（7个）
│   │   ├── views/       # 页面视图（4个）
│   │   ├── api/         # API客户端（8个）
│   │   └── stores/      # Pinia状态管理（3个）
│   └── package.json
├── docker-compose.yml   # Docker一键部署
└── README.md
```

## 🔧 支持的算法

| 算法 | 类名 | 关键参数 | 描述 |
|------|------|----------|------|
| **AWCSAT** | `AWCSAT` | `outer_loops`, `initial_inner_loops`, `tabu_tenure` | 自适应波动温控禁忌SA，论文复现 |
| 禁忌搜索 | `TabuSearch` | `tabu_tenure` | 经典禁忌搜索 |
| 模拟退火 | `SimulatedAnnealing` | `initial_temp`, `cooling_rate` | 经典模拟退火 |
| 遗传算法 | `GeneticAlgorithm` | `population_size`, `crossover_rate`, `mutation_rate` | 经典遗传算法 |
| 蚁群算法 | `AntColonyOptimization` | `num_ants`, `alpha`, `beta`, `rho` | 蚁群优化 |

> **提示**: 所有基线算法（GA, TS, SA, ACO）均已内置优先级感知能力。如果观测任务包含 `priority` 或 `score` 属性，算法将自动以最大化**总分值**为目标进行规划，而非简单的任务计数。

## 🛠️ 技术栈

### 后端
| 技术 | 用途 | 版本 |
|------|------|------|
| **FastAPI** | Web框架 | ^0.104.0 |
| **SQLAlchemy 2.0** | ORM + 异步数据库 | ^2.0.0 |
| **asyncmy** | MySQL异步驱动 | ^0.2.8 |
| **Pydantic v2** | 数据验证 | ^2.5.0 |
| **python-socketio** | WebSocket实时通信 | ^5.10.0 |

### 前端
| 技术 | 用途 | 版本 |
|------|------|------|
| **Vue 3** | 前端框架 | ^3.5.0 |
| **CesiumJS** | 三维地球可视化 | ^1.129.0 |
| **Element Plus** | UI组件库 | ^2.13.0 |
| **ECharts** | 数据可视化图表 | ^5.6.0 |
| **Pinia** | 状态管理 | ^2.3.0 |
| **Vite** | 构建工具 | ^5.4.0 |

### 数据库
- **MySQL 8.0** - 主数据库存储（星座、目标、场景、规划任务、结果）
- **14个核心表** - 覆盖卫星、目标、场景、算法配置、规划任务、观测记录、数传/上注计划等

### AWCSAT算法（推荐）

基于论文《面向点群与大区域目标的成像卫星任务规划模型与算法研究》复现的自适应波动温控禁忌模拟退火算法：

```python
from constellation_planning.algorithms import AWCSAT, AWCSATConfig

# 配置（论文推荐参数）
config = AWCSATConfig(
    outer_loops=3000,         # 外循环次数
    initial_inner_loops=200,  # 初始内循环次数
    tabu_tenure=5,            # 禁忌任期
    initial_temp_coef=0.9     # 初始温度系数
)

# 可选：自定义目标函数
def custom_objective(solution):
    return sum(solution.encoding[:, 0])

algo = AWCSAT(config, objective_func=custom_objective)
result = algo.solve(tasks, satellites)
print(f"Best: {result.objective_value}")
```

## 🎯 支持的目标类型

| 类型 | 类名 | 描述 |
|------|------|------|
| 点目标 | `PointTarget` | 固定位置地面目标 |
| 网格目标 | `GridTarget` | 0.1°×0.1° 网格单元 |
| 动态目标 | `MovingTarget` | 车辆/舰船，航点路径 |
| 区域目标 | `AreaTarget` | 多边形区域，可分解 |

## ⚙️ 约束类型

### 基础约束
- **可见性约束**：最小仰角、最大离轴角
- **云层约束**：手动设置多边形云区（光学卫星）
- **存储约束**：卫星存储容量限制
- **能源约束**：电池电量限制
- **下传约束**：地面站数据回传能力

### 动作转换约束（新增）
- **成像-成像转换**：同一卫星连续成像动作间的最小转换时间
- **成像-数传转换**：成像动作与数传动作间的最小转换时间
- **同星多站转换**：同一卫星对不同地面站数传动作间的转换时间
- **同站多星转换**：同一天线服务不同卫星间的转换时间

### 测控约束（新增）
- **上注前置约束**：成像任务必须在上注指令完成后执行
- **天线资源互斥**：同一天线同时刻只能服务一颗卫星

## 🖥️ 开发说明

支持三种轨道计算后端，通过配置切换：

| 后端 | 适用场景 | 平台 | 精度 |
|------|----------|------|------|
| `mock` | 快速开发、算法调试 | 跨平台 | 低（简化模型） |
| `orekit` | 精确仿真、算法验证 | 跨平台 | 高（Orekit） |
| `stk` | 最终部署、结果对标 | 仅 Windows | 高（STK 10） |

### Web界面与核心框架集成

Web界面（`web_interface/`）与核心规划框架（`constellation_planning/`）的关系：

```
┌─────────────────────────────────────────────────────────────┐
│                    Web可视化界面                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  星座设计器   │  │  规划执行    │  │  结果可视化  │       │
│  │  Vue3+Cesium │  │  WebSocket   │  │  甘特图+图表 │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                        │                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │            FastAPI REST API (97个端点)                 │   │
│  │  /api/constellations  /api/planning  /api/results    │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────────┐
│               星座任务规划核心框架                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │  STK连接层   │  │  约束检查    │  │  调度器      │       │
│  │  Mock/Orekit │  │  转换/资源   │  │  TTC/数传    │       │
│  └──────────────┘  └──────────────┘  └──────────────┘       │
│                        │                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              优化算法 (TS/SA/GA/ACO)                   │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

Web界面通过 REST API 调用核心框架的功能，支持：
- 创建和管理星座、目标、场景
- 配置和运行规划算法
- 实时查看规划进度（WebSocket）
- 三维可视化展示结果

### 使用 get_connector 工厂函数

```python
from constellation_planning.config import Settings
from constellation_planning.stk import get_connector

# 配置后端（可通过 YAML 文件配置）
settings = Settings(orbit_backend="orekit")  # 或 "mock", "stk"

# 自动获取对应的连接器
with get_connector(settings) as conn:
    satellites = conn.create_walker_constellation(
        name="MyConstellation",
        altitude_km=500,
        inclination_deg=97.4,
        num_planes=6,
        sats_per_plane=10
    )

# Orekit 安装（需要 conda 环境）
# conda install -c conda-forge orekit
```

## 📄 License

MIT License
