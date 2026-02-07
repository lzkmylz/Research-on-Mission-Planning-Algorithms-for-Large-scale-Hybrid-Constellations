% run_benchmark.m - 基准测试运行脚本

                        % 初始化环境 clc;
clear;
addpath(genpath(pwd));

% 导入包 import models.*import algorithms.*

        fprintf('========================================\n');
fprintf('MATLAB 星座任务规划基准测试\n');
fprintf('========================================\n');

% % 1. 加载数据 dataPath = '../benchmark_dataset';
satFile =
    fullfile(dataPath, 'constellation', 'satellites', 'constellation_200.json');
tgtFile =
    fullfile(dataPath, 'constellation', 'targets', 'global_uniform_1000.json');

fprintf('[1/3] Loading data...\n');
if
  ~exist(satFile, 'file') ||
      ~exist(tgtFile, 'file')
          error('Data files not found. Please run Python generator first.');
end

    % 读取 JSON(需 R2016b +) satData = jsondecode(fileread(satFile));
tgtData = jsondecode(fileread(tgtFile));

% 实例化卫星模型 satellites =
    models.Satellite.empty(0, length(satData.satellites));
for
  i = 1 : length(satData.satellites) s = satData.satellites(i);
% 处理可能为空的 orbital_elements alt = 500;
inc = 97.4;
if isfield (s, 'orbital_elements')
  if isfield (s.orbital_elements, 'altitude_km')
    , alt = s.orbital_elements.altitude_km;
end if isfield (s.orbital_elements, 'inclination_deg'),
    inc = s.orbital_elements.inclination_deg;
end end

    satellites(i) = models.Satellite(s.id, s.id, s.type, alt, inc);
end

    % 实例化目标模型 targets = models.Target.empty(0, length(tgtData.targets));
for
  i = 1 : length(tgtData.targets) t = tgtData.targets(i);
targets(i) = models.Target(t.id, t.id, 'point', t.latitude, t.longitude,
                           t.priority);
end

    fprintf('Loaded %d satellites and %d targets.\n', length(satellites),
            length(targets));

% % 2. 生成 /
    加载观测机会
        fprintf('[2/3] Generating observations via MockSTKConnector...\n');

% 初始化连接器 connector = stk.MockSTKConnector();
connector.init();

% 计算可见性(Mock) observations = connector.computeAccess(satellites, targets);
fprintf('Generated %d observations.\n', length(observations));

% % 3. 运行算法 fprintf('[3/3] Running Genetic Algorithm...\n');

config.MaxIterations = 50;
config.PopulationSize = 20;
config.TimeLimit = 10.0;

ga = algorithms.GeneticAlgorithm(config);
solution = ga.solve(observations, satellites);

% % 4. 结果输出 report = evaluation.MetricsCalculator.calculate(
    solution, observations, satellites, targets);
evaluation.MetricsCalculator.printReport(report);

fprintf('Runtime: %.4f seconds\n', ga.Runtime);
```
