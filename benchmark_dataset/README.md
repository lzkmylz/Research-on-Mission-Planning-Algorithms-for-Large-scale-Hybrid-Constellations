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

## 目录结构

```
benchmark_dataset/
├── constellation/                       # 输入数据（星座、目标、地面站）
│   ├── satellites/
│   │   ├── satellite_templates.json    # 四种卫星型号模板
│   │   └── constellation_200.json      # 200颗卫星配置
│   ├── ground_stations/
│   │   └── stations_global.json        # 8个全球地面站
│   └── targets/
│       ├── global_uniform_1000.json    # 场景1：全球均匀分布
│       ├── hotspot_asia_1000.json      # 场景2：亚太热点
│       ├── hotspot_multi_1000.json     # 场景3：多热点区域
│       └── mixed_1000.json             # 场景4：混合分布
│
├── scenarios/                           # 算法结果（待生成）
│   ├── genetic_algorithm/
│   ├── tabu_search/
│   ├── simulated_annealing/
│   └── ant_colony/
│
└── README.md                            # 本文档
```

## 星座配置

### 卫星型号（4种）

| 类型 | 数量 | 分辨率 | 幅宽 | 轨道高度 | 成像模式 |
|------|------|--------|------|----------|----------|
| 超高分辨率光学 | 10 | 0.5m | 12km | 530km | strip/stare/area |
| 高分辨率光学 | 90 | 2m | 40km | 645km | strip/stare/area |
| 超高分辨率SAR | 10 | 1m | 10km | 514km | spotlight/stripmap/sliding_spotlight/scanSAR |
| 高分辨率SAR | 90 | 5m | 80km | 693km | spotlight/stripmap/sliding_spotlight/scanSAR |

**星座配置**: Walker Delta (200/10/1)
- 总卫星数: 200
- 轨道平面数: 10
- 每平面卫星数: 20
- 相位因子: 1

### 地面站（8个）

| 站点 | 位置 | 覆盖区域 |
|------|------|----------|
| Beijing Station | 40.0°N, 116.4°E | 东亚 |
| Melbourne Station | 37.8°S, 144.9°E | 大洋洲 |
| Svalbard Station | 78.2°N, 15.6°E | 北极 |
| Alaska Station | 64.8°N, 147.7°W | 北美北部 |
| Miami Station | 25.8°N, 80.2°W | 北美南部 |
| Madrid Station | 40.4°N, 3.7°W | 欧洲 |
| Santiago Station | 33.3°S, 70.7°W | 南美 |
| Cape Town Station | 33.9°S, 18.4°E | 非洲 |

## 测试场景

### 场景1: 全球均匀分布
- **文件**: `targets/global_uniform_1000.json`
- **目标数**: 1000个点目标
- **分布**: 纬度-60°至+60°均匀随机
- **优先级**: 1-5级均匀分布
- **用途**: 基准性能测试

### 场景2: 亚太热点
- **文件**: `targets/hotspot_asia_1000.json`
- **目标数**: 1000个点目标
- **分布**:
  - 热点区域（800个）：中国东部35% + 东南亚20% + 日韩15% + 印度及南亚30%
  - 全球分散（200个）
- **优先级**: 热点区域3-5级（较高），分散区域1-3级（较低）
- **用途**: 区域密集观测场景

### 场景3: 多热点
- **文件**: `targets/hotspot_multi_1000.json`
- **目标数**: 1000个点目标
- **分布**:
  - 五大热点（各150个）：亚太、欧洲、北美、中东、南美
  - 全球分散（250个）
- **用途**: 全球多区域协同观测

### 场景4: 混合分布
- **文件**: `targets/mixed_1000.json`
- **目标数**: 1000个点目标
- **分布**:
  - 沿海区域（500个）：全球主要海岸线±200km
  - 内陆城市（300个）：主要内陆大城市周边
  - 随机分布（200个）
- **用途**: 海洋监测+陆地观测混合任务

## 数据生成

所有配置数据通过以下工具生成：

```bash
# 生成星座配置
python3 -m constellation_planning.benchmark.constellation_generator

# 生成目标配置
python3 -m constellation_planning.benchmark.target_generator

# 生成地面站配置
python3 -m constellation_planning.benchmark.ground_station_generator
```

**重要**: 所有随机生成使用固定种子（seed=42），确保可复现性。

## 数据格式

### 卫星配置格式

```json
{
  "id": "SAT_ULTRA_HI_001",
  "type": "ultra_high_res_optical",
  "orbital_elements": {
    "semi_major_axis_km": 6908.137,
    "eccentricity": 0.001,
    "inclination_deg": 97.4,
    "raan_deg": 0.0,
    "argument_of_perigee_deg": 0.0,
    "true_anomaly_deg": 0.0,
    "epoch": "2024-06-01T00:00:00Z"
  },
  "sensor": {
    "resolution_m": 0.5,
    "swath_width_km": 12,
    "imaging_modes": ["strip", "stare", "area"],
    "agility": {...},
    "constraints": {...}
  },
  "resources": {
    "storage_capacity_gb": 256,
    "downlink_rate_mbps": 300,
    "power_capacity_wh": 1200
  }
}
```

### 目标配置格式

```json
{
  "id": "TGT_0001",
  "type": "point",
  "latitude": 39.9042,
  "longitude": 116.4074,
  "priority": 4,
  "time_window": {
    "start": "2024-06-01T00:00:00Z",
    "end": "2024-06-02T00:00:00Z"
  },
  "observation_requirements": {
    "min_resolution_m": 5.0,
    "min_elevation_deg": 15,
    "max_cloud_cover": 0.3
  }
}
```

## 评估指标

运行算法后，将计算以下6项指标：

1. **任务完成率** (Task Completion Rate)
   - 公式: 成功观测目标数 / 总目标数
   - 目标: 越高越好

2. **运行时间** (Runtime)
   - 单位: 秒
   - 目标: 越短越好

3. **总收益** (Total Value)
   - 综合考虑：优先级 + 仰角质量 + 分辨率 + 时效性
   - 目标: 越高越好

4. **资源利用率** (Resource Utilization)
   - 存储利用率、能源利用率
   - 目标: 0.6-0.8为佳

5. **重访次数分布** (Revisit Distribution)
   - 统计每个目标被观测的次数（0次、1次、2次、3+次）
   - 分析: 资源分配均衡性

6. **完成观测时间** (Completion Time)
   - 单位: 小时
   - 最后一个目标被观测的时刻 - 开始时刻
   - 目标: 越短越好

## 下一步工作

- [ ] 开发评估指标计算模块
- [ ] 开发算法对比工具
- [ ] 开发结果可视化工具
- [ ] 运行基准测试（4种算法 × 4个场景）
- [ ] 生成性能对比报告

## 引用

如在研究中使用本数据集，请引用:

```
赵林. 大规模混合星座任务规划基准测试数据集 v1.0. 2026.
```

## 更多信息

- **设计文档**: [docs/plans/2026-02-07-benchmark-dataset-design.md](../docs/plans/2026-02-07-benchmark-dataset-design.md)
- **实施计划**: 见项目artifacts目录
- **代码**: `constellation_planning/benchmark/`

---

**版本历史**:
- v1.0-baseline (2026-02-07): 初始版本，包含200颗星座、4个场景、8个地面站
