# 大规模成像星座任务规划框架

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

卫星任务规划研究的仿真与算法测试框架，支持大规模 Walker 星座的成像任务规划。

## ✨ 核心特性

- 🛰️ **大规模星座**：支持 50-500 颗卫星的 Walker 星座配置
- 📸 **多种成像模式**：光学（推扫/敏捷）+ SAR（条带/聚束/滑动聚束）
- 🎯 **丰富目标类型**：点目标、网格目标、动态目标（车辆/舰船）、区域目标
- 📡 **地面站仿真**：支持数据回传约束建模
- 📈 **优先级感知**：算法自动优化最大化任务总优先级收益（Total Priority Score）
- 🧬 **经典算法**：禁忌搜索、模拟退火、遗传算法、蚁群算法
- ⚡ **跨平台开发**：Mac 上使用 Mock 开发，Windows 上对接 STK 10

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

## �📁 项目结构

```
constellation_planning/
├── benchmark/       # 基准测试数据集与评估工具
├── config/          # 配置管理
├── models/          # 数据模型（卫星、传感器、目标、地面站）
├── stk/             # STK 接口层（Mock + STK10 COM）
├── decomposition/   # 区域分解策略
├── constraints/     # 约束检查（云层/可见性/存储/能源/下传）
├── algorithms/      # 优化算法（TS/SA/GA/ACO）
├── objectives/      # 优化目标函数
├── evaluation/      # 性能评估与可视化
└── utils/           # 工具函数
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

- **可见性约束**：最小仰角、最大离轴角
- **云层约束**：手动设置多边形云区（光学卫星）
- **存储约束**：卫星存储容量限制
- **能源约束**：电池电量限制
- **下传约束**：地面站数据回传能力

## 🖥️ 开发说明

- **Mac 开发**：使用 `MockSTKConnector` 进行算法开发和测试
- **Windows 部署**：切换到 `STK10Connector` 对接真实 STK

```python
from constellation_planning.stk import MockSTKConnector

# Mac 开发
with MockSTKConnector() as stk:
    satellites = stk.create_walker_constellation(...)
```

## 📄 License

MIT License
