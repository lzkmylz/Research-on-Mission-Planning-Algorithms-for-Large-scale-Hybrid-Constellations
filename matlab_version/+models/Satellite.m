classdef Satellite < handle
    % SATELLITE 卫星模型类
    
    properties
        Id              % 卫星ID
        Name            % 卫星名称
        SatType         % 卫星类型 (optical/sar)
        
        % 轨道参数
        Altitude        % 轨道高度 (km)
        Inclination     % 轨道倾角 (deg)
        
        % 载荷列表
        Sensors         % 传感器对象数组 (cell array)
        
        % 资源参数
        StorageCapacity % 存储容量 (GB)
        CurrentStorage  % 当前已用存储 (GB)
        PowerCapacity   % 电池容量 (Wh)
    end
    
    methods
        function obj = Satellite(id, name, type, alt, inc)
            % SATELLITE 构造函数
            obj.Id = id;
            obj.Name = name;
            obj.SatType = type;
            obj.Altitude = alt;
            obj.Inclination = inc;
            obj.Sensors = {};
            
            % 默认值
            obj.StorageCapacity = 100.0;
            obj.CurrentStorage = 0.0;
            obj.PowerCapacity = 1000.0;
        end
        
        function addSensor(obj, sensor)
            % 添加传感器
            obj.Sensors{end+1} = sensor;
        end
        
        function valid = checkStorage(obj, needed)
            % 检查存储是否足够
            valid = (obj.CurrentStorage + needed) <= obj.StorageCapacity;
        end
        
        function consumeStorage(obj, amount)
            % 消耗存储
            obj.CurrentStorage = obj.CurrentStorage + amount;
        end
        
        function resetStorage(obj)
            % 重置存储
            obj.CurrentStorage = 0.0;
        end
    end
end
