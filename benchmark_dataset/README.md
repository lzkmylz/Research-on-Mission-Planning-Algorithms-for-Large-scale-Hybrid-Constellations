# 基准测试数据集

> **版本**: v1.0-baseline  
> **创建日期**: 2026-02-07  
> **用途**: 大规模混合星座任务规划算法性能评估

## 数据集概述

本数据集为卫星任务规划算法研究提供标准的测试环境，包含：

- **星座**: 200颗混合星座（分层型：少量超高分辨率+主力高分辨率，光学+SAR）
- **测试场景**: 4个场景，各1000个点目标，24小时规划窗口
- **地面站**: 8个全球分布的地面站
- **评估指标**: 6项性能指标

## 快速开始

### 1. 生成数据

虽然仓库中已包含生成好的 JSON 数据，但你可以随时重新生成：

```bash
python3 -m constellation_planning.benchmark.run_benchmark --generate
```

这将在 `benchmark_dataset/constellation/` 下生成星座、目标和地面站文件。

### 2. 运行基准测试

运行所有算法在所有场景下的测试：

```bash
python3 -m constellation_planning.benchmark.run_benchmark --run-all
```

**注意**: 默认脚本为了演示速度，限制了可见性计算的规模（仅计算前10颗卫星和前50个目标）。如需全量运行，请修改 `constellation_planning/benchmark/run_benchmark.py` 中的 `compute_access_opportunities` 方法，移除切片限制。

### 3. 查看结果

测试完成后，结果将保存在 `benchmark_dataset/evaluation/` 目录下，包含：

- **CSV 报告**: `*_comparison_report.csv` - 包含各算法的详细指标对比。
- **图表**: 
  - `*_radar.png` - 综合性能雷达图
  - `*_completion_rate.png` - 完成率对比柱状图
  - `*_runtime.png` - 运行时间对比
  - `*_total_value.png` - 总收益对比

## 目录结构

```
benchmark_dataset/
├── constellation/                       # 输入数据
│   ├── satellites/
│   │   ├── satellite_templates.json
│   │   └── constellation_200.json
│   ├── ground_stations/
│   │   └── stations_global.json
│   └── targets/
│       ├── global_uniform_1000.json
│       ├── hotspot_asia_1000.json     
│       ├── hotspot_multi_1000.json
│       └── mixed_1000.json
│
├── scenarios/                           # 算法详细运行结果 (JSON)
│   ├── GeneticAlgorithm/
│   ├── TabuSearch/
│   ├── SimulatedAnnealing/
│   └── AntColony/
│
├── evaluation/                          # 评估报告与图表
│   ├── global_uniform_comparison_report.csv
│   ├── global_uniform_radar.png
│   ├── ...
│
└── README.md                            # 本文档
```

## 星座配置

| 类型 | 数量 | 分辨率 | 幅宽 | 轨道高度 | 成像模式 |
|------|------|--------|------|----------|----------|
| 超高分辨率光学 | 10 | 0.5m | 12km | 530km | strip/stare/area |
| 高分辨率光学 | 90 | 2m | 40km | 645km | strip/stare/area |
| 超高分辨率SAR | 10 | 1m | 10km | 514km | spotlight/stripmap/sliding_spotlight/scanSAR |
| 高分辨率SAR | 90 | 5m | 80km | 693km | spotlight/stripmap/sliding_spotlight/scanSAR |

**星座配置**: Walker Delta (200/10/1)

## 测试场景

1. **全球均匀分布**: 基准性能测试，目标均匀分布全球。
2. **亚太热点**: 区域密集观测场景，80%目标集中在亚太地区。
3. **多热点**: 全球协同观测，目标集中在五大洲热点区域。
4. **混合分布**: 复杂任务场景，包含沿海、内陆城市和随机分布目标。

## 评估指标

1. **任务完成率** (Task Completion Rate)
2. **运行时间** (Runtime)
3. **总收益** (Total Value)
4. **资源利用率** (Resource Utilization)
5. **重访次数分布** (Revisit Distribution)
6. **完成观测时间** (Completion Time)

## 扩展指南

### 添加新算法

1. 在 `constellation_planning/algorithms/` 下实现你的算法类，继承自 `PlanningAlgorithm`。
2. 在 `constellation_planning/benchmark/run_benchmark.py` 中导入你的算法类。
3. 将算法类添加到 `run_all` 方法中的 `algorithms` 列表中：

```python
algorithms = [
    ("YourAlgorithm", YourAlgorithmClass),
    ...
]
```

### 调整数据规模

修改 `constellation_planning/benchmark/target_generator.py` 中的 `generate_scenario` 参数可调整目标数量。
修改 `constellation_planning/benchmark/constellation_generator.py` 可调整星座规模。

## 引用

如在研究中使用本数据集，请引用:

```
赵林. 大规模混合星座任务规划基准测试数据集 v1.0. 2026.
```
