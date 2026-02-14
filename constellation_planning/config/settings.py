# -*- coding: utf-8 -*-
"""
全局配置管理
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Literal
from pathlib import Path
from enum import Enum

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class OrbitBackend(Enum):
    """轨道计算后端类型"""
    MOCK = "mock"      # 简化模型，用于快速开发
    STK = "stk"        # STK 10 COM 接口（仅 Windows）
    OREKIT = "orekit"  # Orekit 高精度轨道计算（跨平台）


@dataclass
class Settings:
    """全局配置类"""
    
    # 轨道计算后端配置
    orbit_backend: str = "mock"  # "mock" | "stk" | "orekit"
    stk_version: str = "10"      # STK 版本（仅 orbit_backend="stk" 时有效）
    orekit_data_path: Optional[Path] = None  # Orekit 数据文件路径
    
    # 时间配置
    scenario_start: str = "2026-01-01T00:00:00Z"
    scenario_stop: str = "2026-01-02T00:00:00Z"
    time_step_sec: float = 60.0
    
    # 输出配置
    output_dir: Path = field(default_factory=lambda: Path("./output"))
    log_level: str = "INFO"
    
    # 随机种子（用于算法可重复性）
    random_seed: Optional[int] = 42
    
    @classmethod
    def from_yaml(cls, path: str) -> "Settings":
        """从 YAML 文件加载配置"""
        if not YAML_AVAILABLE:
            raise ImportError("需要安装 pyyaml: pip install pyyaml")
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return cls(**data)
    
    def to_yaml(self, path: str) -> None:
        """保存配置到 YAML 文件"""
        if not YAML_AVAILABLE:
            raise ImportError("需要安装 pyyaml: pip install pyyaml")
        data = {
            "orbit_backend": self.orbit_backend,
            "stk_version": self.stk_version,
            "orekit_data_path": str(self.orekit_data_path) if self.orekit_data_path else None,
            "scenario_start": self.scenario_start,
            "scenario_stop": self.scenario_stop,
            "time_step_sec": self.time_step_sec,
            "output_dir": str(self.output_dir),
            "log_level": self.log_level,
            "random_seed": self.random_seed,
        }
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
