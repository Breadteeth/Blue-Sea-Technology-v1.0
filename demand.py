from typing import Dict, Any, List, Optional
import hashlib
import json
import time
from datetime import datetime
from api import calculate_distance, verify_compliance
from dataclasses import dataclass
import math
from blockchain import blockchain  # 添加导入

@dataclass
class CLPItem:
    """集装箱装箱单物品"""
    name: str
    quantity: int
    weight: float
    volume: float
    category: str
    dangerous: bool = False

class DemandProcessor:
    def __init__(self):
        self.demands: Dict[str, Dict] = {}
        self.stu_factors = {"普通货物": 1.0, "易碎品": 1.2, "冷链": 1.3, "危险品": 1.5}
        self.time_factors = {"标准型 (5-7天)": 1.0, "加急型 (3天)": 1.4, "超急型 (24小时)": 2.0}
    
    def process_demand(self, weight: float, volume: float, origin: str, destination: str,
                      cargo_type: str = "普通货物", delivery_time: str = "标准型 (5-7天)",
                      clp_items: List[Dict] = None, merchant_id: str = "Merchant_1") -> Dict[str, Any]:
        """
        处理并标准化物流需求，包含身份验证
        
        Args:
            weight: 重量(kg)
            volume: 体积(m³)
            origin: 始发地
            destination: 目的地
            cargo_type: 货物类型
            delivery_time: 期望时效
            clp_items: CLP物品列表
            merchant_id: 商家ID
            
        Returns:
            标准化的需求数据
        """
        print("Debug: blockchain is", blockchain)  # 添加调试输出
        
        # 输入验证
        if weight <= 0 or volume <= 0:
            raise ValueError("Weight and volume must be positive")
        if cargo_type not in self.stu_factors:
            raise ValueError(f"Unknown cargo type: {cargo_type}")
        if delivery_time not in self.time_factors:
            raise ValueError(f"Unknown delivery time: {delivery_time}")
        
        # 身份验证
        if not verify_compliance(merchant_id, weight * 0.1, "demand_submission"):  # 假设0.1为估算金额
            raise ValueError(f"Merchant {merchant_id} failed compliance check")
        
        # 计算基础STU
        base_stu = max(weight / 1000, volume / 3)
        adjusted_stu = base_stu * self.stu_factors[cargo_type] * self.time_factors[delivery_time]
        
        # 计算距离
        distance = calculate_distance(origin, destination)
        
        # 验证CLP并生成签名
        clp_valid = self._validate_clp(clp_items) if clp_items else False
        clp_signature = self._generate_clp_signature(clp_items) if clp_items else "N/A"
        
        # 生成需求ID
        demand_id = self._generate_demand_id(weight, volume, origin, destination, time.time())
        
        # 构建需求对象
        demand = {
            "id": demand_id,
            "timestamp": datetime.now().isoformat(),
            "status": "pending",
            "merchant_id": merchant_id,
            "base_data": {
                "weight": weight,
                "volume": volume,
                "origin": origin,
                "destination": destination,
                "cargo_type": cargo_type,
                "delivery_time": delivery_time
            },
            "calculated_data": {
                "base_stu": base_stu,
                "adjusted_stu": adjusted_stu,
                "distance": distance,
                "estimated_base_cost": self._estimate_base_cost(adjusted_stu, distance)
            },
            "clp_data": {
                "valid": clp_valid,
                "items": clp_items,
                "signature": clp_signature,
                "verification_time": datetime.now().isoformat()
            }
        }
        
        # 存储并记录到区块链
        self.demands[demand_id] = demand
        blockchain.add_transaction({"type": "demand", "data": demand})
        return demand
    
    def _validate_clp(self, clp_items: List[Dict]) -> bool:
        """验证CLP物品列表"""
        try:
            total_weight = sum(item["weight"] * item["quantity"] for item in clp_items)
            total_volume = sum(item["volume"] * item["quantity"] for item in clp_items)
            
            if total_weight <= 0 or total_volume <= 0 or total_weight > 28000 or total_volume > 67.7:
                return False
            
            for item in clp_items:
                if item.get("dangerous", False):
                    if not verify_compliance("system", total_weight, "dangerous_goods"):
                        return False
            return True
        except Exception as e:
            print(f"CLP validation error: {str(e)}")
            return False
    
    def _generate_clp_signature(self, clp_items: List[Dict]) -> str:
        """生成CLP签名（模拟）"""
        clp_string = json.dumps(clp_items, sort_keys=True)
        return hashlib.sha256(clp_string.encode()).hexdigest()
    
    def _generate_demand_id(self, weight: float, volume: float, origin: str, 
                           destination: str, timestamp: float) -> str:
        data = f"{weight}{volume}{origin}{destination}{timestamp}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]
    
    def _estimate_base_cost(self, stu: float, distance: float) -> float:
        return stu * distance * 0.1 + 50 + (stu * 10)
    
    def update_demand_status(self, demand_id: str, status: str) -> None:
        if demand_id in self.demands:
            self.demands[demand_id]["status"] = status
            self.demands[demand_id]["last_updated"] = datetime.now().isoformat()
    
    def get_demand(self, demand_id: str) -> Optional[Dict[str, Any]]:
        return self.demands.get(demand_id)
    
    def list_active_demands(self) -> List[Dict[str, Any]]:
        return [d for d in self.demands.values() if d["status"] in ["pending", "bidding", "processing"]]
    
    def get_demand_statistics(self) -> Dict[str, Any]:
        total_demands = len(self.demands)
        active_demands = len(self.list_active_demands())
        total_stu = sum(d["calculated_data"]["adjusted_stu"] for d in self.demands.values())
        return {
            "total_demands": total_demands,
            "active_demands": active_demands,
            "total_stu": total_stu,
            "average_stu": total_stu / total_demands if total_demands > 0 else 0
        }

demand_processor = DemandProcessor()

def process_demand(*args, **kwargs) -> Dict[str, Any]:
    return demand_processor.process_demand(*args, **kwargs)

def validate_clp(clp_items: List[Dict]) -> bool:
    return demand_processor._validate_clp(clp_items)

def get_demand_stats() -> Dict[str, Any]:
    return demand_processor.get_demand_statistics()