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
from payment import PaymentStage
from payment import PaymentSystem
from visuals import LogisticsVisualizer
from api import calculate_distance, fetch_carbon_footprint
import api  # 导入 api 模块以设置 global_payment_system

class LogisticsApp:
    def __init__(self):
        self.visualizer = LogisticsVisualizer()
        if 'initialized' not in st.session_state:
            self._init_session_state()
        api.global_payment_system = st.session_state.payment_system  # 设置 api.py 中的全局变量
    
    def _init_session_state(self):
        st.session_state.initialized = True
        st.session_state.mode = "pseudo"
        st.session_state.testnet = TestnetLedger()
        st.session_state.bidding_system = bidding_system  # 使用全局实例
        st.session_state.token_system = token_system      # 使用全局实例
        st.session_state.payment_system = PaymentSystem()
        st.session_state.current_demand = None
        st.session_state.current_bid_id = None
        st.session_state.current_solutions = None
        st.session_state.selected_solution = None
        st.session_state.current_payment_id = None  # 初始化 current_payment_id
    
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
            st.sidebar.write(f"节点数: {stats['node_count']}")
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
                            delivery_time=delivery_time, clp_items=clp_data
                        )
                        if st.session_state.mode == "pseudo":
                            blockchain.add_transaction({"type": "demand", "data": demand})
                            blockchain.mine_pending_transactions("SuperNode_A")
                        else:
                            tx_hash = st.session_state.testnet.post_demand(demand)
                            st.info(f"需求已记录到区块链: {tx_hash}")
                        st.session_state.current_demand = demand
                        bid_id = start_bidding(demand)
                        st.session_state.current_bid_id = bid_id
                        st.success(f"需求已提交并开始竞价! 竞价ID: {bid_id}")
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
        
        # 第一轮竞价
        if bid_status["status"] == "first_round":
            if st.button("模拟第一轮竞价"):
                for i in range(3):
                    bidding_system.submit_first_round_bid(
                        st.session_state.current_bid_id, f"Carrier_{i+1}",
                        base_price=1000 + i * 200, transport_type="sea"
                    )
                # 确保进入第二轮
                success = bidding_system.start_second_round(st.session_state.current_bid_id)
                if success:
                    st.success("第一轮竞价完成，已进入第二轮")
                else:
                    st.error("无法进入第二轮竞价，可能是投标数量不足")
                st.rerun()
        
        # 第二轮竞价
        if bid_status["status"] == "second_round":
            if st.button("模拟第二轮竞价并生成方案"):
                for i in range(3):
                    success = bidding_system.submit_second_round_bid(
                        st.session_state.current_bid_id, f"Carrier_{i+1}",
                        final_price=1100 + i * 200, carbon_compensation=100
                    )
                    if not success:
                        st.error(f"Carrier_{i+1} 第二轮竞价提交失败")
                        return
                solutions = bidding_system.generate_solutions(st.session_state.current_bid_id)
                st.session_state.current_solutions = solutions
                st.success("第二轮竞价完成，方案已生成")
                st.rerun()
        
        # 方案选择
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
                payment_id = st.session_state.payment_system.create_payment(
                    selected_solution, "Merchant_1"
                )
                st.session_state.current_payment_id = payment_id
                if st.session_state.mode == "pseudo":
                    blockchain.add_transaction({"type": "solution_selected", "solution": selected_solution})
                    blockchain.mine_pending_transactions("SuperNode_A")
                else:
                    tx_hash = st.session_state.testnet.post_solution(selected_solution, payment_id)
                    st.info(f"方案已记录到区块链: {tx_hash}")
                st.success("方案已确认，支付订单已创建!")
    
    def _render_payment_tab(self):
        st.header("支付管理")
        if st.session_state.current_payment_id is None:
            st.info("请先确认一个方案")
            return
        
        payment_status = st.session_state.payment_system.get_payment_status(st.session_state.current_payment_id)
        if not payment_status:
            st.error("获取支付状态失败")
            return
        
        st.write("Debug: Payment status before rendering:", payment_status)
        st.json(payment_status)
        
        # 将 current_stage 转换为索引
        stages = ["warehouse", "customs", "transport", "delivery"]
        stage_to_index = {stage: idx for idx, stage in enumerate(stages)}
        current_stage_index = stage_to_index.get(payment_status["current_stage"], 0)
        st.write("Debug: Current stage index:", current_stage_index)
        
        # 渲染物流状态图
        fig = self.visualizer.plot_logistics_status({"current_stage": current_stage_index})
        st.pyplot(fig)
        
        if payment_status["status"] != "completed":
            if st.button("触发下一阶段支付"):
                try:
                    # 调用 advance_payment
                    success = st.session_state.payment_system.advance_payment(st.session_state.current_payment_id)
                    if success:
                        if st.session_state.mode == "pseudo":
                            blockchain.add_transaction({"type": "payment_update", "payment_id": st.session_state.current_payment_id})
                            blockchain.mine_pending_transactions("SuperNode_A")
                        else:
                            tx_hash = st.session_state.testnet.trigger_payment(
                                {"demand_id": st.session_state.current_demand["id"], 
                                 "stage": payment_status["current_stage"], "amount": payment_status["total_amount"] * 0.3}
                            )
                            st.info(f"支付更新已记录到区块链: {tx_hash}")
                        st.success("支付状态已更新!")
                        # 强制刷新页面
                        st.rerun()
                    else:
                        st.error("支付失败，请检查物流状态")
                except Exception as e:
                    st.error(f"支付触发失败，错误信息：{str(e)}")
                    raise  # 重新抛出异常以便在终端显示堆栈
    
    def _render_status_tab(self):
        st.header("系统状态")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("账本状态")
            if st.session_state.mode == "pseudo":
                stats = blockchain.get_chain_stats()
                st.write(f"区块数: {stats['block_count']}")
                st.write(f"交易数: {stats['transaction_count']}")
                st.write(f"节点数: {stats['node_count']}")
            else:
                status = st.session_state.testnet.get_network_status()
                st.write(f"网络: {status['network']}")
                st.write(f"区块高度: {status.get('block_number', 'N/A')}")
        with col2:
            st.subheader("代币系统")
            token_stats = token_system.get_stats()
            st.write(f"总发行量: {token_stats['total_supply']:.2f}")
            st.write(f"流通量: {token_stats['circulation']:.2f}")
            st.write(f"碳补偿总量: {token_stats['carbon_offset']:.2f}")
        
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