from typing import Dict, Any, List, Optional
import time
from datetime import datetime
import hashlib
import json
from enum import Enum
from api import verify_compliance, check_logistics_status
from blockchain import blockchain

class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

    def to_json(self):
        """将 PaymentStatus 转换为可序列化的字符串"""
        return self.value

class PaymentStage(Enum):
    WAREHOUSE = "warehouse"
    CUSTOMS = "customs"
    TRANSPORT = "transport"
    DELIVERY = "delivery"

    def to_json(self):
        """将 PaymentStage 转换为可序列化的字符串"""
        return self.value

class PaymentSystem:
    def __init__(self):
        self.payments: Dict[str, Dict] = {}
        self.stage_weights = {
            PaymentStage.WAREHOUSE: 0.3,
            PaymentStage.CUSTOMS: 0.4,
            PaymentStage.TRANSPORT: 0.2,
            PaymentStage.DELIVERY: 0.1
        }
    
    def create_payment(self, solution: Dict[str, Any], payer_id: str, currency: str = "USD") -> str:
        payment_id = self._generate_payment_id(solution, payer_id)
        total_amount = solution["price"]
        stage_amounts = {stage.to_json(): total_amount * weight for stage, weight in self.stage_weights.items()}
        
        payment = {
            "id": payment_id,
            "solution_id": solution["carrier_id"],  # 简化，使用carrier_id
            "payer_id": payer_id,
            "carrier_id": solution["carrier_id"],
            "total_amount": total_amount,
            "currency": currency,
            "stage_amounts": stage_amounts,
            "paid_amounts": {},
            "current_stage": PaymentStage.WAREHOUSE.to_json(),  # 转换为字符串
            "status": PaymentStatus.PENDING.to_json(),  # 转换为字符串
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "completed_at": None,
            "stage_timestamps": {},
            "refund_info": None
        }
        self.payments[payment_id] = payment
        blockchain.add_transaction({"type": "payment_created", "data": payment})
        return payment_id
    
    def _generate_payment_id(self, solution: Dict, payer_id: str) -> str:
        data = f"{solution['carrier_id']}{payer_id}{time.time()}"
        return f"pay_{hashlib.sha256(data.encode()).hexdigest()[:8]}"
    
    def trigger_stage_payment(self, payment_id: str, stage: PaymentStage, proof: Dict[str, Any]) -> bool:
        if payment_id not in self.payments:
            return False
        payment = self.payments[payment_id]
        if payment["current_stage"] != stage.to_json() or payment["status"] != PaymentStatus.PENDING.to_json():
            return False
        
        # 身份验证
        if not verify_compliance(payment["payer_id"], payment["stage_amounts"][stage.to_json()], "payment"):
            return False
        if not verify_compliance(payment["carrier_id"], payment["stage_amounts"][stage.to_json()], "payment_receive"):
            return False
        
        # 验证物流状态
        tracking_status = check_logistics_status(payment_id)
        if not self._verify_payment_condition(stage, proof, tracking_status):
            return False
        
        amount = payment["stage_amounts"][stage.to_json()]
        if self._process_payment(payment_id, stage, amount):
            payment["paid_amounts"][stage.to_json()] = amount
            payment["stage_timestamps"][stage.to_json()] = datetime.now().isoformat()
            stages = list(PaymentStage)
            current_index = stages.index(stage)
            if current_index < len(stages) - 1:
                payment["current_stage"] = stages[current_index + 1].to_json()  # 转换为字符串
            else:
                payment["status"] = PaymentStatus.COMPLETED.to_json()  # 转换为字符串
                payment["completed_at"] = datetime.now().isoformat()
            payment["updated_at"] = datetime.now().isoformat()
            blockchain.add_transaction({
                "type": "payment_stage",
                "payment_id": payment_id,
                "stage": stage.to_json(),  # 转换为字符串
                "amount": amount
            })
            return True
        return False
    
    def _verify_payment_condition(self, stage: PaymentStage, proof: Dict[str, Any], tracking_status: Dict) -> bool:
        stage_str = stage.to_json()
        if stage_str == PaymentStage.WAREHOUSE.to_json():
            return proof.get("warehouse_receipt") and tracking_status["current_stage"] == "warehouse"
        elif stage_str == PaymentStage.CUSTOMS.to_json():
            return all(k in proof for k in ["customs_declaration", "inspection_cert"]) and \
                   tracking_status["current_stage"] == "customs"
        elif stage_str == PaymentStage.TRANSPORT.to_json():
            return proof.get("tracking_status") == "in_transit" and tracking_status["current_stage"] == "transport"
        elif stage_str == PaymentStage.DELIVERY.to_json():
            return proof.get("delivery_confirmation") and tracking_status["current_stage"] == "delivery"
        return False
    
    def _process_payment(self, payment_id: str, stage: PaymentStage, amount: float) -> bool:
        return True  # 模拟支付成功
    
    def get_payment_status(self, payment_id: str) -> Optional[Dict[str, Any]]:
        if payment_id not in self.payments:
            return None
        payment = self.payments[payment_id]
        return {
            "id": payment["id"],
            "status": payment["status"],
            "current_stage": payment["current_stage"],
            "total_amount": payment["total_amount"],
            "paid_amount": sum(payment["paid_amounts"].values()),
            "remaining_amount": payment["total_amount"] - sum(payment["paid_amounts"].values()),
            "updated_at": payment["updated_at"]
        }
    
    def request_refund(self, payment_id: str, reason: str) -> bool:
        if payment_id not in self.payments or self.payments[payment_id]["status"] != PaymentStatus.COMPLETED.to_json():
            return False
        payment = self.payments[payment_id]
        payment["refund_info"] = {
            "reason": reason,
            "requested_at": datetime.now().isoformat(),
            "status": "pending",
            "amount": sum(payment["paid_amounts"].values())
        }
        blockchain.add_transaction({"type": "refund_requested", "payment_id": payment_id, "reason": reason})
        return True
    
    def process_refund(self, payment_id: str, approved: bool) -> bool:
        if payment_id not in self.payments or not self.payments[payment_id].get("refund_info"):
            return False
        payment = self.payments[payment_id]
        if payment["refund_info"]["status"] == "pending":
            payment["refund_info"]["status"] = "completed" if approved else "rejected"
            payment["refund_info"]["processed_at"] = datetime.now().isoformat()
            if approved:
                payment["status"] = PaymentStatus.REFUNDED.to_json()  # 转换为字符串
            blockchain.add_transaction({"type": "refund_processed", "payment_id": payment_id, "approved": approved})
            return True
        return False
    
    def get_payment_history(self, payer_id: str) -> List[Dict[str, Any]]:
        return [p for p in self.payments.values() if p["payer_id"] == payer_id]
    
    def get_stage_statistics(self) -> Dict[str, Any]:
        stats = {stage.to_json(): {"count": 0, "total_amount": 0} for stage in PaymentStage}
        for payment in self.payments.values():
            for stage, amount in payment["paid_amounts"].items():
                stats[stage]["count"] += 1
                stats[stage]["total_amount"] += amount
        return stats