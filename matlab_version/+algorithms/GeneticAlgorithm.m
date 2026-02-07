classdef GeneticAlgorithm < algorithms.PlanningAlgorithm %
                                GENETICALGORITHM 遗传算法 MATLAB 实现

                                    properties PopulationSize CrossoverRate
                                        MutationRate ElitismCount end

                                            methods function obj =
    GeneticAlgorithm(config) % 构造函数 obj =
        obj @algorithms.PlanningAlgorithm(config);

obj.PopulationSize = 50;
obj.CrossoverRate = 0.8;
obj.MutationRate = 0.1;
obj.ElitismCount = 2;

if isfield (config, 'PopulationSize')
  , obj.PopulationSize = config.PopulationSize;
end if isfield (config, 'CrossoverRate'),
    obj.CrossoverRate = config.CrossoverRate;
end if isfield (config, 'MutationRate'), obj.MutationRate = config.MutationRate;
end end

    function bestSol =
        solve(obj, observations, satellites) % SOLVE 执行遗传算法 tic;

% 1. 预处理：建立 ID->Observation 映射以加速查询 obsMap = containers.Map();
            for
              i = 1 : length(observations) obsMap(observations(i).Id) =
                          observations(i);
            end obsIds = obsMap.keys;

            % 2. 初始化种群 %
                解表示：Assignments
                    Map(ObsID->SatID) population = cell(1, obj.PopulationSize);
            for
              i = 1 : obj.PopulationSize population{i} =
                  obj.generateRandomSolution(observations, satellites);
            end
            
            % 3. 迭代
            for gen = 1:obj.Config.MaxIterations
                if toc > obj.Config.TimeLimit
                    break;
            end

                % 评估 scores = zeros(1, obj.PopulationSize);
                for
                  i = 1 : obj.PopulationSize scores(i) =
                      obj.evaluate(population{i}, obsMap);

                % 更新全局最优 if isempty (obj.BestSolution) ||
                    scores(i) > obj.BestSolution.Objective obj.BestSolution =
                    population{i};
                obj.BestSolution.Objective = scores(i);
                end end

                    obj.History(end + 1) = obj.BestSolution.Objective;

                % 选择(锦标赛) newPop = cell(1, obj.PopulationSize);
                % 精英保留[~, sortedIdx] = sort(scores, 'descend');
                for
                  k = 1 : obj.ElitismCount newPop{k} = population{sortedIdx(k)};
                end

                    currentCount = obj.ElitismCount;
                while
                  currentCount < obj.PopulationSize parent1 =
                      obj.tournamentSelection(population, scores);
                parent2 = obj.tournamentSelection(population, scores);

                if rand ()
                  < obj.CrossoverRate[child1, child2] =
                      obj.crossover(parent1, parent2, obsIds);
                else
                  child1 = parent1;
                child2 = parent2;
                end

                    child1 = obj.mutate(child1, observations, satellites);
                child2 = obj.mutate(child2, observations, satellites);

                if currentCount
                  < obj.PopulationSize currentCount = currentCount + 1;
                newPop{currentCount} = child1;
                end if currentCount < obj.PopulationSize currentCount =
                    currentCount + 1;
                newPop{currentCount} = child2;
                end end

                    population = newPop;
                end

                    obj.Runtime = toc;
                bestSol = obj.BestSolution;
                end end

                    methods(Access = private) function sol =
                        generateRandomSolution(obj, observations, satellites)
                            sol.Assignments = containers.Map();
            for
              i = 1
                  : length(observations) if rand () >
                    0.5 %
                        假设 Observation 已包含可行卫星列表(Mock step needed) %
                        这里简化为随机分配给卫星 ID %
                        注意：Python 版本中 obs.satellite_id
                        是预计算好的单个可行解？
                        % 不，Python 中 obs 可能有多个窗口。 %
                        但 run_benchmark.py 中 BenchObservation 包含
                        'satellite_id' 属性，
                        %
                        这意味着 BenchObservation
                        本身就是一个(Task, Satellite,
                                     Time) 的元组，即一个可行窗口。
                        %
                        所以分配非常简单：如果要选这个
                        Observation(窗口)，它的 SatID 是固定的。

                        obs = observations(i);
            sol.Assignments(obs.Id) = obs.SatelliteId;
            end end sol.Objective = 0;
            % 待评估 end

                    function score = evaluate(obj, solution, obsMap) score = 0;
            keys = solution.Assignments.keys;
            for
              i = 1 : length(keys) if obsMap.isKey(keys{i}) obs =
                  obsMap(keys{i});
            score = score + obs.Score;
            end end end

                function selected = tournamentSelection(obj, pop, scores) k = 3;
            idx = randperm(length(pop), k);
            bestIdx = idx(1);
            for
              i = 2 : k if scores (idx(i)) > scores(bestIdx) bestIdx = idx(i);
            end end selected = pop{bestIdx};
            end

                function[c1, c2] =
                    crossover(obj, p1, p2, obsIds) % 单点交叉 point =
                        randi(length(obsIds));

            c1.Assignments = containers.Map();
            c2.Assignments = containers.Map();

            % 前半段
            for i = 1:point
                id = obsIds{i};
            if p1
              .Assignments.isKey(id), c1.Assignments(id) = p1.Assignments(id);
            end if p2.Assignments.isKey(id), c2.Assignments(id) =
                                                 p2.Assignments(id); end
            end
            
            % 后半段
            for i = (point+1):length(obsIds)
                id = obsIds{i};
            if p2
              .Assignments.isKey(id), c1.Assignments(id) = p2.Assignments(id);
            end if p1.Assignments.isKey(id), c2.Assignments(id) =
                                                 p1.Assignments(id);
            end end

                c1.Objective = 0;
            c2.Objective = 0;
            end

                function sol = mutate(obj, sol, observations, satellites) keys =
                    sol.Assignments.keys;
            % 随机移除
            for i = 1:length(keys)
                if rand() < obj.MutationRate
                    remove(sol.Assignments, keys{i});
                end
            end
            
            % 随机添加
            for i = 1:length(observations)
                obs = observations(i);
                if
                  ~sol.Assignments.isKey(obs.Id) &&
                      rand() < obj.MutationRate sol.Assignments(obs.Id) =
                      obs.SatelliteId;
                end end end end end
