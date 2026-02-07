# MATLAB 版本移植规划

## 目标
将现有的 Python 星座任务规划框架完整移植到 MATLAB 平台，保持架构一致性，并复用已生成的基准测试数据。

## 目录结构映射

| Python 模块 | MATLAB 目录 (`matlab_version/`) | 说明 |
|-------------|---------------------------------|------|
| `constellation_planning/models` | `+models/` | 核心数据模型 (Satellite, Sensor, Target) |
| `constellation_planning/algorithms` | `+algorithms/` | 优化算法 (GA, TS, SA, ACO) |
| `constellation_planning/stk` | `+stk/` | STK 接口 (Mock & COM) |
| `constellation_planning/constraints` | `+constraints/` | 约束检查 (Energy, Storage, Visibility) |
| `constellation_planning/evaluation` | `+evaluation/` | 评估指标计算 |
| `constellation_planning/utils` | `+utils/` | 工具函数 (JSON读取, 几何计算) |
| `benchmark_dataset/` | (复用根目录数据) | 直接从 MATLAB 读取 JSON 数据 |

> **注意**: MATLAB 包文件夹以 `+` 开头，便于命名空间管理。

## 核心组件移植策略

### 1. 数据模型 (`+models/`)
使用 MATLAB `classdef` 定义类，对应 Python 的 `dataclass`。

- **Satellite.m**: 属性包括 id, orbital_elements, sensors 等。
- **Sensor.m**: 属性包括 fov, resolution, mode 等。
- **Target.m**: 属性包括 lat, lon, priority, score 等。
- **Observation.m**: 对应 Python 中的 `BenchObservation`，包含 id, satellite_id, target_id, score, time_window。

### 2. 算法实现 (`+algorithms/`)
所有算法继承自基类 `PlanningAlgorithm.m`。

- **GeneticAlgorithm.m**: 实现 `solve` 方法，包含种群初始化、交叉、变异算子。
- **TabuSearch.m**: 实现禁忌表管理和邻域搜索。
- **SimulatedAnnealing.m**: 实现退火过程和接受准则。
- **AntColony.m**: 实现信息素更新和概率选择。
- **统一接口**: `solution = algo.solve(observations, satellites)`

### 3. STK 接口 (`+stk/`)
- **STKConnector.m**: 抽象基类。
- **COMConnector.m**: 使用 `actxserver` 连接 Windows STK。
- **MockConnector.m**: 读取预计算的 Access 数据 (JSON)，用于 Mac 开发/测试。

### 4. 数据加载与基准测试
- **run_benchmark.m**: 主脚本。
  1. 使用 `jsondecode` 读取 `benchmark_dataset/` 下的 JSON 文件。
  2. 实例化模型对象。
  3. 调用算法求解。
  4. 计算评估指标并输出结果。

## 实施步骤

1.  **基础设施搭建**: 创建目录结构，实现 JSON 读取工具。
2.  **模型类实现**: Port `models/*.py` to `+models/*.m`。
3.  **约束与评估**: 实现 `metrics_calculator` 的 MATLAB 版本。
4.  **算法移植**: 逐个移植 4 种算法。
5.  **集成测试**: 编写 `run_benchmark.m`，验证能否跑通 Global Uniform 场景。

## 关键技术点

- **JSON 支持**: MATLAB R2016b+ 原生支持 `jsondecode`。
- **面向对象**: 使用 `classdef`，属性定义在 `properties` 块，方法在 `methods` 块。
- **性能优化**: 尽量使用矩阵运算（Vectorization）替代 `for` 循环，特别是距离计算和可见性判定。
- **引用传递**: MATLAB 类默认是 Value Reference? No, `handle` class 是 Reference。需要继承 `handle` 类。

## 示例代码：Satellite 类

```matlab
classdef Satellite < handle
    properties
        Id
        Name
        Sensors
        Orbit
    end
    
    methods
        function obj = Satellite(id, name)
            obj.Id = id;
            obj.Name = name;
            obj.Sensors = {};
        end
        
        function addSensor(obj, sensor)
            obj.Sensors{end+1} = sensor;
        end
    end
end
```
