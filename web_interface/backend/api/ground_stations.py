# -*- coding: utf-8 -*-
"""
地面站管理API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.repositories import GroundStationRepository
from schemas.ground_station_schemas import (
    GroundStationCreate, GroundStationUpdate, GroundStationResponse
)

router = APIRouter()
gs_repo = GroundStationRepository()


@router.get("", response_model=List[GroundStationResponse])
async def list_ground_stations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """获取地面站列表"""
    stations = await gs_repo.get_multi(db, skip=skip, limit=limit)
    return stations


@router.post("", response_model=GroundStationResponse)
async def create_ground_station(
    station: GroundStationCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建地面站"""
    db_station = await gs_repo.create(db, obj_in=station.dict())
    return db_station


@router.get("/{station_id}", response_model=GroundStationResponse)
async def get_ground_station(
    station_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取地面站详情"""
    station = await gs_repo.get(db, station_id)
    if not station:
        raise HTTPException(status_code=404, detail="地面站不存在")
    return station


@router.put("/{station_id}", response_model=GroundStationResponse)
async def update_ground_station(
    station_id: str,
    station_update: GroundStationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新地面站"""
    db_station = await gs_repo.get(db, station_id)
    if not db_station:
        raise HTTPException(status_code=404, detail="地面站不存在")

    update_data = station_update.dict(exclude_unset=True)
    updated = await gs_repo.update(db, db_obj=db_station, obj_in=update_data)
    return updated


@router.delete("/{station_id}")
async def delete_ground_station(
    station_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除地面站"""
    deleted = await gs_repo.delete(db, id=station_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="地面站不存在")
    return {"message": "地面站已删除"}


@router.get("/region/search")
async def search_by_region(
    min_lat: float,
    max_lat: float,
    min_lon: float,
    max_lon: float,
    db: AsyncSession = Depends(get_db)
):
    """根据地理位置范围搜索地面站"""
    stations = await gs_repo.get_by_location(db, min_lat, max_lat, min_lon, max_lon)
    return stations