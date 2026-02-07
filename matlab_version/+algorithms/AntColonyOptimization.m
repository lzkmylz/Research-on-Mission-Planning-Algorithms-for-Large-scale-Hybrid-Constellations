classdef AntColonyOptimization <
    algorithms.PlanningAlgorithm %
        ANTCOLONYOPTIMIZATION 蚁群算法 MATLAB 实现

            properties NumAnts Alpha Beta Rho Q Pheromone end

                methods function obj = AntColonyOptimization(config) obj =
    obj @algorithms.PlanningAlgorithm(config);
obj.NumAnts = 20;
obj.Alpha = 1.0;
obj.Beta = 2.0;
obj.Rho = 0.5;
obj.Q = 100.0;
obj.Pheromone = containers.Map();
end

    function bestSol = solve(obj, observations, satellites) tic;

% 预处理 obsMap = containers.Map();
            for
              i = 1 : length(observations) obsMap(observations(i).Id) =
                          observations(i);
            obj.Pheromone(observations(i).Id) = 1.0;
            % Init pheromone end obsIds = obsMap.keys;

            for
              iter = 1 : obj.Config.MaxIterations if toc > obj.Config.TimeLimit,
              break;
            end

                antSolutions = cell(1, obj.NumAnts);

                % 蚂蚁构建解
                for k = 1:obj.NumAnts
                    sol = obj.constructSolution(obsMap, obsIds);
                antSolutions{k} = sol;

                if isempty (obj.BestSolution)
                  || sol.Objective >
                          obj.BestSolution.Objective obj.BestSolution = sol;
                end end

                    % 更新信息素 obj.updatePheromone(antSolutions);

                obj.History(end + 1) = obj.BestSolution.Objective;
                end

                    obj.Runtime = toc;
                bestSol = obj.BestSolution;
                end end

                    methods(Access = private) function sol =
                        constructSolution(obj, obsMap, obsIds) sol.Assignments =
                            containers.Map();

            for
              i = 1 : length(obsIds) id = obsIds{i};
            obs = obsMap(id);

            tau = obj.Pheromone(id);
            eta = obs.Score / 10.0;
            % Normalize

                    prob = (tau ^ obj.Alpha) * (eta ^ obj.Beta);
            threshold = prob / (prob + 1);

            if rand ()
              < threshold sol.Assignments(id) = obs.SatelliteId;
            end end

                sol.Objective = obj.evaluate(sol, obsMap);
            end

                    function updatePheromone(obj, solutions) %
                蒸发 keys = obj.Pheromone.keys;
            for
              i = 1 : length(keys) obj.Pheromone(keys{i}) =
                  obj.Pheromone(keys{i}) * (1 - obj.Rho);
            end

                % 增强 bestObj = 1.0;
            if
              ~isempty(obj.BestSolution), bestObj = max(
                                              1.0, obj.BestSolution.Objective); end
            
            for k = 1:length(solutions)
                sol = solutions{k};
            deposit = (sol.Objective / bestObj) *
                      (obj.Q / (length(sol.Assignments) + 1));

            keys = sol.Assignments.keys;
                for
                  i = 1 : length(keys) id = keys{i};
                obj.Pheromone(id) = obj.Pheromone(id) + deposit;
                end end end

                    function score = evaluate(obj, solution, obsMap) score = 0;
                keys = solution.Assignments.keys;
            for
              i = 1 : length(keys) if obsMap.isKey(keys{i}) score =
                  score + obsMap(keys{i}).Score;
            end end end end end
