classdef MockSTKConnector <
    stk.STKConnector %
        MOCKSTKCONNECTOR 模拟 STK 接口(用于 Mac 开发)

            methods function obj = MockSTKConnector() obj = obj
                                                            @stk.STKConnector();
end

    function init(obj) fprintf('Initialized Mock STK Connector.\n');
end

    function satellites =
        createWalkerConstellation(obj, config) import models.Satellite fprintf(
            'Mocking Walker constellation creation...\n');
% 返回虚拟对象 satellites = models.Satellite.empty(0, 0);
end

    function access = computeAccess(obj, satellites, targets)
                          import models.Observation fprintf(
                              'Mocking Access calculation...\n');
% 简单生成随机 Access access = models.Observation.empty(0, 0);

rng(42);
            for
              k = 1 : 500 satIdx = randi(length(satellites));
            tgtIdx = randi(length(targets));
            sat = satellites(satIdx);
            tgt = targets(tgtIdx);

            obsId = sprintf('OBS_%d', k);
            score = tgt.Priority * 10;

            obs =
                models.Observation(obsId, sat.Id, tgt.Id, '2026-01-01T00:00:00',
                                   '2026-01-01T00:10:00', 600, score);
            access(k) = obs;
            end end end end
