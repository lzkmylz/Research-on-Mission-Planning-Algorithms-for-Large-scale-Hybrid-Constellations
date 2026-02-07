classdef Sensor < handle %
                      SENSOR 传感器模型类

                          properties Id %
                      传感器ID Name % 传感器名称 Mode %
                      成像模式(pushbroom / spotlight等)

                      % 几何参数 FovCrossTrack % 跨轨视场角(deg) FovAlongTrack %
                      顺轨视场角(deg)

                      % 性能参数 Resolution % 分辨率(m) SwathWidth % 幅宽(km)

                      % 功耗与数据率 PowerConsumption % 功耗(W) DataRate %
                      数据率(Mbps) end

                      methods function obj = Sensor(id, name, mode, res, width,
                                                    fov_cross, fov_along) %
                                             SENSOR 构造函数 obj.Id = id;
obj.Name = name;
obj.Mode = mode;
obj.Resolution = res;
obj.SwathWidth = width;
obj.FovCrossTrack = fov_cross;
if nargin
  < 7 obj.FovAlongTrack = 0.0;
else
  obj.FovAlongTrack = fov_along;
end

    % 默认值 obj.PowerConsumption = 100.0;
obj.DataRate = 100.0;
end

    function gb = calculateDataVolume(obj, duration) % 计算数据量(GB) gb =
                      (obj.DataRate * duration) / 8 / 1024;
end end end
