# -*- coding: utf-8 -*-
"""
卫星管理相关Pydantic Schema

包含完整卫星模型的schema定义，用于卫星管理API。
"""

from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field, field_validator
from datetime import datetime
from enum import Enum


# ========== 枚举类型 ==========

class OrbitType(str, Enum):
    """轨道类型"""
    LEO = "LEO"
    MEO = "MEO"
    GEO = "GEO"
    SSO = "SSO"
    GTO = "GTO"


class StorageType(str, Enum):
    """存储类型"""
    SSD = "ssd"
    MLC = "mlc"
    SLC = "slc"


class Modulation(str, Enum):
    """调制方式"""
    QPSK = "qpsk"
    PSK8 = "8psk"
    QAM16 = "16qam"
    BPSK = "bpsk"


class PayloadType(str, Enum):
    """载荷类型"""
    OPTICAL = "optical"
    SAR = "sar"
    INFRARED = "infrared"
    MULTISPECTRAL = "multispectral"
    COMMUNICATION = "communication"
    SCIENTIFIC = "scientific"


# ========== Payload Schema ==========

class PayloadBase(BaseModel):
    """载荷基础Schema"""
    name: str = Field(..., min_length=1, max_length=100, description="载荷名称")
    type: PayloadType = Field(..., description="载荷类型")
    resolution_m: float = Field(..., gt=0, description="分辨率(米)")
    swath_km: float = Field(..., gt=0, description="幅宽(公里)")
    operation_modes: List[str] = Field(default=["strip"], description="工作模式")
    mass_kg: Optional[float] = Field(None, ge=0, description="质量(kg)")


class PayloadCreate(PayloadBase):
    """创建载荷请求"""
    pass


class PayloadUpdate(BaseModel):
    """更新载荷请求"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[PayloadType] = None
    resolution_m: Optional[float] = Field(None, gt=0)
    swath_km: Optional[float] = Field(None, gt=0)
    operation_modes: Optional[List[str]] = None
    mass_kg: Optional[float] = Field(None, ge=0)


class PayloadResponse(PayloadBase):
    """载荷响应"""
    pass


# ========== Satellite Schema ==========

class SatelliteBase(BaseModel):
    """卫星基础Schema"""
    # 基本信息
    name: str = Field(..., min_length=1, max_length=100, description="卫星名称")
    norad_id: Optional[str] = Field(None, max_length=20, description="NORAD ID")
    satellite_code: Optional[str] = Field(None, max_length=50, description="卫星编号")
    constellation_name: Optional[str] = Field(None, max_length=100, description="所属星座")

    # 轨道六根数 (NASA格式)
    semi_major_axis_km: float = Field(..., gt=6000, description="半长轴(km)")
    eccentricity: float = Field(..., ge=0, le=1, description="偏心率")
    inclination_deg: float = Field(..., ge=0, le=180, description="轨道倾角(度)")
    raan_deg: float = Field(default=0.0, ge=0, le=360, description="升交点赤经(度)")
    arg_perigee_deg: float = Field(default=0.0, ge=0, le=360, description="近地点幅角(度)")
    mean_anomaly_deg: float = Field(default=0.0, ge=0, le=360, description="平近点角(度)")
    epoch: Optional[datetime] = Field(None, description="参考历元")
    orbit_type: OrbitType = Field(default=OrbitType.LEO, description="轨道类型")

    # 载荷配置
    payloads: List[PayloadBase] = Field(default=[], description="载荷列表")

    # 能源配置
    solar_panel_power_w: Optional[float] = Field(None, ge=0, description="太阳能板功率(W)")
    battery_capacity_ah: Optional[float] = Field(None, ge=0, description="电池容量(Ah)")
    battery_voltage_v: Optional[float] = Field(None, ge=0, description="电池电压(V)")
    avg_power_consumption_w: Optional[float] = Field(None, ge=0, description="平均功耗(W)")
    imaging_power_w: Optional[float] = Field(None, ge=0, description="成像功耗(W)")
    downlink_power_w: Optional[float] = Field(None, ge=0, description="数传功耗(W)")

    # 存储配置
    storage_capacity_gb: Optional[float] = Field(None, ge=0, description="存储容量(GB)")
    storage_type: Optional[StorageType] = Field(None, description="存储类型")
    storage_write_rate_mbps: Optional[float] = Field(None, ge=0, description="写入速率(Mbps)")
    storage_read_rate_mbps: Optional[float] = Field(None, ge=0, description="读取速率(Mbps)")
    downlink_rate_mbps: Optional[float] = Field(None, ge=0, description="数传速率(Mbps)")
    modulation: Optional[Modulation] = Field(None, description="调制方式")
    antenna_gain_dbi: Optional[float] = Field(None, description="天线增益(dBi)")


class SatelliteCreate(SatelliteBase):
    """创建卫星请求"""
    pass


class SatelliteUpdate(BaseModel):
    """更新卫星请求"""
    # 基本信息
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    norad_id: Optional[str] = Field(None, max_length=20)
    satellite_code: Optional[str] = Field(None, max_length=50)
    constellation_name: Optional[str] = Field(None, max_length=100)

    # 轨道六根数
    semi_major_axis_km: Optional[float] = Field(None, gt=6000)
    eccentricity: Optional[float] = Field(None, ge=0, le=1)
    inclination_deg: Optional[float] = Field(None, ge=0, le=180)
    raan_deg: Optional[float] = Field(None, ge=0, le=360)
    arg_perigee_deg: Optional[float] = Field(None, ge=0, le=360)
    mean_anomaly_deg: Optional[float] = Field(None, ge=0, le=360)
    epoch: Optional[datetime] = None
    orbit_type: Optional[OrbitType] = None

    # 载荷配置
    payloads: Optional[List[PayloadBase]] = None

    # 能源配置
    solar_panel_power_w: Optional[float] = Field(None, ge=0)
    battery_capacity_ah: Optional[float] = Field(None, ge=0)
    battery_voltage_v: Optional[float] = Field(None, ge=0)
    avg_power_consumption_w: Optional[float] = Field(None, ge=0)
    imaging_power_w: Optional[float] = Field(None, ge=0)
    downlink_power_w: Optional[float] = Field(None, ge=0)

    # 存储配置
    storage_capacity_gb: Optional[float] = Field(None, ge=0)
    storage_type: Optional[StorageType] = None
    storage_write_rate_mbps: Optional[float] = Field(None, ge=0)
    storage_read_rate_mbps: Optional[float] = Field(None, ge=0)
    downlink_rate_mbps: Optional[float] = Field(None, ge=0)
    modulation: Optional[Modulation] = None
    antenna_gain_dbi: Optional[float] = None


class SatelliteResponse(SatelliteBase):
    """卫星响应Schema"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="卫星ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class SatelliteList(BaseModel):
    """卫星列表响应"""
    total: int = Field(..., description="总数")
    items: List[SatelliteResponse] = Field(..., description="卫星列表")


class SatelliteListParams(BaseModel):
    """卫星列表查询参数"""
    skip: int = Field(default=0, ge=0, description="跳过记录数")
    limit: int = Field(default=20, ge=1, le=1000, description="返回记录数上限")
    search: Optional[str] = Field(None, description="搜索关键词")
    constellation: Optional[str] = Field(None, description="星座名称筛选")
    order_by: Optional[str] = Field(None, description="排序字段")


# ========== 以下是旧版Schema，为保持向后兼容而保留 ==========
# 这些Schema用于星座模板相关的API，与上面的完整卫星管理Schema不同

from database.models import SatelliteTypeEnum


class SatelliteCapabilityBase(BaseModel):
    """卫星能力基础Schema (旧版)"""
    satellite_id: str
    max_roll_deg: float
    max_pitch_deg: float
    min_roll_deg: Optional[float] = None
    min_pitch_deg: Optional[float] = None
    max_slew_rate_deg_per_sec: Optional[float] = None


class SatelliteCapabilityCreate(SatelliteCapabilityBase):
    """创建卫星能力请求"""
    pass


class SatelliteCapabilityUpdate(BaseModel):
    """更新卫星能力请求"""
    max_roll_deg: Optional[float] = None
    max_pitch_deg: Optional[float] = None
    min_roll_deg: Optional[float] = None
    min_pitch_deg: Optional[float] = None
    max_slew_rate_deg_per_sec: Optional[float] = None


class SatelliteCapabilityResponse(SatelliteCapabilityBase):
    """卫星能力响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class SatelliteResourceBase(BaseModel):
    """卫星资源基础Schema (旧版)"""
    satellite_id: str
    storage_capacity_gb: float
    power_capacity_wh: float
    initial_storage_gb: Optional[float] = 0.0
    initial_power_wh: Optional[float] = None


class SatelliteResourceCreate(SatelliteResourceBase):
    """创建卫星资源请求"""
    pass


class SatelliteResourceUpdate(BaseModel):
    """更新卫星资源请求"""
    storage_capacity_gb: Optional[float] = None
    power_capacity_wh: Optional[float] = None
    initial_storage_gb: Optional[float] = None
    initial_power_wh: Optional[float] = None


class SatelliteResourceResponse(SatelliteResourceBase):
    """卫星资源响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class SatelliteStatusBase(BaseModel):
    """卫星状态基础Schema (旧版)"""
    satellite_id: str
    current_storage_gb: float
    current_power_wh: float
    last_update_time: datetime
    is_available: bool = True


class SatelliteStatusCreate(SatelliteStatusBase):
    """创建卫星状态请求"""
    pass


class SatelliteStatusUpdate(BaseModel):
    """更新卫星状态请求"""
    current_storage_gb: Optional[float] = None
    current_power_wh: Optional[float] = None
    last_update_time: Optional[datetime] = None
    is_available: Optional[bool] = None


class SatelliteStatusResponse(SatelliteStatusBase):
    """卫星状态响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class ImagingModeBase(BaseModel):
    """成像模式基础Schema (旧版)"""
    name: str
    mode_type: str  # strip, stare, area, spotlight, stripmap, sliding_spotlight, scanSAR
    resolution_m: float
    data_rate_mbps: float
    power_consumption_w: float
    compression_ratio: Optional[float] = None
    max_duration_sec: Optional[float] = None


class ImagingModeCreate(ImagingModeBase):
    """创建成像模式请求"""
    pass


class ImagingModeUpdate(BaseModel):
    """更新成像模式请求"""
    name: Optional[str] = None
    mode_type: Optional[str] = None
    resolution_m: Optional[float] = None
    data_rate_mbps: Optional[float] = None
    power_consumption_w: Optional[float] = None
    compression_ratio: Optional[float] = None
    max_duration_sec: Optional[float] = None


class ImagingModeResponse(ImagingModeBase):
    """成像模式响应"""
    model_config = ConfigDict(from_attributes=True)
    id: str


class ImagingModeList(BaseModel):
    """成像模式列表响应"""
    total: int
    items: List[ImagingModeResponse]


class SatelliteInfoResponse(BaseModel):
    """完整卫星信息响应 (旧版)"""
    model_config = ConfigDict(from_attributes=True)
    id: str
    name: str
    sat_type: SatelliteTypeEnum
    altitude_km: float
    inclination_deg: float
    capabilities: Optional[SatelliteCapabilityResponse] = None
    resources: Optional[SatelliteResourceResponse] = None
    imaging_modes: List[ImagingModeResponse] = []
