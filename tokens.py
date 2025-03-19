from typing import Dict, List, Any
import time
from blockchain import blockchain

class TokenSystem:
    def __init__(self):
        self.balances = {}
        self.transactions = []
        self.total_supply = 1000000
        self.carbon_price = 8
        self.carbon_records = []
    
    def init_balance(self, node_id: str, amount: float = 0) -> None:
        if node_id not in self.balances:
            self.balances[node_id] = amount
            blockchain.add_transaction({"type": "init_balance", "node_id": node_id, "amount": amount})
    
    def get_balance(self, node_id: str) -> float:
        return self.balances.get(node_id, 0)
    
    def transfer(self, from_node: str, to_node: str, amount: float, tx_type: str = "transfer") -> bool:
        if from_node not in self.balances or to_node not in self.balances:
            return False
        if self.balances[from_node] < amount:
            return False
        self.balances[from_node] -= amount
        self.balances[to_node] += amount
        tx = {"from": from_node, "to": to_node, "amount": amount, "type": tx_type, "timestamp": time.time()}
        self.transactions.append(tx)
        blockchain.add_transaction({"type": "token_transfer", "data": tx})
        blockchain.mine_pending_transactions("SuperNode_A")
        return True
    
    def reward_super_node(self, node_id: str, block_count: int) -> None:
        reward = block_count * 10
        self.balances[node_id] = self.balances.get(node_id, 0) + reward
        tx = {"from": "system", "to": node_id, "amount": reward, "type": "super_node_reward", "timestamp": time.time()}
        self.transactions.append(tx)
        blockchain.add_transaction({"type": "token_reward", "data": tx})
        blockchain.mine_pending_transactions("SuperNode_A")
    
    def compensate_carbon(self, carrier_id: str, carbon_amount: float) -> None:
        compensation = carbon_amount * self.carbon_price
        self.balances[carrier_id] = self.balances.get(carrier_id, 0) + compensation
        record = {"carrier_id": carrier_id, "carbon_amount": carbon_amount, "compensation": compensation, "timestamp": time.time()}
        self.carbon_records.append(record)
        tx = {"from": "system", "to": carrier_id, "amount": compensation, "type": "carbon_compensation", "timestamp": time.time()}
        self.transactions.append(tx)
        blockchain.add_transaction({"type": "carbon_compensation", "data": tx})
        blockchain.mine_pending_transactions("SuperNode_A")
    
    def get_flow_data(self) -> List[Dict[str, Any]]:
        return self.transactions[-10:]
    
    def get_total_supply(self) -> float:
        return self.total_supply
    
    def get_circulation(self) -> float:
        return sum(self.balances.values())
    
    def update_carbon_price(self, new_price: float) -> None:
        self.carbon_price = new_price
    
    def burn_tokens(self, amount: float) -> None:
        self.total_supply -= amount
        blockchain.add_transaction({"type": "burn_tokens", "amount": amount})
    
    def get_stats(self) -> Dict[str, Any]:
        avg_balance = sum(self.balances.values()) / len(self.balances) if self.balances else 0
        carbon_offset = sum(record["carbon_amount"] for record in self.carbon_records)
        return {
            "total_supply": self.total_supply,
            "circulation": self.get_circulation(),
            "carbon_price": self.carbon_price,
            "active_users": len(self.balances),
            "total_transactions": len(self.transactions),
            "average_balance": avg_balance,
            "latest_transaction": self.transactions[-1] if self.transactions else None,
            "system_reserve": self.total_supply - self.get_circulation(),
            "carbon_offset": carbon_offset
        }
    
    def get_carbon_data(self) -> List[Dict[str, Any]]:
        return self.carbon_records or [
            {"transport_type": "sea", "emissions": 100, "compensation": 800, "timestamp": time.time()},
            {"transport_type": "air", "emissions": 500, "compensation": 4000, "timestamp": time.time()}
        ]

token_system = TokenSystem()