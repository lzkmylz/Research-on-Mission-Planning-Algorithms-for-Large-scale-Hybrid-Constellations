# -*- coding: utf-8 -*-
"""
连接器工厂 - 根据配置返回合适的轨道计算后端
"""

import sys
from typing import TYPE_CHECKING

from .interface import STKInterface
from .mock_connector import MockSTKConnector

if TYPE_CHECKING:
    from ..config.settings import Settings


def get_connector(settings: "Settings") -> STKInterface:
    """
    根据配置返回合适的轨道计算连接器
    
    Args:
        settings: 全局配置对象
        
    Returns:
        STKInterface 实例
        
    Raises:
        RuntimeError: STK 后端仅在 Windows 上可用
        ValueError: 未知的后端类型
        ImportError: Orekit 未安装
    """
    backend = settings.orbit_backend.lower()
    
    if backend == "mock":
        return MockSTKConnector()
    
    elif backend == "orekit":
        try:
            from .orekit_connector import OrekitConnector
        except ImportError as e:
            raise ImportError(
                "Orekit 未安装。请使用 conda 安装：\n"
                "  conda install -c conda-forge orekit\n"
                f"原始错误: {e}"
            ) from e
        return OrekitConnector(data_path=settings.orekit_data_path)
    
    elif backend == "stk":
        if sys.platform != "win32":
            raise RuntimeError(
                "STK 后端仅在 Windows 上可用。\n"
                "在 Mac/Linux 上请使用 'mock' 或 'orekit' 后端。"
            )
        from .stk_connector import STK10Connector
        return STK10Connector(version=settings.stk_version)
    
    else:
        raise ValueError(
            f"未知的轨道计算后端: '{backend}'\n"
            f"支持的后端: 'mock', 'stk', 'orekit'"
        )
