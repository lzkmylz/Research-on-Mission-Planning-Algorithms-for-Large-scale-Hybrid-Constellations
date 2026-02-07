# 标准测试数据集设计方案

> **创建时间**: 2026-02-07  
> **作者**: 赵林  
> **目的**: 为大规模混合星座任务规划算法研究建立标准基准测试数据集

## 一、设计目标

本数据集旨在提供一个全面的、可复现的基准测试环境，用于：

1. **算法性能对比** - 在相同输入条件下对比不同算法的性能
2. **论文实验验证** - 为职称论文提供可信的实验数据和结果
3. **标准基准测试** - 建立可持续使用的benchmark，便于未来研究复用

## 二、总体架构

### 2.1 目录结构

```
benchmark_dataset/
├── constellation/                       # 星座与任务输入数据
│   ├── satellites/
│   │   ├── satellite_templates.json    # 四种型号卫星模板
│   │   └── constellation_200.json      # 200颗卫星实例配置
│   ├── ground_stations/
│   │   └── stations_global.json        # 全球地面站配置
│   └── targets/                         # 目标任务配置
│       ├── global_uniform_1000.json    # 场景1：全球均匀分布
│       ├── hotspot_asia_1000.json      # 场景2：亚太热点
│       ├── hotspot_multi_1000.json     # 场景3：多热点区域
│       └── mixed_1000.json             # 场景4：混合分布
│
├── scenarios/                           # 按算法组织的实验结果
│   ├── genetic_algorithm/              # 遗传算法
│   │   ├── global_uniform/
│   │   │   └── result.json
│   │   ├── hotspot_asia/
│   │   ├── hotspot_multi/
│   │   └── mixed/
│   ├── tabu_search/                    # 禁忌搜索
│   ├── simulated_annealing/            # 模拟退火
│   └── ant_colony/                     # 蚁群算法
│
└── evaluation/                          # 评估工具与脚本
    ├── metrics.py                      # 评估指标计算
    ├── comparator.py                   # 算法对比工具
    └── visualizer.py                   # 结果可视化
```

### 2.2 设计理念

- **可复现性**: 所有随机生成使用固定种子（seed=42）
- **真实性**: 基于真实卫星系统的轨道参数和传感器特性
- **可扩展性**: 易于添加新场景、新算法和新评估指标
- **标准化**: 统一的JSON数据格式，便于算法读取和结果比对

## 三、星座配置详细设计

### 3.1 混合星座总体配置

**总规模**: 200颗卫星（分层型配置）

| 卫星类型 | 数量 | 定位 | 主要应用 |
|---------|------|------|----------|
| 超高分辨率光学 | 10 | 少而精 | 关键目标精细成像 |
| 高分辨率光学 | 90 | 主力 | 常规观测任务 |
| 超高分辨率SAR | 10 | 少而精 | 全天候精细观测 |
| 高分辨率SAR | 90 | 主力 | 全天候常规观测 |

### 3.2 卫星型号详细参数

#### 型号1：超高分辨率光学卫星

**参考型号**: WorldView-3、高景一号

```json
{
  "type": "ultra_high_res_optical",
  "count": 10,
  "specs": {
    "resolution_m": 0.5,
    "swath_width_km": 12,
    "altitude_km": 530,
    "inclination_deg": 97.4,
    "eccentricity": 0.001,
    
    "imaging_modes": ["strip", "stare", "area"],
    
    "agility": {
      "roll_range_deg": [-30, 30],
      "pitch_range_deg": [-15, 15],
      "yaw_range_deg": [-5, 5],
      "maneuver_time_sec": 8,
      "settling_time_sec": 4,
      "max_slew_rate_deg_per_sec": 3.0
    },
    
    "constraints": {
      "min_elevation_deg": 20,
      "max_sun_angle_deg": 70,
      "max_cloud_cover": 0.3,
      "min_sun_elevation_deg": 10
    },
    
    "storage_capacity_gb": 256,
    "downlink_rate_mbps": 300,
    "power_capacity_wh": 1200
  }
}
```

#### 型号2：高分辨率光学卫星（主力）

**参考型号**: Sentinel-2、资源三号

```json
{
  "type": "high_res_optical",
  "count": 90,
  "specs": {
    "resolution_m": 2.0,
    "swath_width_km": 40,
    "altitude_km": 645,
    "inclination_deg": 98.0,
    
    "imaging_modes": ["strip", "stare", "area"],
    
    "agility": {
      "roll_range_deg": [-25, 25],
      "pitch_range_deg": [-10, 10],
      "maneuver_time_sec": 12,
      "settling_time_sec": 5
    },
    
    "constraints": {
      "min_elevation_deg": 15,
      "max_cloud_cover": 0.4
    },
    
    "storage_capacity_gb": 128,
    "downlink_rate_mbps": 150
  }
}
```

#### 型号3：超高分辨率SAR卫星

**参考型号**: TerraSAR-X、高分三号精细模式

```json
{
  "type": "ultra_high_res_sar",
  "count": 10,
  "specs": {
    "resolution_m": 1.0,
    "swath_width_km": 10,
    "altitude_km": 514,
    "inclination_deg": 97.44,
    
    "imaging_modes": [
      "spotlight",           // 聚束模式（最高分辨率）
      "stripmap",           // 条带模式
      "sliding_spotlight",  // 滑动聚束
      "scanSAR"            // 扫描模式
    ],
    
    "mode_parameters": {
      "spotlight": {
        "resolution_m": 1.0,
        "swath_width_km": 5
      },
      "stripmap": {
        "resolution_m": 3.0,
        "swath_width_km": 10
      },
      "sliding_spotlight": {
        "resolution_m": 2.0,
        "swath_width_km": 8
      },
      "scanSAR": {
        "resolution_m": 10.0,
        "swath_width_km": 100
      }
    },
    
    "agility": {
      "roll_range_deg": [-35, 35],
      "maneuver_time_sec": 10
    },
    
    "constraints": {
      "min_elevation_deg": 15,
      "no_cloud_constraint": true
    },
    
    "storage_capacity_gb": 384,
    "downlink_rate_mbps": 600
  }
}
```

#### 型号4：高分辨率SAR卫星（主力）

**参考型号**: Sentinel-1、ALOS-2

```json
{
  "type": "high_res_sar",
  "count": 90,
  "specs": {
    "resolution_m": 5.0,
    "swath_width_km": 80,
    "altitude_km": 693,
    "inclination_deg": 98.18,
    
    "imaging_modes": [
      "spotlight",
      "stripmap",
      "sliding_spotlight",
      "scanSAR"
    ],
    
    "mode_parameters": {
      "spotlight": {
        "resolution_m": 3.0,
        "swath_width_km": 10
      },
      "stripmap": {
        "resolution_m": 5.0,
        "swath_width_km": 80
      },
      "sliding_spotlight": {
        "resolution_m": 4.0,
        "swath_width_km": 40
      },
      "scanSAR": {
        "resolution_m": 20.0,
        "swath_width_km": 250
      }
    },
    
    "agility": {
      "roll_range_deg": [-30, 30],
      "maneuver_time_sec": 15
    },
    
    "storage_capacity_gb": 256,
    "downlink_rate_mbps": 300
  }
}
```

### 3.3 轨道配置策略

采用**Walker Delta星座**配置，确保全球覆盖：

```
总卫星数: 200
轨道平面数: 10
每平面卫星数: 20
相位因子: 1
```

不同型号卫星在轨道平面内均匀分布，形成异构混合星座。

### 3.4 地面站配置

全球布设**8个**地面站，确保数据下传：

| 地面站 | 位置 | 覆盖区域 |
|--------|------|----------|
| 北京站 | 40.0°N, 116.4°E | 东亚 |
| 墨尔本站 | 37.8°S, 144.9°E | 大洋洲 |
| 斯瓦尔巴站 | 78.2°N, 15.6°E | 北极 |
| 阿拉斯加站 | 64.8°N, 147.7°W | 北美北部 |
| 迈阿密站 | 25.8°N, 80.2°W | 北美南部 |
| 马德里站 | 40.4°N, 3.7°W | 欧洲 |
| 圣地亚哥站 | 33.3°S, 70.7°W | 南美 |
| 开普敦站 | 33.9°S, 18.4°E | 非洲 |

## 四、测试场景设计

### 4.1 场景概览

所有场景均包含**1000个点目标**，规划窗口为**24小时**。

| 场景ID | 名称 | 目标分布特征 | 研究意义 |
|--------|------|-------------|----------|
| 场景1 | 全球均匀分布 | 均匀随机分布 | 基准性能测试 |
| 场景2 | 亚太热点 | 80%集中亚太，20%全球 | 区域热点应对 |
| 场景3 | 多热点 | 五大洲热点 | 多区域协同 |
| 场景4 | 混合分布 | 沿海+内陆混合 | 复杂场景适应 |

### 4.2 场景详细设计

#### 场景1：全球均匀分布

**文件名**: `global_uniform_1000.json`

**生成策略**:
```python
参数设置:
- 总目标数: 1000
- 纬度范围: -60° 到 +60° (避免极地)
- 经度范围: -180° 到 +180°
- 分布方式: 均匀随机
- 优先级分配: 随机（1-5级，均匀分布）
- 时间窗口: 24小时内任意时刻
- 随机种子: 42
```

**应用场景**: 全球常规观测任务，无明显热点区域

#### 场景2：亚太热点

**文件名**: `hotspot_asia_1000.json`

**生成策略**:
```python
热点区域 (800个目标):
- 中国东部 (35%): 280个
  经度: 110°E - 125°E
  纬度: 20°N - 45°N
  
- 东南亚 (20%): 160个
  经度: 95°E - 115°E
  纬度: 0° - 20°N
  
- 日韩 (15%): 120个
  经度: 125°E - 140°E
  纬度: 30°N - 45°N
  
- 印度及南亚 (30%): 240个
  经度: 68°E - 95°E
  纬度: 8°N - 35°N

全球分散 (200个目标):
- 其他区域均匀分布

优先级分配:
- 热点区域: 平均优先级3-5（较高）
- 分散区域: 平均优先级1-3（较低）
```

**应用场景**: 亚太地区重点监测，模拟区域应急响应

#### 场景3：多热点区域

**文件名**: `hotspot_multi_1000.json`

**生成策略**:
```python
五大热点区域 (各150个目标):

1. 亚太热点 (150):
   - 中国+日韩
   经度: 110°E - 140°E
   纬度: 20°N - 45°N

2. 欧洲热点 (150):
   经度: 10°W - 30°E
   纬度: 40°N - 60°N

3. 北美热点 (150):
   经度: 130°W - 70°W
   纬度: 25°N - 50°N

4. 中东热点 (150):
   经度: 30°E - 60°E
   纬度: 15°N - 40°N

5. 南美热点 (150):
   - 巴西+阿根廷
   经度: 75°W - 35°W
   纬度: 35°S - 5°N

全球分散 (250个目标):
- 其他区域均匀分布
```

**应用场景**: 全球多区域协同观测，考验算法的全局优化能力

#### 场景4：混合分布

**文件名**: `mixed_1000.json`

**生成策略**:
```python
沿海区域聚集 (500个):
- 全球主要海岸线±200km范围内
- 重点: 中国沿海、美国东西海岸、欧洲沿海、日本

内陆城市 (300个):
- 主要内陆大城市及周边
- 如: 莫斯科、德里、芝加哥等

随机分布 (200个):
- 全球其他区域随机分布
```

**应用场景**: 海洋监测+陆地观测混合任务

### 4.3 目标属性配置

每个点目标包含以下属性：

```json
{
  "id": "TGT_001",
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
    "max_cloud_cover": 0.3,
    "preferred_imaging_mode": "strip"
  }
}
```

## 五、评估指标体系

### 5.1 核心指标定义

#### 1. 任务完成率 (Task Completion Rate)

$$
TCR = \frac{N_{observed}}{N_{total}}
$$

其中：
- $N_{observed}$: 成功观测的目标数量
- $N_{total}$: 总目标数量（1000）

**目标**: 越高越好，理想值接近1.0

---

#### 2. 运行时间 (Runtime)

算法从开始执行到收敛或达到最大迭代次数的wall clock时间（秒）。

**目标**: 越短越好

---

#### 3. 总收益 (Total Value)

$$
V_{total} = \sum_{i=1}^{N_{obs}} V_i
$$

其中每个观测的价值 $V_i$ 由以下因素决定：

```python
V_i = w_p * Priority_i + 
      w_e * f_elevation(θ_i) + 
      w_r * f_resolution(r_i) +
      w_t * f_timeliness(t_i)
```

参数说明：
- $w_p, w_e, w_r, w_t$: 权重系数（建议: 0.4, 0.2, 0.2, 0.2）
- $Priority_i$: 目标优先级（1-5）
- $f_{elevation}$: 仰角质量函数（仰角越大质量越高）
- $f_{resolution}$: 分辨率质量函数
- $f_{timeliness}$: 时效性函数（越早完成越好）

**目标**: 越高越好

---

#### 4. 资源利用率 (Resource Utilization)

**4.1 存储利用率**:
$$
U_{storage} = \frac{1}{N_{sat}} \sum_{s=1}^{N_{sat}} \frac{Storage\_Used_s}{Storage\_Capacity_s}
$$

**4.2 能源利用率**:
$$
U_{energy} = \frac{1}{N_{sat}} \sum_{s=1}^{N_{sat}} \frac{Energy\_Used_s}{Energy\_Capacity_s}
$$

**目标**: 合理利用（0.6-0.8为佳，过低浪费资源，过高可能导致资源冲突）

---

#### 5. 重访次数分布 (Revisit Distribution)

统计每个目标被观测的次数，输出分布：

```json
{
  "0_times": 144,    // 未观测目标数
  "1_time": 520,     // 观测1次的目标数
  "2_times": 280,    // 观测2次的目标数
  "3+_times": 56     // 观测3次及以上的目标数
}
```

**分析意义**:
- 0次过多 → 完成率低
- 多次重访 → 可能资源分配不均

---

#### 6. 完成观测用时 (Completion Time)

从规划开始到最后一个目标被观测的时间跨度（小时）。

$$
T_{completion} = t_{last\_observation} - t_{start}
$$

**目标**: 越短越好（对紧急任务尤其重要）

### 5.2 算法结果输出格式

```json
{
  "metadata": {
    "algorithm": "genetic_algorithm",
    "scenario": "global_uniform",
    "timestamp": "2024-06-01T10:30:00Z",
    "config": {
      "population_size": 50,
      "max_iterations": 500,
      "crossover_rate": 0.8,
      "mutation_rate": 0.1,
      "random_seed": 42
    }
  },
  
  "execution": {
    "runtime_seconds": 125.3,
    "iterations_completed": 500,
    "convergence_achieved": true,
    "convergence_curve": [100.5, 150.2, ... , 1245.8]
  },
  
  "solution": {
    "observations": [
      {
        "target_id": "TGT_001",
        "satellite_id": "SAT_HR_OPT_045",
        "observation_time": "2024-06-01T03:25:30Z",
        "imaging_mode": "strip",
        "elevation_deg": 45.2,
        "azimuth_deg": 180.5,
        "sun_angle_deg": 35.0,
        "cloud_cover": 0.15,
        "value": 85.5
      }
      // ... 其他观测任务
    ]
  },
  
  "metrics": {
    "task_completion_rate": 0.856,
    "total_value": 12450.8,
    "targets_covered": 856,
    "targets_total": 1000,
    
    "resource_utilization": {
      "avg_storage_usage": 0.68,
      "max_storage_usage": 0.92,
      "avg_energy_usage": 0.72,
      "max_energy_usage": 0.95
    },
    
    "revisit_distribution": {
      "0_times": 144,
      "1_time": 520,
      "2_times": 280,
      "3+_times": 56
    },
    
    "completion_time_hours": 18.5,
    
    "detailed_breakdown": {
      "ultra_high_res_optical": {
        "observations": 125,
        "avg_value": 95.2
      },
      "high_res_optical": {
        "observations": 580,
        "avg_value": 72.3
      },
      "ultra_high_res_sar": {
        "observations": 48,
        "avg_value": 88.5
      },
      "high_res_sar": {
        "observations": 103,
        "avg_value": 65.8
      }
    }
  }
}
```

## 六、数据生成与管理

### 6.1 数据生成工具

需要开发以下Python工具：

**1. 星座生成器** (`constellation_generator.py`):
```python
class ConstellationGenerator:
    def generate_walker_constellation(
        total_sats: int,
        num_planes: int,
        altitude_km: float,
        inclination_deg: float
    ) -> List[Satellite]
    
    def assign_satellite_types(
        satellites: List[Satellite],
        type_distribution: Dict[str, int]
    ) -> List[Satellite]
```

**2. 目标生成器** (`target_generator.py`):
```python
class TargetGenerator:
    def generate_uniform(
        num_targets: int,
        lat_range: Tuple[float, float],
        lon_range: Tuple[float, float],
        seed: int = 42
    ) -> List[Target]
    
    def generate_hotspot(
        hotspot_regions: List[HotspotConfig],
        num_scattered: int,
        seed: int = 42
    ) -> List[Target]
```

**3. 评估计算器** (`metrics_calculator.py`):
```python
class MetricsCalculator:
    def calculate_all_metrics(
        solution: Solution,
        targets: List[Target],
        satellites: List[Satellite]
    ) -> Dict[str, Any]
```

### 6.2 版本控制与分发

- 所有配置文件使用Git进行版本控制
- 数据集版本标签: `v1.0-baseline`
- 未来更新使用语义化版本号（如v1.1, v2.0等）
- 大文件（>100MB）使用Git LFS管理

## 七、使用流程

### 7.1 算法集成流程

```python
# 1. 加载数据集
from benchmark_dataset import load_constellation, load_targets

constellation = load_constellation("constellation/satellites/constellation_200.json")
targets = load_targets("constellation/targets/global_uniform_1000.json")
ground_stations = load_ground_stations("constellation/ground_stations/stations_global.json")

# 2. 运行算法
from constellation_planning.algorithms import GeneticAlgorithm, AlgorithmConfig

config = AlgorithmConfig(
    max_iterations=500,
    random_seed=42
)
ga = GeneticAlgorithm(config, population_size=50)
solution = ga.solve(targets, constellation, ground_stations)

# 3. 计算评估指标
from benchmark_dataset.evaluation import MetricsCalculator

calculator = MetricsCalculator()
metrics = calculator.calculate_all_metrics(solution, targets, constellation)

# 4. 保存结果
save_result(
    solution,
    metrics,
    output_path="scenarios/genetic_algorithm/global_uniform/result.json"
)
```

### 7.2 对比分析流程

```python
from benchmark_dataset.evaluation import AlgorithmComparator, Visualizer

# 加载所有算法结果
results = {
    "GA": load_result("scenarios/genetic_algorithm/global_uniform/result.json"),
    "TS": load_result("scenarios/tabu_search/global_uniform/result.json"),
    "SA": load_result("scenarios/simulated_annealing/global_uniform/result.json"),
    "ACO": load_result("scenarios/ant_colony/global_uniform/result.json")
}

# 对比分析
comparator = AlgorithmComparator()
comparison_report = comparator.compare(results)

# 可视化
visualizer = Visualizer()
visualizer.plot_comparison_table(comparison_report)
visualizer.plot_convergence_curves(results)
visualizer.plot_radar_chart(results)
```

## 八、验证与质量保证

### 8.1 数据有效性检查

- [ ] 所有卫星轨道参数符合物理约束
- [ ] 目标坐标在有效范围内（-90° ≤ lat ≤ 90°, -180° ≤ lon ≤ 180°）
- [ ] 时间窗口合法（开始时间 < 结束时间）
- [ ] 地面站位置合理
- [ ] JSON格式正确性验证

### 8.2 可复现性验证

- [ ] 使用相同随机种子生成相同数据
- [ ] 算法运行相同配置得到相同结果（确定性算法）
- [ ] 随机算法多次运行的统计特性一致

### 8.3 合理性验证

- [ ] 不同场景的难度梯度合理
- [ ] 评估指标计算正确
- [ ] 可视化结果符合预期

## 九、未来扩展方向

### 9.1 目标类型扩展

- 网格目标（Grid Target）
- 动态目标（Moving Target）
- 区域目标（Area Target）

### 9.2 场景扩展

- 应急响应场景（灾害发生后的紧急观测）
- 长期规划场景（7-14天）
- 实时重规划场景（在线算法测试）

### 9.3 评估指标扩展

- 算法稳定性分析（多次运行的方差）
- Pareto前沿分析（多目标优化）
- 公平性指标（优先级分配公平性）

## 十、参考文献

1. Bianchessi, N., et al. (2007). "A heuristic for the multi-satellite, multi-orbit and multi-user management of Earth observation satellites." *European Journal of Operational Research*.

2. Wolfe, W. J., & Sorensen, S. E. (2000). "Three scheduling algorithms applied to the earth observing systems domain." *Management Science*.

3. Lemaître, M., et al. (2002). "Selecting and scheduling observations of agile satellites." *Aerospace Science and Technology*.

4. Wu, G., et al. (2013). "A two-phase scheduling method with the consideration of task clustering for earth observing satellites." *Computers & Operations Research*.

---

**文档状态**: 设计完成，待审核批准  
**下一步**: 创建详细实施计划
