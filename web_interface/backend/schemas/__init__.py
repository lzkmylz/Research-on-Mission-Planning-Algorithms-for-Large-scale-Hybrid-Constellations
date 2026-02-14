# -*- coding: utf-8 -*-
"""
Pydantic Schemas

所有Pydantic模型定义，用于请求验证和响应序列化。
"""

# 星座相关Schema
from .constellation_schemas import (
    # 卫星模板
    SatelliteTemplateBase,
    SatelliteTemplateCreate,
    SatelliteTemplateUpdate,
    SatelliteTemplateResponse,
    SatelliteTemplateList,
    # 星座
    ConstellationBase,
    ConstellationCreate,
    ConstellationUpdate,
    ConstellationResponse,
    ConstellationList,
    # 星座-卫星关联
    ConstellationSatelliteBase,
    ConstellationSatelliteCreate,
    ConstellationSatelliteUpdate,
    ConstellationSatelliteResponse,
    ConstellationSatelliteList,
    # 详细响应
    ConstellationWithSatellitesResponse,
)

# 卫星相关Schema
from .satellite_schemas import (
    # 卫星能力
    SatelliteCapabilityBase,
    SatelliteCapabilityCreate,
    SatelliteCapabilityUpdate,
    SatelliteCapabilityResponse,
    # 卫星资源
    SatelliteResourceBase,
    SatelliteResourceCreate,
    SatelliteResourceUpdate,
    SatelliteResourceResponse,
    # 卫星状态
    SatelliteStatusBase,
    SatelliteStatusCreate,
    SatelliteStatusUpdate,
    SatelliteStatusResponse,
    # 成像模式
    ImagingModeBase,
    ImagingModeCreate,
    ImagingModeUpdate,
    ImagingModeResponse,
    ImagingModeList,
    # 完整信息
    SatelliteInfoResponse,
)

# 地面站相关Schema
from .ground_station_schemas import (
    # 地面站
    GroundStationBase,
    GroundStationCreate,
    GroundStationUpdate,
    GroundStationResponse,
    GroundStationList,
    # 天线
    AntennaBase,
    AntennaCreate,
    AntennaUpdate,
    AntennaResponse,
    AntennaList,
    # 可见窗口
    StationVisibilityWindowBase,
    StationVisibilityWindowCreate,
    StationVisibilityWindowResponse,
    StationVisibilityWindowList,
    # 详细信息
    GroundStationWithAntennasResponse,
)

# 目标相关Schema
from .target_schemas import (
    # 目标基础
    TargetBase,
    TargetCreate,
    TargetUpdate,
    TargetResponse,
    TargetList,
    # 点目标
    PointTargetCreate,
    PointTargetResponse,
    # 网格目标
    GridTargetCreate,
    GridTargetResponse,
    # 区域目标
    AreaTargetCreate,
    AreaTargetResponse,
    # 动态目标
    MovingTargetCreate,
    MovingTargetResponse,
    # 目标分组
    TargetGroupBase,
    TargetGroupCreate,
    TargetGroupUpdate,
    TargetGroupResponse,
    TargetGroupList,
    # 批量导入
    TargetBatchImportItem,
    TargetBatchImportRequest,
    TargetBatchImportResponse,
)

# 场景相关Schema
from .scenario_schemas import (
    # 场景
    ScenarioBase,
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
    ScenarioList,
    # 场景-目标关联
    ScenarioTargetBase,
    ScenarioTargetCreate,
    ScenarioTargetResponse,
    ScenarioTargetList,
    # 批量操作
    ScenarioBatchAddTargetsRequest,
    ScenarioBatchRemoveTargetsRequest,
    ScenarioBatchTargetsResponse,
    # 配置
    ScenarioConfigurationBase,
    ScenarioConfigurationCreate,
    ScenarioConfigurationUpdate,
    ScenarioConfigurationResponse,
    # 详细信息
    ScenarioDetailResponse,
    # 复制
    ScenarioCloneRequest,
    ScenarioCloneResponse,
)

# 算法配置相关Schema
from .algorithm_schemas import (
    # 算法配置
    AlgorithmConfigBase,
    AlgorithmConfigCreate,
    AlgorithmConfigUpdate,
    AlgorithmConfigResponse,
    AlgorithmConfigList,
    # 遗传算法
    GAConfigBase,
    GAConfigCreate,
    GAConfigResponse,
    # 禁忌搜索
    TabuConfigBase,
    TabuConfigCreate,
    TabuConfigResponse,
    # 模拟退火
    SAConfigBase,
    SAConfigCreate,
    SAConfigResponse,
    # 蚁群算法
    ACOConfigBase,
    ACOConfigCreate,
    ACOConfigResponse,
    # AWCSAT
    AWCSATConfigBase,
    AWCSATConfigCreate,
    AWCSATConfigResponse,
    # 算法比较
    AlgorithmComparisonRequest,
    AlgorithmComparisonResult,
    AlgorithmComparisonResponse,
)

# 规划任务相关Schema
from .planning_schemas import (
    # 规划任务
    PlanningTaskBase,
    PlanningTaskCreate,
    PlanningTaskUpdate,
    PlanningTaskResponse,
    PlanningTaskList,
    # 状态更新
    TaskStatusUpdateRequest,
    TaskProgressUpdateRequest,
    # 任务控制
    TaskControlRequest,
    TaskControlResponse,
    # 任务查询
    TaskFilterRequest,
    TaskStatisticsResponse,
    # 批量任务
    BatchTaskCreateRequest,
    BatchTaskCreateResponse,
    BatchTaskControlRequest,
    BatchTaskControlResponse,
    # 任务详情
    PlanningTaskDetailResponse,
    # 任务日志
    TaskLogBase,
    TaskLogCreate,
    TaskLogResponse,
    TaskLogList,
)

# 结果相关Schema
from .result_schemas import (
    # 规划结果
    PlanningResultBase,
    PlanningResultCreate,
    PlanningResultUpdate,
    PlanningResultResponse,
    PlanningResultList,
    # 观测记录
    ObservationBase,
    ObservationCreate,
    ObservationUpdate,
    ObservationResponse,
    ObservationList,
    # 数传计划
    DownlinkPlanBase,
    DownlinkPlanCreate,
    DownlinkPlanUpdate,
    DownlinkPlanResponse,
    DownlinkPlanList,
    # 上注计划
    UplinkPlanBase,
    UplinkPlanCreate,
    UplinkPlanUpdate,
    UplinkPlanResponse,
    UplinkPlanList,
    # 约束违规
    ConstraintViolationBase,
    ConstraintViolationCreate,
    ConstraintViolationResponse,
    ConstraintViolationList,
    # 资源时间线
    ResourceTimelineBase,
    ResourceTimelineCreate,
    ResourceTimelineResponse,
    ResourceTimelineList,
    # 详细结果
    PlanningResultDetailResponse,
    # 结果比较
    ResultComparisonRequest,
    ResultComparisonMetric,
    ResultComparisonResponse,
    # 结果导出
    ResultExportRequest,
    ResultExportResponse,
    # 结果统计
    ResultStatisticsResponse,
)

__all__ = [
    # Constellation
    "SatelliteTemplateBase",
    "SatelliteTemplateCreate",
    "SatelliteTemplateUpdate",
    "SatelliteTemplateResponse",
    "SatelliteTemplateList",
    "ConstellationBase",
    "ConstellationCreate",
    "ConstellationUpdate",
    "ConstellationResponse",
    "ConstellationList",
    "ConstellationSatelliteBase",
    "ConstellationSatelliteCreate",
    "ConstellationSatelliteUpdate",
    "ConstellationSatelliteResponse",
    "ConstellationSatelliteList",
    "ConstellationWithSatellitesResponse",

    # Satellite
    "SatelliteCapabilityBase",
    "SatelliteCapabilityCreate",
    "SatelliteCapabilityUpdate",
    "SatelliteCapabilityResponse",
    "SatelliteResourceBase",
    "SatelliteResourceCreate",
    "SatelliteResourceUpdate",
    "SatelliteResourceResponse",
    "SatelliteStatusBase",
    "SatelliteStatusCreate",
    "SatelliteStatusUpdate",
    "SatelliteStatusResponse",
    "ImagingModeBase",
    "ImagingModeCreate",
    "ImagingModeUpdate",
    "ImagingModeResponse",
    "ImagingModeList",
    "SatelliteInfoResponse",

    # Ground Station
    "GroundStationBase",
    "GroundStationCreate",
    "GroundStationUpdate",
    "GroundStationResponse",
    "GroundStationList",
    "AntennaBase",
    "AntennaCreate",
    "AntennaUpdate",
    "AntennaResponse",
    "AntennaList",
    "StationVisibilityWindowBase",
    "StationVisibilityWindowCreate",
    "StationVisibilityWindowResponse",
    "StationVisibilityWindowList",
    "GroundStationWithAntennasResponse",

    # Target
    "TargetBase",
    "TargetCreate",
    "TargetUpdate",
    "TargetResponse",
    "TargetList",
    "PointTargetCreate",
    "PointTargetResponse",
    "GridTargetCreate",
    "GridTargetResponse",
    "AreaTargetCreate",
    "AreaTargetResponse",
    "MovingTargetCreate",
    "MovingTargetResponse",
    "TargetGroupBase",
    "TargetGroupCreate",
    "TargetGroupUpdate",
    "TargetGroupResponse",
    "TargetGroupList",
    "TargetBatchImportItem",
    "TargetBatchImportRequest",
    "TargetBatchImportResponse",

    # Scenario
    "ScenarioBase",
    "ScenarioCreate",
    "ScenarioUpdate",
    "ScenarioResponse",
    "ScenarioList",
    "ScenarioTargetBase",
    "ScenarioTargetCreate",
    "ScenarioTargetResponse",
    "ScenarioTargetList",
    "ScenarioBatchAddTargetsRequest",
    "ScenarioBatchRemoveTargetsRequest",
    "ScenarioBatchTargetsResponse",
    "ScenarioConfigurationBase",
    "ScenarioConfigurationCreate",
    "ScenarioConfigurationUpdate",
    "ScenarioConfigurationResponse",
    "ScenarioDetailResponse",
    "ScenarioCloneRequest",
    "ScenarioCloneResponse",

    # Algorithm
    "AlgorithmConfigBase",
    "AlgorithmConfigCreate",
    "AlgorithmConfigUpdate",
    "AlgorithmConfigResponse",
    "AlgorithmConfigList",
    "GAConfigBase",
    "GAConfigCreate",
    "GAConfigResponse",
    "TabuConfigBase",
    "TabuConfigCreate",
    "TabuConfigResponse",
    "SAConfigBase",
    "SAConfigCreate",
    "SAConfigResponse",
    "ACOConfigBase",
    "ACOConfigCreate",
    "ACOConfigResponse",
    "AWCSATConfigBase",
    "AWCSATConfigCreate",
    "AWCSATConfigResponse",
    "AlgorithmComparisonRequest",
    "AlgorithmComparisonResult",
    "AlgorithmComparisonResponse",

    # Planning
    "PlanningTaskBase",
    "PlanningTaskCreate",
    "PlanningTaskUpdate",
    "PlanningTaskResponse",
    "PlanningTaskList",
    "TaskStatusUpdateRequest",
    "TaskProgressUpdateRequest",
    "TaskControlRequest",
    "TaskControlResponse",
    "TaskFilterRequest",
    "TaskStatisticsResponse",
    "BatchTaskCreateRequest",
    "BatchTaskCreateResponse",
    "BatchTaskControlRequest",
    "BatchTaskControlResponse",
    "PlanningTaskDetailResponse",
    "TaskLogBase",
    "TaskLogCreate",
    "TaskLogResponse",
    "TaskLogList",

    # Result
    "PlanningResultBase",
    "PlanningResultCreate",
    "PlanningResultUpdate",
    "PlanningResultResponse",
    "PlanningResultList",
    "ObservationBase",
    "ObservationCreate",
    "ObservationUpdate",
    "ObservationResponse",
    "ObservationList",
    "DownlinkPlanBase",
    "DownlinkPlanCreate",
    "DownlinkPlanUpdate",
    "DownlinkPlanResponse",
    "DownlinkPlanList",
    "UplinkPlanBase",
    "UplinkPlanCreate",
    "UplinkPlanUpdate",
    "UplinkPlanResponse",
    "UplinkPlanList",
    "ConstraintViolationBase",
    "ConstraintViolationCreate",
    "ConstraintViolationResponse",
    "ConstraintViolationList",
    "ResourceTimelineBase",
    "ResourceTimelineCreate",
    "ResourceTimelineResponse",
    "ResourceTimelineList",
    "PlanningResultDetailResponse",
    "ResultComparisonRequest",
    "ResultComparisonMetric",
    "ResultComparisonResponse",
    "ResultExportRequest",
    "ResultExportResponse",
    "ResultStatisticsResponse",
]
