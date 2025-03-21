import random
from demand import process_demand
from bidding import bidding_system
from payment import PaymentSystem
from blockchain import blockchain
from tokens import token_system
from api import logistics_api

def initialize_demo_data(num_demands=10):
    """
    初始化 Demo 数据，模拟多个需求、竞价、支付和代币交易。
    
    Args:
        num_demands (int): 要生成的需求数量，默认 10。
    """
    # 初始化支付系统实例
    payment_system = PaymentSystem()

    # 定义一些模拟参数
    origins = ["Shanghai", "Singapore", "Bangkok"]
    destinations = ["Singapore", "Jakarta", "Ho Chi Minh"]
    cargo_types = ["普通货物", "易碎品", "冷链"]
    transport_types = ["sea", "land", "air"]

    # 为主要节点初始化代币余额
    nodes = ["SuperNode_A", "Carrier_1", "Carrier_2", "Carrier_3", "Merchant_1"]
    for node in nodes:
        token_system.init_balance(node, amount=1000.0)

    # 生成多个需求及其相关交易
    for i in range(num_demands):
        # 1. 生成随机需求
        weight = random.uniform(500, 2000)  # 重量 500-2000 kg
        volume = random.uniform(2, 10)      # 体积 2-10 m³
        origin = random.choice(origins)
        destination = random.choice(destinations)
        cargo_type = random.choice(cargo_types)
        clp_items = [
            {"name": f"Item_{i}", "quantity": 10, "weight": weight/10, 
             "volume": volume/10, "category": cargo_type, "dangerous": False}
        ]

        demand = process_demand(
            weight=weight,
            volume=volume,
            origin=origin,
            destination=destination,
            cargo_type=cargo_type,
            delivery_time="标准型 (5-7天)",
            clp_items=clp_items,
            merchant_id="Merchant_1"
        )
        blockchain.add_transaction({"type": "demand", "data": demand})
        blockchain.mine_pending_transactions("SuperNode_A")

        # 2. 模拟竞价过程
        bid_id = bidding_system.start_bidding(demand)
        
        # 第一轮竞价：3 个承运商参与
        for j, carrier in enumerate(["Carrier_1", "Carrier_2", "Carrier_3"]):
            base_price = 1000 + j * 200 + random.uniform(0, 100)  # 基础价格随机波动
            transport_type = random.choice(transport_types)
            bidding_system.submit_first_round_bid(bid_id, carrier, base_price, transport_type)
        
        # 进入第二轮竞价
        bidding_system.start_second_round(bid_id)
        for j, carrier in enumerate(["Carrier_1", "Carrier_2", "Carrier_3"]):
            final_price = 1100 + j * 200 + random.uniform(0, 50)
            carbon_compensation = random.randint(50, 150)  # 碳补偿 50-150 单位
            bidding_system.submit_second_round_bid(bid_id, carrier, final_price, carbon_compensation)
        
        # 生成解决方案
        solutions = bidding_system.generate_solutions(bid_id)
        blockchain.add_transaction({"type": "solutions_generated", "bid_id": bid_id, "solutions": solutions})
        blockchain.mine_pending_transactions("SuperNode_A")

        # 3. 创建并推进支付
        if solutions:  # 确保有解决方案
            selected_solution = solutions[0]  # 选择第一个方案（经济型）
            payment_id = payment_system.create_payment(selected_solution, "Merchant_1")
            payment_system.advance_payment(payment_id)  # 推进到第一个阶段（warehouse）
            blockchain.add_transaction({"type": "payment_created", "payment_id": payment_id})
            blockchain.mine_pending_transactions("SuperNode_A")

            # 4. 模拟碳补偿（假设在 transport 阶段触发）
            carbon_amount = selected_solution["carbon_footprint"] * 0.1  # 假设 10% 转为碳补偿
            token_system.compensate_carbon(selected_solution["carrier_id"], carbon_amount)

    # 5. 输出初始化结果
    stats = blockchain.get_chain_stats()
    token_stats = token_system.get_stats()
    print(f"初始化完成：生成 {stats['block_count']} 个区块，{stats['transaction_count']} 笔交易，"
          f"代币流通量 {token_stats['circulation']:.2f}")

if __name__ == "__main__":
    # 测试运行
    initialize_demo_data()