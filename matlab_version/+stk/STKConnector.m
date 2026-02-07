classdef STKConnector < handle %
                            STKCONNECTOR STK 接口基类

                                properties Root %
                            STK 根对象 end

                                methods function obj =
    STKConnector() %
    构造函数 end

        function init(obj) %
    初始化 error('Method init must be implemented');
end

    function satellites =
        createWalkerConstellation(obj, config) %
        创建星座 error('Method createWalker must be implemented');
end

    function access =
        computeAccess(obj, satellites, targets) %
        计算可见性 error('Method computeAccess must be implemented');
end

        function
        close(obj) %
    关闭连接 end end end
