classdef TabuSearch <
    algorithms.PlanningAlgorithm %
        TABUSEARCH 禁忌搜索 MATLAB 实现

            properties TabuTenure NeighborhoodSize TabuList end

                methods function obj = TabuSearch(config) obj =
    obj @algorithms.PlanningAlgorithm(config);
obj.TabuTenure = 10;
obj.NeighborhoodSize = 20;
obj.TabuList = {};
% Cell array of strings

    if isfield (config, 'TabuTenure'),
    obj.TabuTenure = config.TabuTenure;
end end

    function bestSol = solve(obj, observations, satellites) tic;

% 1. 预处理 obsMap = containers.Map();
            for
              i = 1 : length(observations),
              obsMap(observations(i).Id) = observations(i);
            end obsIds = obsMap.keys;

            % 2. 初始解(贪婪) current = obj.generateGreedySolution(observations,
                                                                   satellites);
            currentScore = obj.evaluate(current, obsMap);

            obj.BestSolution = current;
            obj.BestSolution.Objective = currentScore;

            % 3. 迭代
            for iter = 1:obj.Config.MaxIterations
                if toc > obj.Config.TimeLimit, break;
            end

                % 生成邻域 bestNeighbor = [];
            bestNeighborScore = -Inf;
            bestMove = '';

                for
                  k = 1 : obj.NeighborhoodSize % 随机翻转 obsId =
                          obsIds{randi(length(obsIds))};
                neighbor = current;
                % struct copy by value ? No,
                    assignments map is reference ! %
                        Map is handle class.So we must copy map
                            explicitly.neighbor.Assignments = containers.Map(
                        current.Assignments.keys, current.Assignments.values);

                move = ['flip_' obsId];
                if neighbor
                  .Assignments.isKey(obsId) remove(neighbor.Assignments, obsId);
                else
                  % 简化：如果不在解中，尝试加入（假设 SatID 固定） obs =
                      obsMap(obsId);
                neighbor.Assignments(obsId) = obs.SatelliteId;
                end

                    score = obj.evaluate(neighbor, obsMap);

                % 检查禁忌 isTabu = any(strcmp(obj.TabuList, move));
                isAspiration = (score > obj.BestSolution.Objective);

                if
                  ~isTabu || isAspiration if score >
                                 bestNeighborScore bestNeighbor = neighbor;
                bestNeighborScore = score;
                bestMove = move;
                end end end

                    %
                    更新当前解 if ~isempty(bestNeighbor) current = bestNeighbor;
                currentScore = bestNeighborScore;

                % 更新禁忌表 obj.TabuList{end + 1} = bestMove;
                if length (obj.TabuList)
                  > obj.TabuTenure obj.TabuList(1) = [];
                end

                        % 更新全局最优 if currentScore >
                    obj.BestSolution.Objective obj.BestSolution = current;
                obj.BestSolution.Objective = currentScore;
                end end

                    obj.History(end + 1) = obj.BestSolution.Objective;
                end

                    obj.Runtime = toc;
                bestSol = obj.BestSolution;
                end end

                    methods(Access = private) function sol =
                        generateGreedySolution(obj, observations, satellites)
                            sol.Assignments = containers.Map();
                % 简单按分数排序[~, idx] =
                    sort([observations.Score], 'descend');
            for
              k = 1 : length(idx) obs = observations(idx(k));
            % 贪婪加入 sol.Assignments(obs.Id) = obs.SatelliteId;
            end sol.Objective = 0;
            end

                function score = evaluate(obj, solution, obsMap) score = 0;
            keys = solution.Assignments.keys;
            for
              i = 1 : length(keys) if obsMap.isKey(keys{i}) score =
                  score + obsMap(keys{i}).Score;
            end end end end end
