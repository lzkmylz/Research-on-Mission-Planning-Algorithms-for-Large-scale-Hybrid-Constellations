# -*- coding: utf-8 -*-
"""
星座管理API
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from database.connection import get_db
from database.repositories import ConstellationRepository, SatelliteTemplateRepository
from schemas.constellation_schemas import (
    ConstellationCreate, ConstellationUpdate, ConstellationResponse,
    ConstellationWithSatellitesResponse, SatelliteTemplateCreate, SatelliteTemplateResponse
)

router = APIRouter()
constellation_repo = ConstellationRepository()
satellite_repo = SatelliteTemplateRepository()


@router.get("", response_model=List[ConstellationResponse])
async def list_constellations(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """获取星座列表"""
    constellations = await constellation_repo.get_multi(db, skip=skip, limit=limit)
    return constellations


@router.post("", response_model=ConstellationResponse)
async def create_constellation(
    constellation: ConstellationCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建星座"""
    db_constellation = await constellation_repo.create(db, obj_in=constellation.dict())
    return db_constellation


@router.get("/{constellation_id}", response_model=ConstellationWithSatellitesResponse)
async def get_constellation(
    constellation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """获取星座详情"""
    constellation = await constellation_repo.get_with_constellation(db, constellation_id)
    if not constellation:
        raise HTTPException(status_code=404, detail="星座不存在")
    return constellation


@router.put("/{constellation_id}", response_model=ConstellationResponse)
async def update_constellation(
    constellation_id: str,
    constellation_update: ConstellationUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新星座"""
    db_constellation = await constellation_repo.get(db, constellation_id)
    if not db_constellation:
        raise HTTPException(status_code=404, detail="星座不存在")

    update_data = constellation_update.dict(exclude_unset=True)
    updated = await constellation_repo.update(db, db_obj=db_constellation, obj_in=update_data)
    return updated


@router.delete("/{constellation_id}")
async def delete_constellation(
    constellation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """删除星座"""
    deleted = await constellation_repo.delete(db, id=constellation_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="星座不存在")
    return {"message": "星座已删除"}


# ========== 卫星模板路由 ==========

@router.get("/templates", response_model=List[SatelliteTemplateResponse])
async def list_satellite_templates(
    sat_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取卫星模板列表"""
    if sat_type:
        templates = await satellite_repo.get_by_type(db, sat_type)
    else:
        templates = await satellite_repo.get_all(db)
    return templates


@router.post("/templates", response_model=SatelliteTemplateResponse)
async def create_satellite_template(
    template: SatelliteTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建卫星模板"""
    db_template = await satellite_repo.create(db, obj_in=template.dict())
    return db_template