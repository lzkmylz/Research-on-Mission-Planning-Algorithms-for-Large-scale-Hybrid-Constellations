# -*- coding: utf-8 -*-
"""STK 接口层"""

from .interface import STKInterface
from .mock_connector import MockSTKConnector
from .walker import WalkerConstellationBuilder
from .connector_factory import get_connector

# Windows 平台才导入真实连接器
import sys
if sys.platform == "win32":
    from .stk_connector import STK10Connector

__all__ = [
    "STKInterface",
    "MockSTKConnector",
    "WalkerConstellationBuilder",
    "get_connector",
]

