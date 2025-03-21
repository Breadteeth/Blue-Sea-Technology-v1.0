import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from typing import Dict, Any, List
import json

from blockchain import blockchain
from testnet import TestnetLedger
from demand import process_demand, validate_clp
from bidding import start_bidding, get_bid_status, bidding_system
from tokens import token_system
from payment import PaymentStage, PaymentSystem
from visuals import LogisticsVisualizer
from api import calculate_distance, fetch_carbon_footprint, global_payment_system
from init_data import initialize_demo_data  # 引入初始化数据模块

class LogisticsApp:
    def __init__(self):
        self.visualizer = LogisticsVisualizer()
        if 'initialized' not in st.session_state:
            self._init_session_state()
            initialize_demo_data(num_demands=10)
        import api  # 确保 api 模块已导入
        api.global_payment_system = st.session_state.payment_system  # 修复赋值，确保 api.py 能访问
    
    def _init_session_state(self):
        st.session_state.initialized = True
        st.session_state.mode = "pseudo"
        st.session_state.testnet = TestnetLedger()
        st.session_state.bidding_system = bidding_system
        st.session_state.token_system = token_system
        st.session_state.payment_system = PaymentSystem()
        st.session_state.current_demand = None
        st.session_state.current_bid_id = None
        st.session_state.current_solutions = None
        st.session_state.selected_solution = None
        st.session_state.current_payment_id = None
    
    def run(self):
        st.title("跨境电商物流Demo")
        self._render_sidebar()
        tab1, tab2, tab3, tab4 = st.tabs(["需求发布", "竞价方案", "支付管理", "系统状态"])
        
        with tab1:
            self._render_demand_tab()
        with tab2:
            self._render_bidding_tab()
        with tab3:
            self._render_payment_tab()
        with tab4:
            self._render_status_tab()
    
    def _render_sidebar(self):
        st.sidebar.title("系统设置")
        mode = st.sidebar.selectbox(
            "选择运行模式",
            ["伪分布式模式", "测试网模式"],
            index=0 if st.session_state.mode == "pseudo" else 1
        )
        st.session_state.mode = "pseudo" if mode == "伪分布式模式" else "testnet"
        
        if st.session_state.mode == "pseudo":
            stats = blockchain.get_chain_stats()
            st.sidebar.write(f"区块数: {stats['block_count']}")
            st.sidebar.write(f"活跃节点数: {len(blockchain.get_active_nodes())}")  # 修改为活跃节点数
        else:
            status = st.session_state.testnet.get_network_status()
            st.sidebar.write(f"网络: {status['network']}")
            st.sidebar.write(f"区块高度: {status.get('block_number', 'N/A')}")
        
        token_stats = token_system.get_stats()
        st.sidebar.write("---")
        st.sidebar.write("代币系统状态")
        st.sidebar.write(f"流通量: {token_stats['circulation']:.2f}")
        st.sidebar.write(f"碳补偿总量: {token_stats['carbon_offset']:.2f}")
    
    def _render_demand_tab(self):
        st.header("物流需求发布")
        with st.form("logistics_demand"):
            col1, col2 = st.columns(2)
            with col1:
                weight = st.number_input("重量 (kg)", min_value=0.1, value=1000.0)
                origin = st.text_input("始发地", value="Shanghai")
                delivery_time = st.selectbox(
                    "期望时效",
                    ["标准型 (5-7天)", "加急型 (3天)", "超急型 (24小时)"]
                )
            with col2:
                volume = st.number_input("体积 (m³)", min_value=0.1, value=5.0)
                destination = st.text_input("目的地", value="Singapore")
                cargo_type = st.selectbox(
                    "货物类型",
                    ["普通货物", "易碎品", "冷链", "危险品"]
                )
            st.subheader("CLP信息")
            clp_items = st.text_area(
                "输入CLP物品列表 (JSON格式)",
                value=json.dumps([
                    {"name": "Sample Item", "quantity": 100, "weight": 10, 
                     "volume": 0.05, "category": "普通货物", "dangerous": False}
                ], indent=2, ensure_ascii=False)
            )
            submitted = st.form_submit_button("提交需求")
            
            if submitted:
                try:
                    clp_data = json.loads(clp_items)
                    if validate_clp(clp_data):
                        demand = process_demand(
                            weight=weight, volume=volume, origin=origin,
                            destination=destination, cargo_type=cargo_type,
                            delivery_time=delivery_time, clp_items=clp_data,
                            merchant_id="Merchant_1"
                        )
                        blockchain.add_transaction({"type": "demand", "data": demand})
                        blockchain.mine_pending_transactions("SuperNode_A")
                        
                        # 修复：存储 current_demand
                        st.session_state.current_demand = demand
                        
                        # 单次操作放大：模拟 3 个承运商竞价
                        st.info("正在模拟竞价：Carrier_1, Carrier_2, Carrier_3...")
                        bid_id = start_bidding(demand)
                        for i in range(3):
                            bidding_system.submit_first_round_bid(
                                bid_id, f"Carrier_{i+1}", 1000 + i * 200, "sea"
                            )
                        bidding_system.start_second_round(bid_id)
                        for i in range(3):
                            bidding_system.submit_second_round_bid(
                                bid_id, f"Carrier_{i+1}", 1100 + i * 200, 100
                            )
                        solutions = bidding_system.generate_solutions(bid_id)
                        st.session_state.current_solutions = solutions
                        st.session_state.current_bid_id = bid_id
                        
                        # 自动触发支付
                        if solutions:
                            payment_id = st.session_state.payment_system.create_payment(solutions[0], "Merchant_1")
                            st.session_state.payment_system.advance_payment(payment_id)
                            st.session_state.current_payment_id = payment_id
                            blockchain.add_transaction({"type": "payment_created", "payment_id": payment_id})
                            blockchain.mine_pending_transactions("SuperNode_A")
                            st.success(f"需求已提交，竞价完成，支付已触发！区块数: {blockchain.get_chain_stats()['block_count']}")
                        else:
                            st.error("生成解决方案失败")
                    else:
                        st.error("CLP验证失败!")
                except Exception as e:
                    st.error(f"处理需求时出错: {str(e)}")
    
    def _render_bidding_tab(self):
        st.header("竞价方案")
        if st.session_state.current_demand is None or st.session_state.current_bid_id is None:
            st.info("请先提交物流需求")
            return
        
        bid_status = get_bid_status(st.session_state.current_bid_id)
        if not bid_status:
            st.error("获取竞价状态失败")
            return
        
        st.write("竞价状态:", bid_status["status"])
        
        if bid_status["status"] == "first_round":
            if st.button("模拟第一轮竞价"):
                for i in range(3):
                    bidding_system.submit_first_round_bid(
                        st.session_state.current_bid_id, f"Carrier_{i+1}",
                        base_price=1000 + i * 200, transport_type="sea"
                    )
                bidding_system.start_second_round(st.session_state.current_bid_id)
                st.success("第一轮竞价完成，已进入第二轮")
                st.rerun()
        
        if bid_status["status"] == "second_round":
            if st.button("模拟第二轮竞价并生成方案"):
                for i in range(3):
                    bidding_system.submit_second_round_bid(
                        st.session_state.current_bid_id, f"Carrier_{i+1}",
                        final_price=1100 + i * 200, carbon_compensation=100
                    )
                solutions = bidding_system.generate_solutions(st.session_state.current_bid_id)
                st.session_state.current_solutions = solutions
                st.success("第二轮竞价完成，方案已生成")
                st.rerun()
        
        if bid_status["status"] == "completed" and st.session_state.current_solutions:
            df = pd.DataFrame(st.session_state.current_solutions)
            df['route'] = df['route'].apply(lambda r: f"{r['origin']} -> {r['destination']} ({r['transport_type']})")
            st.dataframe(df)
            fig = self.visualizer.plot_solutions(st.session_state.current_solutions)
            st.pyplot(fig)
            selected_index = st.selectbox(
                "选择方案",
                range(len(st.session_state.current_solutions)),
                format_func=lambda x: f"方案 {x+1}: {st.session_state.current_solutions[x]['type']}"
            )
            if st.button("确认方案"):
                selected_solution = st.session_state.current_solutions[selected_index]
                st.session_state.selected_solution = selected_solution
                payment_id = st.session_state.payment_system.create_payment(selected_solution, "Merchant_1")
                st.session_state.current_payment_id = payment_id
                blockchain.add_transaction({"type": "solution_selected", "solution": selected_solution})
                blockchain.mine_pending_transactions("SuperNode_A")
                st.success(f"方案已确认，支付订单已创建！奖励: {blockchain.get_mining_reward():.2f} 代币")
    
    def _render_payment_tab(self):
        st.header("支付管理")
        if st.session_state.current_payment_id is None:
            st.info("请先确认一个方案")
            return
        
        payment_status = st.session_state.payment_system.get_payment_status(st.session_state.current_payment_id)
        if not payment_status:
            st.error("获取支付状态失败")
            return
        
        st.json(payment_status)
        stages = ["warehouse", "customs", "transport", "delivery"]
        current_stage = payment_status["current_stage"].strip()
        current_stage_index = stages.index(current_stage) if current_stage in stages else 0
        fig = self.visualizer.plot_logistics_status({"current_stage": current_stage_index})
        st.pyplot(fig)
        
        if payment_status["status"] != "completed":
            if st.button("触发下一阶段支付"):
                success = st.session_state.payment_system.advance_payment(st.session_state.current_payment_id)
                if success:
                    # 新增：触发代币转账和碳补偿
                    payment_id = st.session_state.current_payment_id
                    payment = st.session_state.payment_system.payments[payment_id]
                    payer_id = payment["payer_id"]  # "Merchant_1"
                    carrier_id = payment["carrier_id"]  # e.g., "Carrier_1"
                    stage_amount = payment["stage_amounts"][payment["current_stage"]]
                    
                    # 代币转账：从 payer 到 carrier
                    token_system.transfer(payer_id, carrier_id, stage_amount, tx_type="payment")
                    
                    # 碳补偿：基于解决方案中的 carbon_compensation
                    solution = payment["solution"]
                    carbon_amount = solution.get("carbon_compensation", 100) / len(stages)  # 分摊到每个阶段
                    token_system.compensate_carbon(carrier_id, carbon_amount)
                    
                    # 上链记录
                    blockchain.add_transaction({"type": "payment_update", "payment_id": payment_id})
                    blockchain.mine_pending_transactions("SuperNode_A")
                    st.success(f"支付状态已更新！新区块生成，奖励: {blockchain.get_mining_reward():.2f} 代币")
                    st.rerun()
                else:
                    st.error("支付失败，请检查物流状态")
    
    def _render_status_tab(self):
        st.header("系统状态")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("账本状态")
            stats = blockchain.get_chain_stats()
            st.write(f"区块数: {stats['block_count']} (+{stats['block_count'] - 1} 自启动)")
            st.write(f"交易数: {stats['transaction_count']}")
            st.write(f"活跃节点数: {len(blockchain.get_active_nodes())}")
        with col2:
            st.subheader("代币系统")
            token_stats = token_system.get_stats()
            st.write(f"总发行量: {token_stats['total_supply']:.2f}")
            st.write(f"流通量: {token_stats['circulation']:.2f}")
            st.write(f"碳补偿总量: {token_stats['carbon_offset']:.2f}")
        
        # 信用分展示
        st.subheader("节点信用分")
        credit_data = [
            {"节点": n, "信用分": blockchain.get_node_credit_score(n)}
            for n in ["SuperNode_A", "Carrier_1", "Carrier_2", "Merchant_1"]
        ]
        st.table(credit_data)
        
        st.subheader("代币流动")
        flow_data = token_system.get_flow_data()
        fig = self.visualizer.plot_token_flow(flow_data)
        st.pyplot(fig)
        
        st.subheader("碳排放分析")
        carbon_data = token_system.get_carbon_data()
        fig = self.visualizer.plot_carbon_analysis(carbon_data)
        st.pyplot(fig)

if __name__ == "__main__":
    app = LogisticsApp()
    app.run()