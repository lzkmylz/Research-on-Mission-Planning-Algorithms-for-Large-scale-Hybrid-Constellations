# -*- coding: utf-8 -*-
"""
全局配置管理
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class Settings:
    """全局配置类"""
    
    # STK 配置
    stk_version: str = "10"
    stk_use_mock: bool = True  # Mac开发时使用Mock
    
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
            "stk_version": self.stk_version,
            "stk_use_mock": self.stk_use_mock,
            "scenario_start": self.scenario_start,
            "scenario_stop": self.scenario_stop,
            "time_step_sec": self.time_step_sec,
            "output_dir": str(self.output_dir),
            "log_level": self.log_level,
            "random_seed": self.random_seed,
        }
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
