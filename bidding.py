from typing import List, Dict, Any, Optional, Tuple
import random
import time
from datetime import datetime, timedelta
from api import calculate_distance, fetch_carbon_footprint, verify_compliance
from dataclasses import dataclass
import math
from blockchain import blockchain

@dataclass
class BidConfig:
    min_bidders: int = 1 #降低要求
    first_round_time: int = 3600 * 24  #延长到24小时
    second_round_time: int = 1800
    max_price_increase: float = 0.2
    min_carbon_compensation: int = 50

@dataclass
class TransportRoute:
    origin: str
    destination: str
    transport_type: str
    distance: float
    carrier: str
    estimated_time: int
    carbon_footprint: float
    base_price: float

    def to_dict(self):
        """将 TransportRoute 转换为可序列化的字典"""
        return {
            "origin": self.origin,
            "destination": self.destination,
            "transport_type": self.transport_type,
            "distance": self.distance,
            "carrier": self.carrier,
            "estimated_time": self.estimated_time,
            "carbon_footprint": self.carbon_footprint,
            "base_price": self.base_price
        }

class BiddingSystem:
    def __init__(self):
        self.bids: Dict[str, Dict] = {}
        self.config = BidConfig()
        self.transport_types = {
            "sea": {"speed": 30, "base_rate": 0.5},
            "land": {"speed": 60, "base_rate": 0.8},
            "air": {"speed": 800, "base_rate": 4.0}
        }
    
    def start_bidding(self, demand: Dict[str, Any]) -> str:
        bid_id = self._generate_bid_id(demand)
        self.bids[bid_id] = {
            "id": bid_id,
            "demand": demand,
            "status": "first_round",
            "start_time": time.time(),
            "first_round_bids": [],
            "second_round_bids": [],
            "solutions": None,
            "selected_solution": None
        }
        blockchain.add_transaction({"type": "bidding_started", "bid_id": bid_id, "demand": demand})
        return bid_id
    
    def submit_first_round_bid(self, bid_id: str, carrier_id: str, 
                          base_price: float, transport_type: str) -> bool:
        if bid_id not in self.bids or self.bids[bid_id]["status"] != "first_round":
            return False
        if time.time() - self.bids[bid_id]["start_time"] > self.config.first_round_time:
            return False
        
        # 身份验证
        if not verify_compliance(carrier_id, base_price, "bidding_participation"):
            return False
        
        bid = self.bids[bid_id]
        route = self._calculate_route(bid["demand"], transport_type, carrier_id)
        bid_entry = {
            "carrier_id": carrier_id,
            "base_price": base_price,
            "transport_type": transport_type,
            "route": route.to_dict(),  # 转换为字典
            "timestamp": datetime.now().isoformat()
        }
        bid["first_round_bids"].append(bid_entry)
        bid["first_round_count"] = len(bid["first_round_bids"])
        blockchain.add_transaction({"type": "first_round_bid", "bid_id": bid_id, "data": bid_entry})
        return True
    
    def start_second_round(self, bid_id: str) -> bool:
        if bid_id not in self.bids or len(self.bids[bid_id]["first_round_bids"]) < self.config.min_bidders:
            return False
        
        bid = self.bids[bid_id]
        bid["status"] = "second_round"
        bid["second_round_bids"] = []
        bid["second_round_count"] = 0
        bid["second_round_start_time"] = time.time()  # 确保设置时间
        return True
    
    def submit_second_round_bid(self, bid_id: str, carrier_id: str, 
                           final_price: float, carbon_compensation: int) -> bool:
        if bid_id not in self.bids or self.bids[bid_id]["status"] != "second_round":
            return False
        
        # 确保 second_round_start_time 存在
        if "second_round_start_time" not in self.bids[bid_id]:
            self.bids[bid_id]["second_round_start_time"] = time.time()
        
        if time.time() - self.bids[bid_id]["second_round_start_time"] > self.config.second_round_time:
            return False
        
        # 身份验证
        if not verify_compliance(carrier_id, final_price, "bidding_participation"):
            return False
        
        # 验证价格和碳补偿
        first_bids = self.bids[bid_id]["first_round_bids"]
        first_bid = next((b for b in first_bids if b["carrier_id"] == carrier_id), None)
        if not first_bid:
            return False
        if final_price > first_bid["base_price"] * (1 + self.config.max_price_increase):
            return False
        if carbon_compensation < self.config.min_carbon_compensation:
            return False
        
        bid = self.bids[bid_id]
        bid_entry = {
            "carrier_id": carrier_id,
            "final_price": final_price,
            "carbon_compensation": carbon_compensation,
            "timestamp": datetime.now().isoformat()
        }
        bid["second_round_bids"].append(bid_entry)
        bid["second_round_count"] = len(bid["second_round_bids"])
        blockchain.add_transaction({"type": "second_round_bid", "bid_id": bid_id, "data": bid_entry})
        return True
    
    def generate_solutions(self, bid_id: str) -> List[Dict[str, Any]]:
        if bid_id not in self.bids or self.bids[bid_id]["status"] != "second_round":
            return []
        
        bid = self.bids[bid_id]
        solutions = []
        for second_bid in bid["second_round_bids"]:
            first_bid = next(b for b in bid["first_round_bids"] if b["carrier_id"] == second_bid["carrier_id"])
            route = first_bid["route"]
            solution = {
                "carrier_id": second_bid["carrier_id"],
                "transport_type": first_bid["transport_type"],
                "price": second_bid["final_price"],
                "carbon_compensation": second_bid["carbon_compensation"],
                "carbon_footprint": route["carbon_footprint"],  # 使用字典访问
                "estimated_days": math.ceil(route["estimated_time"] / 24),
                "route": route  # 已经是字典，无需再次转换
            }
            solutions.append(solution)
        
        economic = min(solutions, key=lambda x: x["price"])
        green = min(solutions, key=lambda x: x["carbon_footprint"])
        balanced = min(solutions, key=lambda x: x["price"] * 0.6 + 
                    (x["carbon_footprint"] / max(s["carbon_footprint"] for s in solutions)) * 0.4)
        
        optimized_solutions = [
            {**economic, "type": "economic"},
            {**green, "type": "green"},
            {**balanced, "type": "balanced"}
        ]
        bid["solutions"] = optimized_solutions
        bid["status"] = "completed"
        blockchain.add_transaction({"type": "solutions_generated", "bid_id": bid_id, "solutions": optimized_solutions})
        return optimized_solutions
    
    def _generate_bid_id(self, demand: Dict[str, Any]) -> str:
        return f"bid_{int(time.time())}_{demand['id']}"
    
    def _calculate_route(self, demand: Dict[str, Any], transport_type: str, carrier_id: str) -> TransportRoute:
        origin = demand["base_data"]["origin"]
        destination = demand["base_data"]["destination"]
        distance = calculate_distance(origin, destination)
        speed = self.transport_types[transport_type]["speed"]
        estimated_time = distance / speed
        carbon_footprint = fetch_carbon_footprint(distance, transport_type, demand["calculated_data"]["base_stu"])
        base_rate = self.transport_types[transport_type]["base_rate"]
        base_price = distance * base_rate * demand["calculated_data"]["base_stu"]
        return TransportRoute(origin, destination, transport_type, distance, carrier_id, 
                             estimated_time, carbon_footprint, base_price)
    
    def get_bid_status(self, bid_id: str) -> Optional[Dict[str, Any]]:
        if bid_id not in self.bids:
            return None
        bid = self.bids[bid_id]
        return {
            "id": bid["id"],
            "status": bid["status"],
            "first_round_count": len(bid["first_round_bids"]),
            "second_round_count": len(bid["second_round_bids"]),
            "solutions": bid["solutions"]
        }

bidding_system = BiddingSystem()

def start_bidding(*args, **kwargs) -> str:
    return bidding_system.start_bidding(*args, **kwargs)

def get_bid_status(*args, **kwargs) -> Optional[Dict[str, Any]]:
    return bidding_system.get_bid_status(*args, **kwargs)