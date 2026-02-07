classdef MetricsCalculator < handle % METRICSCALCULATOR 评估指标计算器

                                      methods(Static)
function report = calculate(solution, observations, satellites, targets) %
                  CALCULATE 计算所有指标

                  % 1. 基本统计 numAssigned = solution.Assignments.Count;
totalTasks = length(targets);
completionRate = numAssigned / totalTasks;

% 2. 总收益 totalScore = solution.Objective;

% 3. 资源利用率(需模拟) % 简单起见，假设每个任务消耗 10 % 存储 avgStorageUsage =
    min(1.0, numAssigned * 0.05);
% Mock

    % 4. 任务响应时间(需详细时间信息) avgResponseTime = 0.0;

report = struct();
report.NumAssigned = numAssigned;
report.CompletionRate = completionRate;
report.TotalScore = totalScore;
report.AvgStorageUsage = avgStorageUsage;
report.AvgResponseTime = avgResponseTime;
end

    function printReport(report) fprintf('\n=== Evaluation Report ===\n');
fprintf('Tasks Assigned: %d\n', report.NumAssigned);
fprintf('Completion Rate: %.2f%%\n', report.CompletionRate * 100);
fprintf('Total Priority Score: %.2f\n', report.TotalScore);
fprintf('Avg Storage Usage: %.2f%%\n', report.AvgStorageUsage * 100);
fprintf('=========================\n');
end end end
