import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from typing import List, Dict, Any
import streamlit as st
import networkx as nx
from datetime import datetime, timedelta

class LogisticsVisualizer:
    def __init__(self):
        # 更新样式设置，使用新版本的命名方式
        sns.set_theme()  # 使用 seaborn 默认主题
        sns.set_palette("husl")
        
    @st.cache_data
    def plot_solutions(_self, solutions: List[Dict[str, Any]]) -> plt.Figure:
        """
        绘制竞价方案对比图
        
        Args:
            solutions: 竞价方案列表，每个方案包含价格、碳排放、时效等信息
            
        Returns:
            matplotlib图表对象
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 提取数据
        prices = [s['price'] for s in solutions]
        emissions = [s['carbon_footprint'] for s in solutions]
        days = [s['estimated_days'] for s in solutions]
        types = [s['type'] for s in solutions]
        
        # 左图：价格vs碳排放散点图
        scatter = ax1.scatter(prices, emissions, c=days, 
                            cmap='YlOrRd', s=100, alpha=0.6)
        ax1.set_xlabel('Price (USD)')
        ax1.set_ylabel('Carbon Emissions (kg CO2)')
        ax1.set_title('Price vs Carbon Emissions')
        
        # 添加方案标签
        for i, type_name in enumerate(types):
            ax1.annotate(type_name, (prices[i], emissions[i]), 
                        xytext=(5, 5), textcoords='offset points')
        
        # 添加颜色条（表示时效）
        plt.colorbar(scatter, ax=ax1, label='Estimated Days')
        
        # 右图：方案对比条形图
        x = range(len(solutions))
        width = 0.35
        
        # 归一化数据用于对比
        norm_prices = [p/max(prices) for p in prices]
        norm_emissions = [e/max(emissions) for e in emissions]
        norm_days = [d/max(days) for d in days]
        
        ax2.bar([i-width for i in x], norm_prices, width, label='Price', color='skyblue')
        ax2.bar(x, norm_emissions, width, label='Emissions', color='lightgreen')
        ax2.bar([i+width for i in x], norm_days, width, label='Time', color='salmon')
        
        ax2.set_ylabel('Normalized Value')
        ax2.set_title('Solution Comparison')
        ax2.set_xticks(x)
        ax2.set_xticklabels(types)
        ax2.legend()
        
        plt.tight_layout()
        return fig

    @st.cache_data
    def plot_token_flow(_self, flow_data: List[Dict[str, Any]]) -> plt.Figure:
        """
        绘制代币流动图
        
        Args:
            flow_data: 代币交易记录列表
            
        Returns:
            matplotlib图表对象
        """
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 10))
        
        # 上图：代币流动网络图
        G = nx.DiGraph()
        
        # 添加节点和边
        for tx in flow_data:
            G.add_edge(tx['from'], tx['to'], 
                      weight=tx['amount'],
                      type=tx['type'])
        
        # 设置节点位置
        pos = nx.spring_layout(G)
        
        # 绘制节点
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                             node_size=500, alpha=0.6, ax=ax1)
        
        # 绘制边（使用不同颜色表示不同类型的交易）
        edge_colors = {'transfer': 'gray', 
                      'reward': 'green',
                      'carbon_compensation': 'blue'}
                      
        for edge_type in edge_colors:
            edges = [(u, v) for (u, v, d) in G.edges(data=True) 
                    if d['type'] == edge_type]
            nx.draw_networkx_edges(G, pos, edgelist=edges, 
                                 edge_color=edge_colors[edge_type],
                                 alpha=0.6, ax=ax1)
        
        # 添加节点标签
        nx.draw_networkx_labels(G, pos, ax=ax1)
        ax1.set_title('Token Flow Network')
        
        # 下图：代币余额时间序列
        balances = {}
        timestamps = []
        
        # 计算累计余额
        for tx in sorted(flow_data, key=lambda x: x['timestamp']):
            timestamp = datetime.fromtimestamp(tx['timestamp'])
            timestamps.append(timestamp)
            
            # 更新发送方余额
            if tx['from'] not in balances:
                balances[tx['from']] = 0
            balances[tx['from']] -= tx['amount']
            
            # 更新接收方余额
            if tx['to'] not in balances:
                balances[tx['to']] = 0
            balances[tx['to']] += tx['amount']
        
        # 绘制余额变化
        for node, balance in balances.items():
            ax2.plot(timestamps, [balance]*len(timestamps), 
                    label=node, marker='o')
        
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Token Balance')
        ax2.set_title('Token Balance Changes')
        ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        ax2.grid(True)
        
        plt.tight_layout()
        return fig

    @st.cache_data
    def plot_logistics_status(_self, status: Dict[str, Any]) -> plt.Figure:
        stages = ["warehouse", "customs", "transport", "delivery"]
        current_stage = status["current_stage"]
        
        # 将字符串形式的 current_stage 映射为整数索引
        stage_to_index = {stage: idx for idx, stage in enumerate(stages)}
        current_stage_index = stage_to_index.get(current_stage, 0)  # 默认值为 0
        
        fig, ax = plt.subplots(figsize=(8, 1))
        for i, stage in enumerate(stages):
            color = 'green' if i <= current_stage_index else 'grey'  # 使用 <= 以包含当前阶段
            ax.barh(0, 1, left=i, color=color, edgecolor='black')
            ax.text(i + 0.5, 0, stage, ha='center', va='center')
        
        ax.set_xlim(0, len(stages))
        ax.set_yticks([])
        ax.set_xticks(range(len(stages)))
        ax.set_xticklabels(stages)
        ax.set_title("Logistics Status")
        return fig

    @st.cache_data
    def plot_carbon_analysis(_self, carbon_data: List[Dict[str, Any]]) -> plt.Figure:
        """
        绘制碳排放分析图表
        
        Args:
            carbon_data: 碳排放数据列表
            
        Returns:
            matplotlib图表对象
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        # 转换为DataFrame
        df = pd.DataFrame(carbon_data)
        
        # 左图：运输方式碳排放对比
        sns.boxplot(data=df, x='transport_type', y='emissions', ax=ax1)
        ax1.set_title('Carbon Emissions by Transport Type')
        ax1.set_xlabel('Transport Type')
        ax1.set_ylabel('CO2 Emissions (kg)')
        
        # 右图：碳补偿分布
        sns.histplot(data=df, x='compensation', bins=20, ax=ax2)
        ax2.set_title('Carbon Compensation Distribution')
        ax2.set_xlabel('Compensation Amount (Tokens)')
        ax2.set_ylabel('Frequency')
        
        plt.tight_layout()
        return fig
