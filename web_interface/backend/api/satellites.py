# -*- coding: utf-8 -*-
"""
卫星管理API

提供卫星的CRUD操作。
"""

from typing import Optional, List
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.repositories import SatelliteRepository
from database.models import Satellite, OrbitTypeEnum, StorageTypeEnum, ModulationEnum
from schemas.satellite_schemas import (
    SatelliteCreate, SatelliteUpdate, SatelliteResponse, SatelliteList,
    OrbitType, StorageType, Modulation
)

router = APIRouter()
satellite_repo = SatelliteRepository()


def _satellite_to_response(db_satellite: Satellite) -> dict:
    """将数据库卫星模型转换为响应字典"""
    return {
        "id": db_satellite.id,
        "name": db_satellite.name,
        "norad_id": db_satellite.norad_id,
        "satellite_code": db_satellite.satellite_code,
        "constellation_name": db_satellite.constellation_name,
        "semi_major_axis_km": db_satellite.semi_major_axis_km,
        "eccentricity": db_satellite.eccentricity,
        "inclination_deg": db_satellite.inclination_deg,
        "raan_deg": db_satellite.raan_deg,
        "arg_perigee_deg": db_satellite.arg_perigee_deg,
        "mean_anomaly_deg": db_satellite.mean_anomaly_deg,
        "epoch": db_satellite.epoch,
        "orbit_type": db_satellite.orbit_type.value if db_satellite.orbit_type else None,
        "payloads": db_satellite.payloads or [],
        "solar_panel_power_w": db_satellite.solar_panel_power_w,
        "battery_capacity_ah": db_satellite.battery_capacity_ah,
        "battery_voltage_v": db_satellite.battery_voltage_v,
        "avg_power_consumption_w": db_satellite.avg_power_consumption_w,
        "imaging_power_w": db_satellite.imaging_power_w,
        "downlink_power_w": db_satellite.downlink_power_w,
        "storage_capacity_gb": db_satellite.storage_capacity_gb,
        "storage_type": db_satellite.storage_type.value if db_satellite.storage_type else None,
        "storage_write_rate_mbps": db_satellite.storage_write_rate_mbps,
        "storage_read_rate_mbps": db_satellite.storage_read_rate_mbps,
        "downlink_rate_mbps": db_satellite.downlink_rate_mbps,
        "modulation": db_satellite.modulation.value if db_satellite.modulation else None,
        "antenna_gain_dbi": db_satellite.antenna_gain_dbi,
        "created_at": db_satellite.created_at,
        "updated_at": db_satellite.updated_at,
    }


def _convert_orbit_type(orbit_type: OrbitType) -> OrbitTypeEnum:
    """转换轨道类型枚举"""
    mapping = {
        OrbitType.LEO: OrbitTypeEnum.LEO,
        OrbitType.MEO: OrbitTypeEnum.MEO,
        OrbitType.GEO: OrbitTypeEnum.GEO,
        OrbitType.SSO: OrbitTypeEnum.SSO,
        OrbitType.GTO: OrbitTypeEnum.GTO,
    }
    return mapping.get(orbit_type, OrbitTypeEnum.LEO)


def _convert_storage_type(storage_type: Optional[StorageType]) -> Optional[StorageTypeEnum]:
    """转换存储类型枚举"""
    if storage_type is None:
        return None
    mapping = {
        StorageType.SSD: StorageTypeEnum.SSD,
        StorageType.MLC: StorageTypeEnum.MLC,
        StorageType.SLC: StorageTypeEnum.SLC,
    }
    return mapping.get(storage_type)


def _convert_modulation(modulation: Optional[Modulation]) -> Optional[ModulationEnum]:
    """转换调制方式枚举"""
    if modulation is None:
        return None
    mapping = {
        Modulation.QPSK: ModulationEnum.QPSK,
        Modulation.PSK8: ModulationEnum.PSK8,
        Modulation.QAM16: ModulationEnum.QAM16,
        Modulation.BPSK: ModulationEnum.BPSK,
    }
    return mapping.get(modulation)


@router.get("", response_model=SatelliteList)
async def list_satellites(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(20, ge=1, le=1000, description="返回记录数上限"),
    search: Optional[str] = Query(None, description="搜索关键词"),
    constellation: Optional[str] = Query(None, description="星座名称筛选"),
    order_by: Optional[str] = Query(None, description="排序字段"),
    db: AsyncSession = Depends(get_db)
):
    """获取卫星列表（支持分页和搜索）"""
    if search:
        # 搜索模式
        items = await satellite_repo.search(db, query=search, skip=skip, limit=limit)
        total = await satellite_repo.count_search(db, query=search)
    elif constellation:
        # 按星座筛选
        items = await satellite_repo.get_by_constellation(
            db, constellation_name=constellation, skip=skip, limit=limit
        )
        total = len(items)  # 简化处理，实际应单独查询总数
    else:
        # 普通分页
        items, total = await satellite_repo.get_multi_with_total(
            db, skip=skip, limit=limit, order_by=order_by
        )

    return {
        "total": total,
        "items": [_satellite_to_response(item) for item in items]
    }


@router.post("", response_model=SatelliteResponse, status_code=status.HTTP_201_CREATED)
async def create_satellite(
    satellite: SatelliteCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建新卫星"""
    # 准备数据
    data = satellite.model_dump()

    # 转换枚举类型
    data["orbit_type"] = _convert_orbit_type(satellite.orbit_type)
    if satellite.storage_type:
        data["storage_type"] = _convert_storage_type(satellite.storage_type)
    if satellite.modulation:
        data["modulation"] = _convert_modulation(satellite.modulation)

    # 处理payloads（已经是dict列表，可以直接存储）
    data["payloads"] = [p.model_dump() for p in satellite.payloads]

    # 创建卫星
    db_satellite = await satellite_repo.create(db, obj_in=data)

    return _satellite_to_response(db_satellite)


@router.get("/{satellite_id}", response_model=SatelliteResponse)
async def get_satellite(
    satellite_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取卫星详情"""
    db_satellite = await satellite_repo.get(db, satellite_id)
    if not db_satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卫星不存在"
        )
    return _satellite_to_response(db_satellite)


@router.put("/{satellite_id}", response_model=SatelliteResponse)
async def update_satellite(
    satellite_id: str,
    satellite_update: SatelliteUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新卫星"""
    # 检查卫星是否存在
    db_satellite = await satellite_repo.get(db, satellite_id)
    if not db_satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卫星不存在"
        )

    # 准备更新数据
    update_data = satellite_update.model_dump(exclude_unset=True)

    # 转换枚举类型
    if "orbit_type" in update_data and update_data["orbit_type"]:
        update_data["orbit_type"] = _convert_orbit_type(satellite_update.orbit_type)
    if "storage_type" in update_data and update_data["storage_type"]:
        update_data["storage_type"] = _convert_storage_type(satellite_update.storage_type)
    if "modulation" in update_data and update_data["modulation"]:
        update_data["modulation"] = _convert_modulation(satellite_update.modulation)

    # 处理payloads
    if "payloads" in update_data and update_data["payloads"] is not None:
        update_data["payloads"] = [p.model_dump() for p in satellite_update.payloads]

    # 更新卫星
    updated_satellite = await satellite_repo.update(
        db, db_obj=db_satellite, obj_in=update_data
    )

    return _satellite_to_response(updated_satellite)


@router.delete("/{satellite_id}")
async def delete_satellite(
    satellite_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除卫星"""
    # 检查卫星是否存在
    db_satellite = await satellite_repo.get(db, satellite_id)
    if not db_satellite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="卫星不存在"
        )

    # 删除卫星
    deleted = await satellite_repo.delete(db, id=satellite_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除失败"
        )

    return {"message": "卫星已删除", "id": satellite_id}
