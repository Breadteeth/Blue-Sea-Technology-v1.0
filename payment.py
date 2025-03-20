from typing import Dict, Any, List, Optional
import time
from datetime import datetime
import hashlib
import json
from enum import Enum
from api import verify_compliance, check_logistics_status
from blockchain import blockchain

# 确保这些定义在文件顶部，且没有缩进到其他类或方法中
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
        print("Debug: Creating payment for solution:", solution)
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
            "refund_info": None,
            "solution": solution  # 存储 solution 以便后续使用
        }
        self.payments[payment_id] = payment
        blockchain.add_transaction({"type": "payment_created", "data": payment})
        print("Debug: Payment created with ID:", payment_id)
        return payment_id
    
    def _generate_payment_id(self, solution: Dict, payer_id: str) -> str:
        data = f"{solution['carrier_id']}{payer_id}{time.time()}"
        return f"pay_{hashlib.sha256(data.encode()).hexdigest()[:8]}"
    
    def advance_payment(self, payment_id: str) -> bool:
        print("Debug: Entering advance_payment with payment_id:", payment_id)
        if payment_id not in self.payments:
            print("Debug: Payment ID not found:", payment_id)
            return False
        
        # 调试：检查 PaymentStage 和 PaymentStatus 是否可用
        print("Debug: Checking PaymentStage in advance_payment...")
        print("Debug: globals() keys:", list(globals().keys()))
        print("Debug: PaymentStage in globals():", 'PaymentStage' in globals())
        print("Debug: PaymentStatus in globals():", 'PaymentStatus' in globals())
        
        payment = self.payments[payment_id]
        print("Debug: Payment details:", payment)
        
        if payment["status"] == PaymentStatus.COMPLETED.to_json():
            print("Debug: Payment already completed:", payment_id)
            return False
        
        # 模拟物流状态检查
        print("Debug: Checking logistics status for stage:", payment["current_stage"])
        tracking_status = check_logistics_status(payment_id)
        print("Debug: Tracking status:", tracking_status)
        if tracking_status["current_stage"] != payment["current_stage"]:
            print("Debug: Logistics stage mismatch. Expected:", payment["current_stage"], "Got:", tracking_status["current_stage"])
            return False
        
        # 计算当前阶段的支付金额
        stage = payment["current_stage"]
        print("Debug: Current stage:", stage)
        try:
            stage_percentage = self.stage_weights[PaymentStage(stage)]
        except Exception as e:
            print(f"Debug: Error accessing PaymentStage: {str(e)}")
            raise
        stage_amount = payment["total_amount"] * stage_percentage
        print("Debug: Stage percentage:", stage_percentage, "Stage amount:", stage_amount)
        
        # 更新支付状态
        payment["paid_amounts"][stage] = stage_amount
        payment["remaining_amount"] = payment["total_amount"] - sum(payment["paid_amounts"].values())
        payment["updated_at"] = datetime.now().isoformat()
        
        # 推进到下一阶段
        try:
            stages = [stage.to_json() for stage in PaymentStage]
        except Exception as e:
            print(f"Debug: Error accessing PaymentStage for stages: {str(e)}")
            raise
        current_index = stages.index(payment["current_stage"])
        if current_index < len(stages) - 1:
            payment["current_stage"] = stages[current_index + 1]
        else:
            payment["status"] = PaymentStatus.COMPLETED.to_json()
        print("Debug: Updated current_stage to:", payment["current_stage"])
        
        # 记录碳补偿（在 delivery 阶段）
        try:
            if payment["current_stage"] == PaymentStage.DELIVERY.to_json() and payment["status"] != PaymentStatus.COMPLETED.to_json():
                carbon_compensation = payment.get("solution", {}).get("carbon_compensation", 0)
                print("Debug: Carbon compensation:", carbon_compensation)
                # tokens.compensate_carbon(carbon_compensation)
                pass
        except Exception as e:
            print(f"Debug: Error in carbon compensation block: {str(e)}")
            raise
        
        blockchain.add_transaction({"type": "payment_advanced", "payment": payment})
        print("Debug: Payment advanced successfully:", payment_id)
        
        # 同步物流状态
        # 必要性：支付系统在推进阶段后需要通知物流系统更新状态，以保持两者一致
        # 合理性：在模拟环境中，通过调用 update_logistics_status 模拟真实的物流系统状态更新
        try:
            from api import update_logistics_status
            update_logistics_status(payment_id, payment["current_stage"])
            print("Debug: Logistics status updated to:", payment["current_stage"])
        except ImportError as e:
            print(f"Debug: Failed to update logistics status: {str(e)}")
        
        return True
    
    def trigger_stage_payment(self, payment_id: str, stage: PaymentStage, proof: Dict[str, Any]) -> bool:
        print("Debug: Entering trigger_stage_payment with payment_id:", payment_id, "stage:", stage.to_json())
        if payment_id not in self.payments:
            print("Debug: Payment ID not found:", payment_id)
            return False
        payment = self.payments[payment_id]
        if payment["current_stage"] != stage.to_json() or payment["status"] != PaymentStatus.PENDING.to_json():
            print("Debug: Stage or status mismatch. Current stage:", payment["current_stage"], "Status:", payment["status"])
            return False
        
        # 身份验证
        if not verify_compliance(payment["payer_id"], payment["stage_amounts"][stage.to_json()], "payment"):
            print("Debug: Payer compliance check failed")
            return False
        if not verify_compliance(payment["carrier_id"], payment["stage_amounts"][stage.to_json()], "payment_receive"):
            print("Debug: Carrier compliance check failed")
            return False
        
        # 验证物流状态
        tracking_status = check_logistics_status(payment_id)
        print("Debug: Tracking status:", tracking_status)
        if not self._verify_payment_condition(stage, proof, tracking_status):
            print("Debug: Payment condition verification failed")
            print("Debug: Proof provided:", proof)
            print("Debug: Expected stage:", stage.to_json(), "Actual logistics stage:", tracking_status["current_stage"])
            return False
        
        amount = payment["stage_amounts"][stage.to_json()]
        if self._process_payment(payment_id, stage, amount):
            payment["paid_amounts"][stage.to_json()] = amount
            payment["stage_timestamps"][stage.to_json()] = datetime.now().isoformat()
            stages = list(PaymentStage)
            current_index = stages.index(stage)
            if current_index < len(stages) - 1:
                payment["current_stage"] = stages[current_index + 1].to_json()
            else:
                payment["status"] = PaymentStatus.COMPLETED.to_json()
                payment["completed_at"] = datetime.now().isoformat()
            payment["updated_at"] = datetime.now().isoformat()
            blockchain.add_transaction({
                "type": "payment_stage",
                "payment_id": payment_id,
                "stage": stage.to_json(),
                "amount": amount
            })
            print("Debug: Stage payment triggered successfully:", payment_id)
            return True
        print("Debug: Payment processing failed")
        return False
    
    def _verify_payment_condition(self, stage: PaymentStage, proof: Dict[str, Any], tracking_status: Dict) -> bool:
        stage_str = stage.to_json()
        print("Debug: Verifying payment condition for stage:", stage_str)
        if stage_str == PaymentStage.WAREHOUSE.to_json():
            result = proof.get("warehouse_receipt") and tracking_status["current_stage"] == "warehouse"
            print("Debug: Warehouse condition - warehouse_receipt:", proof.get("warehouse_receipt"), "stage match:", tracking_status["current_stage"] == "warehouse")
            return result
        elif stage_str == PaymentStage.CUSTOMS.to_json():
            result = all(k in proof for k in ["customs_declaration", "inspection_cert"]) and \
                     tracking_status["current_stage"] == "customs"
            print("Debug: Customs condition - customs_declaration:", "customs_declaration" in proof, 
                  "inspection_cert:", "inspection_cert" in proof, "stage match:", tracking_status["current_stage"] == "customs")
            return result
        elif stage_str == PaymentStage.TRANSPORT.to_json():
            result = proof.get("tracking_status") == "in_transit" and tracking_status["current_stage"] == "transport"
            print("Debug: Transport condition - tracking_status:", proof.get("tracking_status"), 
                  "stage match:", tracking_status["current_stage"] == "transport")
            return result
        elif stage_str == PaymentStage.DELIVERY.to_json():
            result = proof.get("delivery_confirmation") and tracking_status["current_stage"] == "delivery"
            print("Debug: Delivery condition - delivery_confirmation:", proof.get("delivery_confirmation"), 
                  "stage match:", tracking_status["current_stage"] == "delivery")
            return result
        return False
    
    def _process_payment(self, payment_id: str, stage: PaymentStage, amount: float) -> bool:
        print("Debug: Processing payment for payment_id:", payment_id, "stage:", stage.to_json(), "amount:", amount)
        return True  # 模拟支付成功
    
    def get_payment_status(self, payment_id: str) -> Optional[Dict[str, Any]]:
        print("Debug: Getting payment status for payment_id:", payment_id)
        if payment_id not in self.payments:
            print("Debug: Payment ID not found:", payment_id)
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
        print("Debug: Requesting refund for payment_id:", payment_id)
        if payment_id not in self.payments or self.payments[payment_id]["status"] != PaymentStatus.COMPLETED.to_json():
            print("Debug: Cannot request refund, payment not completed or not found")
            return False
        payment = self.payments[payment_id]
        payment["refund_info"] = {
            "reason": reason,
            "requested_at": datetime.now().isoformat(),
            "status": "pending",
            "amount": sum(payment["paid_amounts"].values())
        }
        blockchain.add_transaction({"type": "refund_requested", "payment_id": payment_id, "reason": reason})
        print("Debug: Refund requested successfully:", payment_id)
        return True
    
    def process_refund(self, payment_id: str, approved: bool) -> bool:
        print("Debug: Processing refund for payment_id:", payment_id, "approved:", approved)
        if payment_id not in self.payments or not self.payments[payment_id].get("refund_info"):
            print("Debug: No refund info found for payment_id:", payment_id)
            return False
        payment = self.payments[payment_id]
        if payment["refund_info"]["status"] == "pending":
            payment["refund_info"]["status"] = "completed" if approved else "rejected"
            payment["refund_info"]["processed_at"] = datetime.now().isoformat()
            if approved:
                payment["status"] = PaymentStatus.REFUNDED.to_json()
            blockchain.add_transaction({"type": "refund_processed", "payment_id": payment_id, "approved": approved})
            print("Debug: Refund processed successfully:", payment_id)
            return True
        print("Debug: Refund not in pending state")
        return False
    
    def get_payment_history(self, payer_id: str) -> List[Dict[str, Any]]:
        print("Debug: Getting payment history for payer_id:", payer_id)
        return [p for p in self.payments.values() if p["payer_id"] == payer_id]
    
    def get_stage_statistics(self) -> Dict[str, Any]:
        print("Debug: Getting stage statistics")
        stats = {stage.to_json(): {"count": 0, "total_amount": 0} for stage in PaymentStage}
        for payment in self.payments.values():
            for stage, amount in payment["paid_amounts"].items():
                stats[stage]["count"] += 1
                stats[stage]["total_amount"] += amount
        return stats