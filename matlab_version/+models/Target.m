classdef Target < handle %
                      TARGET 目标模型类

                          properties Id %
                      目标ID Name % 目标名称 Type %
                      目标类型(point / grid / area)

                      % 位置(点目标) Latitude % 纬度(deg) Longitude % 经度(deg)

                      % 属性 Priority % 优先级(1 - 5) Score %
                      任务分值(用于优化目标) end

                      methods function obj =
    Target(id, name, type, lat, lon, priority) % TARGET 构造函数 obj.Id = id;
obj.Name = name;
obj.Type = type;
obj.Latitude = lat;
obj.Longitude = lon;
obj.Priority = priority;
obj.Score = priority * 10;
% 默认分值策略 end end end
