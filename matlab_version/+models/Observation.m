classdef Observation <
    handle % OBSERVATION 观测机会模型类 %
        对应基准测试中的 BenchObservation

            properties Id %
        观测ID TargetId % 目标ID SatelliteId % 卫星ID

        % 时间窗口(ISO字符串或datetime) StartTime % 开始时间 EndTime
        % 结束时间 Duration % 持续时长(s)

        % 属性 Score %
        观测收益分值 end

        methods function obj = Observation(id, sat_id, tgt_id, start_time,
                                           end_time, duration, score) %
                               OBSERVATION 构造函数 obj.Id = id;
obj.SatelliteId = sat_id;
obj.TargetId = tgt_id;
obj.StartTime = start_time;
obj.EndTime = end_time;
obj.Duration = duration;
obj.Score = score;
end end end
