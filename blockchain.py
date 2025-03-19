import time
import hashlib
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import random
from datetime import datetime

@dataclass
class Block:
    """区块结构"""
    index: int
    timestamp: float
    transactions: List[Dict[str, Any]]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    
    def calculate_hash(self) -> str:
        """计算区块哈希"""
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

@dataclass
class Node:
    """节点结构"""
    id: str
    node_type: str  # "super_node", "warehouse", "carrier", "merchant"
    stake: float = 0.0  # 质押代币数量
    credit_score: float = 8.0  # 初始信用分
    location: str = ""
    last_active: float = time.time()

class Blockchain:
    def __init__(self):
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.nodes: Dict[str, Node] = {}
        self.difficulty = 4  # PoW难度
        
        # 创建创世区块
        self.create_genesis_block()
        
        # 初始化一些测试节点
        self._init_test_nodes()
    
    def create_genesis_block(self) -> None:
        """创建创世区块"""
        genesis_block = Block(
            index=0,
            timestamp=time.time(),
            transactions=[{"type": "genesis", "data": "Genesis Block"}],
            previous_hash="0"
        )
        genesis_block.hash = genesis_block.calculate_hash()
        self.chain.append(genesis_block)
    
    def _init_test_nodes(self) -> None:
        """初始化测试节点"""
        # 添加超级节点
        for i in range(3):
            node_id = f"SuperNode_{chr(65+i)}"  # SuperNode_A, SuperNode_B, ...
            self.add_node(node_id, "super_node", stake=1000.0, location="Shanghai")
        
        # 添加仓储节点
        warehouses = ["Shanghai", "Singapore", "Bangkok"]
        for i, location in enumerate(warehouses):
            node_id = f"Warehouse_{i+1}"
            self.add_node(node_id, "warehouse", stake=500.0, location=location)
        
        # 添加承运商节点
        carriers = ["sea", "land", "air"]
        for i, carrier_type in enumerate(carriers):
            node_id = f"Carrier_{carrier_type.capitalize()}"
            self.add_node(node_id, "carrier", stake=800.0)
            self.nodes[node_id].credit_score = 8.0  # 强制重置信用分
        # 添加测试用 Carrier_1, Carrier_2, Carrier_3
        for i in range(1, 4):
            node_id = f"Carrier_{i}"
            self.add_node(node_id, "carrier", stake=800.0)
            self.nodes[node_id].credit_score = 8.0  # 确保信用分正常
        
        # 添加商家节点
        for i in range(2):
            node_id = f"Merchant_{i+1}"
            self.add_node(node_id, "merchant", stake=300.0)
    
    def add_node(self, node_id: str, node_type: str, 
                stake: float = 0.0, location: str = "") -> None:
        """添加新节点"""
        if node_id not in self.nodes:
            self.nodes[node_id] = Node(
                id=node_id,
                node_type=node_type,
                stake=stake,
                location=location
            )
    
    def add_transaction(self, transaction: Dict[str, Any]) -> int:
        """添加新交易到待处理池"""
        self.pending_transactions.append({
            **transaction,
            "timestamp": time.time()
        })
        return self.get_last_block().index + 1
    
    def mine_pending_transactions(self, miner_node_id: str) -> Optional[Block]:
        if not self.pending_transactions:
            return None
        
        if miner_node_id not in self.nodes:
            raise ValueError("Invalid miner node ID")
        
        print("Debug: Pending transactions:", self.pending_transactions)  # 添加调试
        
        last_block = self.get_last_block()
        new_block = Block(
            index=last_block.index + 1,
            timestamp=time.time(),
            transactions=self.pending_transactions.copy(),
            previous_hash=last_block.hash
        )
        
        # 工作量证明
        new_block = self.proof_of_work(new_block)
        
        # 添加挖矿奖励交易
        reward_transaction = {
            "type": "mining_reward",
            "miner": miner_node_id,
            "amount": self.get_mining_reward(),
            "timestamp": time.time()
        }
        new_block.transactions.append(reward_transaction)
        
        # 更新节点最后活动时间
        self.nodes[miner_node_id].last_active = time.time()
        
        # 将新区块添加到链上
        self.chain.append(new_block)
        
        # 清空待处理交易池
        self.pending_transactions = []
        
        return new_block
    
    def proof_of_work(self, block: Block) -> Block:
        """
        工作量证明
        
        Args:
            block: 待挖掘区块
            
        Returns:
            完成工作量证明的区块
        """
        block.nonce = 0
        calculated_hash = block.calculate_hash()
        
        while not calculated_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            calculated_hash = block.calculate_hash()
        
        block.hash = calculated_hash
        return block
    
    def get_mining_reward(self) -> float:
        """计算挖矿奖励"""
        base_reward = 10.0
        # 根据链长度调整奖励
        return base_reward * (0.95 ** (len(self.chain) // 100))
    
    def is_chain_valid(self) -> bool:
        """验证区块链的有效性"""
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]
            
            # 验证当前区块哈希
            if current_block.hash != current_block.calculate_hash():
                return False
            
            # 验证区块链接
            if current_block.previous_hash != previous_block.hash:
                return False
        
        return True
    
    def get_last_block(self) -> Block:
        """获取最后一个区块"""
        return self.chain[-1]
    
    def get_node_balance(self, node_id: str) -> float:
        """获取节点代币余额"""
        if node_id not in self.nodes:
            return 0.0
            
        balance = self.nodes[node_id].stake
        
        # 遍历所有区块的交易
        for block in self.chain:
            for tx in block.transactions:
                if tx["type"] == "mining_reward" and tx["miner"] == node_id:
                    balance += tx["amount"]
                elif tx["type"] == "transfer":
                    if tx.get("from") == node_id:
                        balance -= tx.get("amount", 0)
                    if tx.get("to") == node_id:
                        balance += tx.get("amount", 0)
        
        return balance
    
    def get_node_credit_score(self, node_id: str) -> float:
        """获取节点信用分"""
        if node_id not in self.nodes:
            return 0.0
        return self.nodes[node_id].credit_score
    
    def update_node_credit_score(self, node_id: str, 
                               score_change: float) -> None:
        """更新节点信用分"""
        if node_id in self.nodes:
            self.nodes[node_id].credit_score = max(0.0, min(10.0, 
                self.nodes[node_id].credit_score + score_change))
    
    def select_super_node(self) -> Optional[str]:
        """选择超级节点（用于出块）"""
        super_nodes = [
            node_id for node_id, node in self.nodes.items()
            if node.node_type == "super_node"
        ]
        
        if not super_nodes:
            return None
            
        # 基于质押量和信用分加权选择
        weights = []
        for node_id in super_nodes:
            node = self.nodes[node_id]
            weight = node.stake * node.credit_score
            weights.append(weight)
            
        return random.choices(super_nodes, weights=weights, k=1)[0]
    
    def get_chain_stats(self) -> Dict[str, Any]:
        """获取区块链统计信息"""
        return {
            "block_count": len(self.chain),
            "transaction_count": sum(
                len(block.transactions) for block in self.chain
            ),
            "node_count": len(self.nodes),
            "super_node_count": len([
                node for node in self.nodes.values()
                if node.node_type == "super_node"
            ]),
            "average_block_time": self._calculate_average_block_time(),
            "total_stake": sum(node.stake for node in self.nodes.values())
        }
    
    def _calculate_average_block_time(self) -> float:
        """计算平均出块时间"""
        if len(self.chain) < 2:
            return 0.0
            
        total_time = self.chain[-1].timestamp - self.chain[0].timestamp
        return total_time / (len(self.chain) - 1)
    
    def get_node_transactions(self, node_id: str, 
                            limit: int = 10) -> List[Dict[str, Any]]:
        """获取节点相关的交易"""
        transactions = []
        for block in reversed(self.chain):
            for tx in block.transactions:
                if (tx.get("from") == node_id or 
                    tx.get("to") == node_id or 
                    tx.get("miner") == node_id):
                    transactions.append({
                        **tx,
                        "block_index": block.index,
                        "block_hash": block.hash
                    })
                if len(transactions) >= limit:
                    return transactions
        return transactions

# 创建全局区块链实例
blockchain = Blockchain()
