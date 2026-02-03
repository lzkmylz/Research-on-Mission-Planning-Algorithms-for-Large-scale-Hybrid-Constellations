# 大规模成像星座任务规划框架

## 项目概述

卫星任务规划论文研究的仿真与算法测试框架。

## 核心功能

| 模块 | 功能 | 状态 |
|------|------|------|
| `models/` | 卫星、传感器、目标（点/网格/动态/区域）、地面站 | ✅ |
| `stk/` | STK 接口层（Mock + STK10 COM） | ✅ |
| `decomposition/` | 区域分解策略（网格） | ✅ |
| `constraints/` | 约束检查（云层/可见性/存储/能源/下传） | ✅ |
| `algorithms/` | 禁忌搜索、模拟退火、遗传算法、蚁群算法 | ✅ |
| `objectives/` | 优化目标函数 | 🚧 |
| `evaluation/` | 性能评估与可视化 | 🚧 |

## 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 创建星座
from constellation_planning.stk import MockSTKConnector, WalkerConstellationBuilder

builder = WalkerConstellationBuilder(
    name="TestConstellation",
    altitude_km=500,
    inclination_deg=97.4,
    num_planes=6,
    sats_per_plane=10
)
satellites = builder.build()  # 60颗卫星
```

## 目标类型

- **点目标**: `PointTarget(id, name, lat, lon, priority)`
- **网格目标**: `GridTarget(id, name, center_lat, center_lon, size_deg=0.1)`
- **动态目标**: `MovingTarget.create_vehicle(...)` / `MovingTarget.create_ship(...)`
- **区域目标**: `AreaTarget(id, name, polygon=[(lat,lon),...])`

## 算法使用

```python
from constellation_planning.algorithms import GeneticAlgorithm, AlgorithmConfig

config = AlgorithmConfig(max_iterations=500, random_seed=42)
ga = GeneticAlgorithm(config, population_size=50)
solution = ga.solve(observations, satellites)
```

## 开发说明

- **Mac 开发**: 使用 `MockSTKConnector` 进行算法开发
- **Windows 部署**: 切换到 `STK10Connector` 进行真实仿真
- **云层约束**: 手动设置多边形区域，无需外部数据源

## 详细计划

参见 `.gemini/antigravity/brain/*/implementation_plan.md`
