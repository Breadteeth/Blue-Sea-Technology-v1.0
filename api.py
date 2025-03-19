import random
from typing import Dict, Any, Optional
import time
from datetime import datetime, timedelta
import math
from blockchain import blockchain

class LogisticsAPI:
    def __init__(self):
        self.carbon_factors = {
            "sea": (0.01, 0.02),
            "land": (0.05, 0.08),
            "air": (0.45, 0.55)
        }
        self.distances = {
            ("Shanghai", "Singapore"): 4480,
            ("Shanghai", "Bangkok"): 3780,
            ("Singapore", "Jakarta"): 880,
            ("Bangkok", "Ho Chi Minh"): 750
        }
        self.exchange_rates = {
            "USD": {"CNY": 6.45, "EUR": 0.85, "SGD": 1.35},
            "CNY": {"USD": 0.155, "EUR": 0.13, "SGD": 0.21},
            "EUR": {"USD": 1.18, "CNY": 7.65, "SGD": 1.59}
        }
        self.weather_conditions = ["clear", "rain", "storm", "fog"]
    
    def calculate_distance(self, origin: str, destination: str) -> float:
        direct = (origin, destination)
        reverse = (destination, origin)
        if direct in self.distances:
            return self.distances[direct]
        elif reverse in self.distances:
            return self.distances[reverse]
        else:
            # 模拟多段运输
            midpoints = ["Singapore", "Bangkok"]
            if random.random() > 0.5 and origin not in midpoints and destination not in midpoints:
                midpoint = random.choice(midpoints)
                return self.calculate_distance(origin, midpoint) + self.calculate_distance(midpoint, destination)
            return random.uniform(500, 5000)
    
    def fetch_carbon_footprint(self, distance: float, transport_type: str, weight: float = 1.0) -> float:
        if transport_type not in self.carbon_factors:
            raise ValueError(f"Unknown transport type: {transport_type}")
        min_factor, max_factor = self.carbon_factors[transport_type]
        factor = random.uniform(min_factor, max_factor)
        # 考虑天气影响
        weather = random.choice(self.weather_conditions)
        weather_factor = 1.0 if weather == "clear" else 1.2 if weather == "rain" else 1.5
        return distance * weight * factor * weather_factor
    
    def check_logistics_status(self, tracking_number: str) -> Dict[str, Any]:
        stages = ["warehouse", "customs", "transport", "delivery"]
        current_stage = random.choice(stages)
        delay = random.randint(0, 48) if random.random() > 0.8 else 0  # 20%概率有延误
        return {
            "tracking_number": tracking_number,
            "current_stage": current_stage,
            "status": "delayed" if delay > 0 else "normal",
            "last_update": datetime.now().isoformat(),
            "location": random.choice(["Shanghai", "Singapore", "Bangkok"]),
            "estimated_arrival": (datetime.now() + timedelta(days=random.randint(1, 7) + delay)).isoformat(),
            "delay_hours": delay
        }
    
    # def verify_compliance(self, user_id: str, amount: float, transaction_type: str) -> bool:
    #     # 模拟合规性检查，基于信用评分和金额
    #     credit_score = blockchain.get_node_credit_score(user_id)
    #     if credit_score < 5.0 or (amount > 1000000 and random.random() > 0.3):
    #         blockchain.update_node_credit_score(user_id, -1.0)  # 降低信用分
    #         return False
    #     return random.random() > 0.1
    
    def verify_compliance(self, user_id: str, amount: float, transaction_type: str) -> bool:
        credit_score = blockchain.get_node_credit_score(user_id)
        print(f"Debug: {user_id} credit_score = {credit_score}")  # 添加调试
        # 临时返回 True
        return True
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        if from_currency not in self.exchange_rates or to_currency not in self.exchange_rates[from_currency]:
            return None
        base_rate = self.exchange_rates[from_currency][to_currency]
        # 动态波动基于时间
        hour = datetime.now().hour
        fluctuation = math.sin(hour / 24 * 2 * math.pi) * 0.05  # ±5%日内波动
        return base_rate * (1 + fluctuation)

logistics_api = LogisticsAPI()

def calculate_distance(*args, **kwargs):
    return logistics_api.calculate_distance(*args, **kwargs)

def fetch_carbon_footprint(*args, **kwargs):
    return logistics_api.fetch_carbon_footprint(*args, **kwargs)

def check_logistics_status(*args, **kwargs):
    return logistics_api.check_logistics_status(*args, **kwargs)

def verify_compliance(*args, **kwargs):
    return logistics_api.verify_compliance(*args, **kwargs)

def get_exchange_rate(*args, **kwargs):
    return logistics_api.get_exchange_rate(*args, **kwargs)