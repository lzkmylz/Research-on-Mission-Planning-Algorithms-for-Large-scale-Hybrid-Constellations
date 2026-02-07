classdef SimulatedAnnealing <
    algorithms.PlanningAlgorithm %
        SIMULATEDANNEALING 模拟退火 MATLAB 实现

            properties InitialTemp CoolingRate MinTemp end

                methods function obj = SimulatedAnnealing(config) obj =
    obj @algorithms.PlanningAlgorithm(config);
obj.InitialTemp = 100.0;
obj.CoolingRate = 0.995;
obj.MinTemp = 0.01;

if isfield (config, 'InitialTemp')
  , obj.InitialTemp = config.InitialTemp;
end end

    function bestSol = solve(obj, observations, satellites) tic;

% 预处理 obsMap = containers.Map();
            for
              i = 1 : length(observations),
              obsMap(observations(i).Id) = observations(i);
            end obsIds = obsMap.keys;

            % 初始解 current = obj.generateRandomSolution(observations);
            currentScore = obj.evaluate(current, obsMap);
            current.Objective = currentScore;

            obj.BestSolution = current; % Value copy for struct?
            % Struct with Map: Map is handle. We need deep copy function.
            obj.BestSolution.Assignments = containers.Map(current.Assignments.keys, current.Assignments.values);

            temp = obj.InitialTemp;

            for
              iter =
                  1 : obj.Config.MaxIterations if toc > obj.Config.TimeLimit ||
                  temp < obj.MinTemp,
              break;
            end

                % 生成邻域 neighbor = current;
            neighbor.Assignments = containers.Map(current.Assignments.keys,
                                                  current.Assignments.values);

            obsId = obsIds{randi(length(obsIds))};
            if neighbor
              .Assignments.isKey(obsId) remove(neighbor.Assignments, obsId);
            else
              obs = obsMap(obsId);
            neighbor.Assignments(obsId) = obs.SatelliteId;
            end

                neighborScore = obj.evaluate(neighbor, obsMap);
            delta = neighborScore - currentScore;

            if delta
              > 0 || rand() < exp(delta / temp) current = neighbor;
            currentScore = neighborScore;

            if currentScore
              > obj.BestSolution.Objective obj.BestSolution.Objective =
                  currentScore;
            obj.BestSolution.Assignments = containers.Map(
                current.Assignments.keys, current.Assignments.values);
            end end

                obj.History(end + 1) = obj.BestSolution.Objective;
            temp = temp * obj.CoolingRate;
            end

                obj.Runtime = toc;
            bestSol = obj.BestSolution;
            end end

                methods(Access = private) function sol =
                    generateRandomSolution(obj, observations) sol.Assignments =
                        containers.Map();
            for
              i = 1 : length(observations) if rand () >
                      0.5 sol.Assignments(observations(i).Id) =
                      observations(i).SatelliteId;
            end end end

                function score = evaluate(obj, solution, obsMap) score = 0;
            keys = solution.Assignments.keys;
            for
              i = 1 : length(keys) if obsMap.isKey(keys{i}) score =
                  score + obsMap(keys{i}).Score;
            end end end end end
