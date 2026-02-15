# -*- coding: utf-8 -*-
"""
卫星管理API测试

遵循TDD原则：先写测试，再实现功能
"""

import pytest
from datetime import datetime


# ========== 测试数据 ==========

@pytest.fixture
def sample_satellite_data():
    """示例卫星数据"""
    return {
        "name": "测试卫星-001",
        "norad_id": "40001",
        "satellite_code": "SAT-001",
        "constellation_name": "测试星座",
        "semi_major_axis_km": 6878.137,
        "eccentricity": 0.001,
        "inclination_deg": 97.4,
        "raan_deg": 45.0,
        "arg_perigee_deg": 30.0,
        "mean_anomaly_deg": 60.0,
        "epoch": datetime.utcnow().isoformat(),
        "orbit_type": "LEO",
        "payloads": [
            {
                "name": "主载荷",
                "type": "optical",
                "resolution_m": 2.0,
                "swath_km": 50,
                "operation_modes": ["strip", "stare"],
                "mass_kg": 100
            }
        ],
        "solar_panel_power_w": 500.0,
        "battery_capacity_ah": 40.0,
        "battery_voltage_v": 28.0,
        "avg_power_consumption_w": 200.0,
        "imaging_power_w": 80.0,
        "downlink_power_w": 60.0,
        "storage_capacity_gb": 500.0,
        "storage_type": "ssd",
        "storage_write_rate_mbps": 500.0,
        "storage_read_rate_mbps": 800.0,
        "downlink_rate_mbps": 450.0,
        "modulation": "qpsk",
        "antenna_gain_dbi": 15.0
    }


@pytest.fixture
def sample_satellite_data_minimal():
    """最小卫星数据（仅必填字段）"""
    return {
        "name": "最小卫星",
        "semi_major_axis_km": 6878.137,
        "eccentricity": 0.001,
        "inclination_deg": 97.4,
        "raan_deg": 0.0,
        "arg_perigee_deg": 0.0,
        "mean_anomaly_deg": 0.0,
        "orbit_type": "LEO"
    }


# ========== API端点测试 ==========

class TestSatelliteEndpoints:
    """卫星API端点测试"""

    def test_list_satellites_empty(self, client):
        """测试获取空卫星列表"""
        response = client.get("/api/satellites")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    def test_create_satellite(self, client, sample_satellite_data):
        """测试创建卫星"""
        response = client.post("/api/satellites", json=sample_satellite_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_satellite_data["name"]
        assert data["norad_id"] == sample_satellite_data["norad_id"]
        assert data["id"] is not None
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_satellite_minimal(self, client, sample_satellite_data_minimal):
        """测试创建最小卫星数据"""
        response = client.post("/api/satellites", json=sample_satellite_data_minimal)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_satellite_data_minimal["name"]
        assert data["id"] is not None

    def test_create_satellite_invalid_data(self, client):
        """测试创建卫星时传入无效数据"""
        invalid_data = {
            "name": "",  # 空名称
            "semi_major_axis_km": -100,  # 无效值
        }
        response = client.post("/api/satellites", json=invalid_data)
        assert response.status_code == 422

    def test_get_satellite(self, client, sample_satellite_data):
        """测试获取单个卫星详情"""
        # 先创建卫星
        create_response = client.post("/api/satellites", json=sample_satellite_data)
        satellite_id = create_response.json()["id"]

        # 获取卫星详情
        response = client.get(f"/api/satellites/{satellite_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == satellite_id
        assert data["name"] == sample_satellite_data["name"]
        assert data["payloads"] == sample_satellite_data["payloads"]

    def test_get_satellite_not_found(self, client):
        """测试获取不存在的卫星"""
        response = client.get("/api/satellites/non-existent-id")
        assert response.status_code == 404

    def test_update_satellite(self, client, sample_satellite_data):
        """测试更新卫星"""
        # 先创建卫星
        create_response = client.post("/api/satellites", json=sample_satellite_data)
        satellite_id = create_response.json()["id"]

        # 更新卫星
        update_data = {
            "name": "更新后的卫星名称",
            "solar_panel_power_w": 600.0
        }
        response = client.put(f"/api/satellites/{satellite_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "更新后的卫星名称"
        assert data["solar_panel_power_w"] == 600.0
        # 未更新的字段应保持不变
        assert data["norad_id"] == sample_satellite_data["norad_id"]

    def test_update_satellite_not_found(self, client):
        """测试更新不存在的卫星"""
        update_data = {"name": "新名称"}
        response = client.put("/api/satellites/non-existent-id", json=update_data)
        assert response.status_code == 404

    def test_delete_satellite(self, client, sample_satellite_data):
        """测试删除卫星"""
        # 先创建卫星
        create_response = client.post("/api/satellites", json=sample_satellite_data)
        satellite_id = create_response.json()["id"]

        # 删除卫星
        response = client.delete(f"/api/satellites/{satellite_id}")
        assert response.status_code == 200

        # 确认已删除
        get_response = client.get(f"/api/satellites/{satellite_id}")
        assert get_response.status_code == 404

    def test_delete_satellite_not_found(self, client):
        """测试删除不存在的卫星"""
        response = client.delete("/api/satellites/non-existent-id")
        assert response.status_code == 404

    def test_list_satellites_with_pagination(self, client, sample_satellite_data):
        """测试卫星列表分页"""
        # 创建多个卫星
        for i in range(5):
            data = sample_satellite_data.copy()
            data["name"] = f"卫星-{i}"
            data["satellite_code"] = f"SAT-{i:03d}"
            client.post("/api/satellites", json=data)

        # 测试分页
        response = client.get("/api/satellites?skip=0&limit=2")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 5
        assert len(data["items"]) == 2

        # 测试第二页
        response = client.get("/api/satellites?skip=2&limit=2")
        data = response.json()
        assert len(data["items"]) == 2

    def test_list_satellites_search(self, client, sample_satellite_data):
        """测试搜索卫星"""
        # 创建卫星
        client.post("/api/satellites", json=sample_satellite_data)

        # 搜索
        response = client.get("/api/satellites?search=测试卫星")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 1

    def test_create_satellite_with_multiple_payloads(self, client):
        """测试创建带多个载荷的卫星"""
        data = {
            "name": "多载荷卫星",
            "semi_major_axis_km": 6878.137,
            "eccentricity": 0.001,
            "inclination_deg": 97.4,
            "raan_deg": 0.0,
            "arg_perigee_deg": 0.0,
            "mean_anomaly_deg": 0.0,
            "orbit_type": "LEO",
            "payloads": [
                {
                    "name": "光学相机",
                    "type": "optical",
                    "resolution_m": 0.5,
                    "swath_km": 20,
                    "operation_modes": ["strip", "stare"],
                    "mass_kg": 80
                },
                {
                    "name": "SAR雷达",
                    "type": "sar",
                    "resolution_m": 1.0,
                    "swath_km": 30,
                    "operation_modes": ["stripmap", "spotlight"],
                    "mass_kg": 120
                }
            ]
        }
        response = client.post("/api/satellites", json=data)
        assert response.status_code == 201
        result = response.json()
        assert len(result["payloads"]) == 2
        assert result["payloads"][0]["name"] == "光学相机"
        assert result["payloads"][1]["name"] == "SAR雷达"


class TestSatelliteEdgeCases:
    """卫星API边界情况测试"""

    def test_create_satellite_with_null_optional_fields(self, client):
        """测试创建卫星时可选字段为null"""
        data = {
            "name": "测试卫星",
            "semi_major_axis_km": 6878.137,
            "eccentricity": 0.001,
            "inclination_deg": 97.4,
            "raan_deg": 0.0,
            "arg_perigee_deg": 0.0,
            "mean_anomaly_deg": 0.0,
            "orbit_type": "LEO",
            "norad_id": None,
            "payloads": []
        }
        response = client.post("/api/satellites", json=data)
        assert response.status_code == 201
        result = response.json()
        assert result["norad_id"] is None
        assert result["payloads"] == []

    def test_create_satellite_with_special_characters(self, client):
        """测试卫星名称包含特殊字符"""
        data = {
            "name": "卫星-测试_001 (V2.0)",
            "semi_major_axis_km": 6878.137,
            "eccentricity": 0.001,
            "inclination_deg": 97.4,
            "raan_deg": 0.0,
            "arg_perigee_deg": 0.0,
            "mean_anomaly_deg": 0.0,
            "orbit_type": "LEO"
        }
        response = client.post("/api/satellites", json=data)
        assert response.status_code == 201
        assert response.json()["name"] == data["name"]

    def test_update_satellite_with_empty_payloads(self, client, sample_satellite_data):
        """测试更新卫星时清空载荷"""
        create_response = client.post("/api/satellites", json=sample_satellite_data)
        satellite_id = create_response.json()["id"]

        update_data = {"payloads": []}
        response = client.put(f"/api/satellites/{satellite_id}", json=update_data)
        assert response.status_code == 200
        assert response.json()["payloads"] == []

    def test_orbital_element_bounds(self, client):
        """测试轨道元素边界值"""
        # 测试无效的偏心率（大于1）
        invalid_data = {
            "name": "无效卫星",
            "semi_major_axis_km": 6878.137,
            "eccentricity": 1.5,  # 无效
            "inclination_deg": 97.4,
            "raan_deg": 0.0,
            "arg_perigee_deg": 0.0,
            "mean_anomaly_deg": 0.0,
            "orbit_type": "LEO"
        }
        response = client.post("/api/satellites", json=invalid_data)
        assert response.status_code == 422

        # 测试无效的倾角（大于180）
        invalid_data["eccentricity"] = 0.001
        invalid_data["inclination_deg"] = 200
        response = client.post("/api/satellites", json=invalid_data)
        assert response.status_code == 422
