from typing import Dict, Any, Optional, List
import nest_asyncio
import asyncio

# 应用 nest_asyncio 来允许嵌套的事件循环
nest_asyncio.apply()

# 确保有一个事件循环在运行
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)


from web3 import Web3
from eth_account import Account
import json
import os
from datetime import datetime
import asyncio
from eth_typing import Address
from web3.middleware import geth_poa_middleware
from dotenv import load_dotenv

class TestnetLedger:
    """
    真实分布式账本实现，连接Ethereum Sepolia测试网
    用于记录跨境物流相关的交易数据，包括需求、竞价、支付等
    """
    def __init__(self):
        # 加载环境变量
        load_dotenv()
        
        # 测试网配置
        self.network = {
            "name": "sepolia",
            "rpc_url": os.getenv("SEPOLIA_RPC_URL"),
            "chain_id": 11155111,
            "explorer": "https://sepolia.etherscan.io"
        }
        
        # 合约配置
        self.contracts = {
            "logistics": {
                "address": os.getenv("LOGISTICS_CONTRACT_ADDRESS"),
                "abi_path": "contracts/LogisticsContract.json"
            },
            "token": {
                "address": os.getenv("TOKEN_CONTRACT_ADDRESS"),
                "abi_path": "contracts/TokenContract.json"
            }
        }
        
        # Web3连接
        self.w3 = None
        self.account = None
        self._initialize_connection()

    def _initialize_connection(self) -> None:
        """初始化与测试网的连接"""
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.network["rpc_url"]))
            self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            
            if not self.w3.is_connected():
                raise ConnectionError("Failed to connect to Sepolia testnet")
                
            # 设置账户
            private_key = os.getenv("PRIVATE_KEY")
            if private_key:
                self.account = self.w3.eth.account.from_key(private_key)
                
        except Exception as e:
            print(f"Testnet connection failed: {str(e)}")

    def _load_contract_abi(self, contract_type: str) -> Dict:
        """加载智能合约ABI"""
        try:
            abi_path = self.contracts[contract_type]["abi_path"]
            with open(abi_path) as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load ABI for {contract_type}: {str(e)}")
            return {}

    async def post_demand(self, demand_data: Dict[str, Any]) -> str:
        """
        发布物流需求到区块链
        
        Args:
            demand_data: 包含STU、始发地、目的地、CLP等信息的需求数据
            
        Returns:
            交易哈希
        """
        contract = self._get_contract("logistics")
        
        try:
            # 准备交易数据
            tx_data = contract.functions.postDemand(
                demand_data["stu"],
                demand_data["origin"],
                demand_data["destination"],
                Web3.to_hex(text=str(demand_data["clp"]))  # CLP数据上链
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            # 签名并发送交易
            signed_tx = self.account.sign_transaction(tx_data)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # 等待交易确认
            receipt = await self._wait_for_transaction(tx_hash)
            return receipt['transactionHash'].hex()
            
        except Exception as e:
            print(f"Failed to post demand: {str(e)}")
            return None

    async def submit_bid(self, bid_data: Dict[str, Any]) -> str:
        """
        提交竞价方案到区块链
        
        Args:
            bid_data: 包含价格、碳排放、运输方式等信息的竞价数据
            
        Returns:
            交易哈希
        """
        contract = self._get_contract("logistics")
        
        try:
            tx_data = contract.functions.submitBid(
                bid_data["demand_id"],
                bid_data["price"],
                bid_data["carbon_emission"],
                bid_data["transport_type"],
                Web3.to_hex(text=str(bid_data["clp_verification"]))  # CLP验证结果
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.account.sign_transaction(tx_data)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = await self._wait_for_transaction(tx_hash)
            return receipt['transactionHash'].hex()
            
        except Exception as e:
            print(f"Failed to submit bid: {str(e)}")
            return None

    async def trigger_payment(self, payment_data: Dict[str, Any]) -> str:
        """
        触发支付交易
        
        Args:
            payment_data: 包含金额、阶段、验证信息等的支付数据
            
        Returns:
            交易哈希
        """
        contract = self._get_contract("logistics")
        
        try:
            tx_data = contract.functions.triggerPayment(
                payment_data["demand_id"],
                payment_data["stage"],
                payment_data["amount"],
                Web3.to_hex(text=str(payment_data["verification"]))
            ).build_transaction({
                'from': self.account.address,
                'nonce': self.w3.eth.get_transaction_count(self.account.address),
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })
            
            signed_tx = self.account.sign_transaction(tx_data)
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            receipt = await self._wait_for_transaction(tx_hash)
            return receipt['transactionHash'].hex()
            
        except Exception as e:
            print(f"Failed to trigger payment: {str(e)}")
            return None

    def get_carbon_tokens(self, address: str) -> int:
        """获取地址的碳代币余额"""
        contract = self._get_contract("token")
        try:
            return contract.functions.balanceOf(address).call()
        except Exception as e:
            print(f"Failed to get token balance: {str(e)}")
            return 0

    def get_transaction_history(self, address: Optional[str] = None) -> List[Dict]:
        """获取交易历史"""
        if not address:
            address = self.account.address
            
        try:
            # 获取最近100个区块的交易
            end_block = self.w3.eth.block_number
            start_block = max(0, end_block - 100)
            
            transactions = []
            for block_num in range(start_block, end_block + 1):
                block = self.w3.eth.get_block(block_num, full_transactions=True)
                for tx in block.transactions:
                    if tx['to'] == address or tx['from'] == address:
                        transactions.append({
                            'hash': tx['hash'].hex(),
                            'from': tx['from'],
                            'to': tx['to'],
                            'value': self.w3.from_wei(tx['value'], 'ether'),
                            'block': block_num,
                            'timestamp': block.timestamp
                        })
            return transactions
            
        except Exception as e:
            print(f"Failed to get transaction history: {str(e)}")
            return []

    def _get_contract(self, contract_type: str):
        """获取合约实例"""
        if contract_type not in self.contracts:
            raise ValueError(f"Unknown contract type: {contract_type}")
            
        address = self.contracts[contract_type]["address"]
        abi = self._load_contract_abi(contract_type)
        
        return self.w3.eth.contract(
            address=self.w3.to_checksum_address(address),
            abi=abi
        )

    async def _wait_for_transaction(self, tx_hash: str) -> Dict:
        """等待交易确认"""
        while True:
            try:
                receipt = self.w3.eth.get_transaction_receipt(tx_hash)
                if receipt:
                    return receipt
            except Exception:
                pass
            await asyncio.sleep(1)

    def get_network_status(self) -> Dict[str, Any]:
        """获取网络状态"""
        try:
            return {
                "network": self.network["name"],
                "connected": self.w3.is_connected() if self.w3 else False,
                "block_number": self.w3.eth.block_number if self.w3 else 0,
                "gas_price": self.w3.from_wei(self.w3.eth.gas_price, 'gwei') if self.w3 else 0,
                "account": self.account.address if self.account else None
            }
        except Exception as e:
            # 确保即使在出错时也返回包含所有必要键的字典
            return {
                "network": self.network["name"],  # 使用配置中的网络名称
                "connected": False,
                "block_number": 0,
                "gas_price": 0,
                "account": None,
                "error": str(e)
            }