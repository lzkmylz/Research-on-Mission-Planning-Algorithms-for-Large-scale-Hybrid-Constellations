# 大规模成像星座任务规划框架

## 项目概述

卫星任务规划论文研究的仿真与算法测试框架。

## 核心功能

| 模块 | 功能 | 状态 |
|------|------|------|
| `models/` | 卫星、传感器、目标（点/网格/动态/区域）、地面站 | ✅ |
| `models/satellite_type.py` | 卫星型号配置（转换时间、能源、存储、机动能力） | ✅ |
| `models/imaging_mode.py` | 成像模式配置（数据速率、压缩比、功耗） | ✅ |
| `models/antenna.py` | 天线模型（独立可用时间段、数传速率） | ✅ |
| `models/ttc_station.py` | 测控数传站（多天线、上注能力） | ✅ |
| `models/uplink.py` | 上注/数传动作模型（分段传输、数传计划） | ✅ |
| `stk/` | STK 接口层（Mock + STK10 COM） | ✅ |
| `decomposition/` | 区域分解策略（网格） | ✅ |
| `constraints/` | 约束检查（云层/可见性/存储/能源/下传） | ✅ |
| `constraints/transition.py` | 动作转换时间约束（成像-成像/成像-数传/数传站切换） | ✅ |
| `constraints/antenna_resource.py` | 天线资源互斥约束 | ✅ |
| `constraints/uplink_precedence.py` | 上注前置约束 | ✅ |
| `scheduling/ttc_scheduler.py` | 基础测控数传调度器 | ✅ |
| `scheduling/advanced_downlink.py` | 高级数传调度器（多天线聚合、分段传输） | ✅ |
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

## 基准测试数据集

**状态**: ✅ 已完成 (v1.0-baseline)

**文档**: [benchmark_dataset/README.md](benchmark_dataset/README.md)
**设计**: [docs/plans/2026-02-07-benchmark-dataset-design.md](docs/plans/2026-02-07-benchmark-dataset-design.md)
**移植**: [docs/plans/2026-02-07-matlab-porting-plan.md](docs/plans/2026-02-07-matlab-porting-plan.md)

**快速开始**:
```bash
# 运行基准测试
python3 -m constellation_planning.benchmark.run_benchmark --run-all

# 查看结果
open benchmark_dataset/evaluation/test_scenario_radar.png
```

**评估结果**:
- 包含4个场景（全球均匀、亚太热点、多热点、混合）
- 包含4种算法（GA, Tabu, SA, ACO）
- 生成CSV报告和可视化图表 (见 `benchmark_dataset/evaluation/`)

### 星座配置（200颗混合星座）

| 类型 | 数量 | 分辨率 | 成像模式 |
|------|------|--------|----------|
| 超高分辨率光学 | 10 | 0.5m | strip/stare/area |
| 高分辨率光学 | 90 | 2m | strip/stare/area |
| 超高分辨率SAR | 10 | 1m | spotlight/stripmap/sliding_spotlight/scanSAR |
| 高分辨率SAR | 90 | 5m | spotlight/stripmap/sliding_spotlight/scanSAR |

### 测试场景（4个，各1000点目标，24h窗口）

1. **全球均匀分布** - 基准性能测试
2. **亚太热点** - 中国东部35% + 东南亚20% + 日韩15% + 印度及南亚30%
3. **多热点** - 五大洲热点区域
4. **混合分布** - 沿海聚集 + 内陆城市

### 评估指标（6项）

- 任务完成率
- 运行时间
- 总收益
- 资源利用率
- 重访次数分布
- 完成观测时间

### 使用方法

```python
# 生成数据集
python -m constellation_planning.benchmark.run_benchmark --generate

# 运行基准测试
python -m constellation_planning.benchmark.run_benchmark --run-all

# 查看对比结果
python -m constellation_planning.benchmark.evaluation.visualizer
```

## 详细计划

参见 `.gemini/antigravity/brain/*/implementation_plan.md`
