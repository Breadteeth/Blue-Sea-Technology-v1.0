import random
from typing import Dict, Any, Optional
import time
from datetime import datetime, timedelta
import math
from blockchain import blockchain

# 模拟全局物流状态存储，用于在模拟环境中存储和更新物流状态
# 必要性：在模拟环境中，我们没有真实的物流系统数据库，因此使用全局字典来模拟状态存储
# 合理性：这种方法简化了状态管理，适合快速验证支付和物流流程，而无需引入复杂的数据库或外部 API
global_logistics_status = {}

# 全局 PaymentSystem 实例，由 main.py 设置
# 必要性：api.py 需要访问 PaymentSystem 实例以获取支付状态，确保物流状态与支付状态一致
# 合理性：在模拟环境中，通过全局变量共享实例是一种简化实现的方式，避免了复杂的依赖注入
global_payment_system = None

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
        """检查物流状态，优先使用 global_logistics_status，确保与支付状态同步"""
        global global_payment_system
        
        # 优先从 global_logistics_status 获取状态
        if tracking_number in global_logistics_status:
            current_stage = global_logistics_status[tracking_number]["current_stage"]
            print(f"Debug: Retrieved current_stage from global_logistics_status: {current_stage}")
        # 若无记录，尝试从 global_payment_system 获取
        elif global_payment_system is not None:
            payment = global_payment_system.payments.get(tracking_number, {})
            current_stage = payment.get("current_stage", "warehouse")
            print(f"Debug: Retrieved current_stage from payment system: {current_stage}")
        # 最后的 fallback
        else:
            print("Debug: global_payment_system is None, falling back to default stage")
            current_stage = "warehouse"

        # 更新或初始化 global_logistics_status
        if tracking_number not in global_logistics_status:
            global_logistics_status[tracking_number] = {
                "tracking_number": tracking_number,
                "current_stage": current_stage,
                "status": "normal",
                "last_update": datetime.now().isoformat(),
                "location": "Shanghai",
                "estimated_arrival": (datetime.now() + timedelta(days=2)).isoformat(),
                "delay_hours": 0
            }
        else:
            global_logistics_status[tracking_number]["current_stage"] = current_stage
            global_logistics_status[tracking_number]["last_update"] = datetime.now().isoformat()

        return global_logistics_status[tracking_number]
    
    def update_logistics_status(self, tracking_number: str, stage: str) -> None:
        """更新物流状态，确保状态持久化"""
        print(f"Debug: Updating logistics status for tracking_number: {tracking_number} to stage: {stage}")
        if tracking_number in global_logistics_status:
            global_logistics_status[tracking_number]["current_stage"] = stage
            global_logistics_status[tracking_number]["last_update"] = datetime.now().isoformat()
            global_logistics_status[tracking_number]["location"] = "Singapore" if stage == "transport" else "Shanghai"
        else:
            global_logistics_status[tracking_number] = {
                "tracking_number": tracking_number,
                "current_stage": stage,
                "status": "normal",
                "last_update": datetime.now().isoformat(),
                "location": "Shanghai",
                "estimated_arrival": (datetime.now() + timedelta(days=2)).isoformat(),
                "delay_hours": 0
            }
    
    def verify_compliance(self, user_id: str, amount: float, transaction_type: str) -> bool:
        """简化合规性检查"""
        credit_score = blockchain.get_node_credit_score(user_id)
        print(f"Debug: {user_id} credit_score = {credit_score}")
        return True
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        """获取汇率，带动态波动"""
        if from_currency not in self.exchange_rates or to_currency not in self.exchange_rates[from_currency]:
            return None
        base_rate = self.exchange_rates[from_currency][to_currency]
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

def update_logistics_status(*args, **kwargs):
    return logistics_api.update_logistics_status(*args, **kwargs)