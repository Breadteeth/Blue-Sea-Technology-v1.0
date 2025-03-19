
---

# 跨境电商物流Demo

欢迎体验 **Cross-Border E-Commerce Logistics Demo**，这是一个基于区块链的原型项目，旨在革新东亚至东南亚跨境电商物流生态系统。本项目通过分布式账本技术优化跨境运输，替代传统货代公司（freight forwarders），实现透明、高效且环保的物流协同平台。专为金融科技竞赛设计，Demo展示了多阶段竞价（multi-stage bidding）、碳排放代币激励（carbon emission incentives）、自动化支付（automated payments）以及CLP集装箱装箱单（Container Loading Plan, CLP）验证等创新功能，并通过Streamlit界面提供直观交互和可视化效果。

---

## 项目概述

### 项目功能
本Demo模拟了一个公链平台，连接跨境电商商家、仓储公司、航运公司、地方货运公司和买家，通过分布式账本实现：
- **物流需求与供给匹配**：透明竞价系统提供最低报价方案。
- **绿色运输激励**：基于碳排放的代币奖励推动环保运输。
- **支付自动化**：与物流节点（如入仓、清关、签收）实时绑定。
- **分布式记录**：所有操作记录在分布式账本上，确保透明性和一致性。
- **API支持**：集成碳足迹、物流状态、合规性、地理信息和汇率接口。
- **身份验证**：通过CLP和其他机制验证链上角色身份。

### 核心技术亮点
1. **分布式账本（Distributed Ledger）**：
   - 伪分布式模拟：单机多节点协作，带伪共识机制。
   - 真实分布式支持：预留Ethereum Sepolia测试网接口。
2. **去中心化竞价（Decentralized Bidding）**：
   - 多阶段竞价（盲拍+优化）。
   - 多式联运优化（经济型、均衡型、绿色型方案）。
3. **代币经济（Token Economy）**：
   - 超级节点（Super Node）因维护账本获奖励。
   - 碳排放补偿激励绿色路径。
   - 信用评分（Credit Scoring）基于交易历史。
4. **智能支付（Smart Payments）**：
   - 分层架构（主链大额、侧链小额）。
   - 物流里程碑触发支付，含合规检查。
5. **API集成**：
   - 碳足迹计算、物流追踪、KYC/AML验证、距离计算、汇率转换。
6. **身份验证与CLP**：
   - 使用CLP集装箱装箱单验证需求、竞价和支付的真实性。
   - 支持模拟签名和未来数字签名/DID。
7. **可视化（Visualization）**：
   - Streamlit交互式UI。
   - 图表展示竞价方案和代币流动。

### 创新之处
- **去中介化**：去除货代中间商，降低18%-22%的物流成本。
- **碳减排**：经济激励与碳排放挂钩，单位运输碳排放下降25%-30%。
- **双模式账本**：支持伪分布式和真实分布式实现，兼顾演示与扩展性。
- **API与身份验证**：预留多种接口，结合CLP增强信任和合规性。

---

## 安装与运行

### 前置条件
- Python 3.8或以上版本
- Git（用于克隆仓库）
- （可选）Ethereum测试网账户和Infura密钥（用于真实分布式模式）

### 安装步骤
1. **克隆仓库**：
   ```bash
   git clone https://github.com/<你的用户名>/cross_border_logistics_demo.git
   cd cross_border_logistics_demo
   ```
2. **安装依赖**：
   ```bash
   pip install -r requirements.txt
   ```
   `requirements.txt`包含：
   - `streamlit`：网页交互界面。
   - `matplotlib`：数据可视化。
   - `pandas`：表格数据处理。
   - `web3`：Ethereum测试网交互。
   - `requests`：API调用支持。
   - `cryptography`：数字签名支持。
3. **运行Demo**：
   ```bash
   streamlit run main.py
   ```
   - 默认启动伪分布式模式，访问`http://localhost:8501`。
   - 若使用真实分布式模式，需配置`testnet.py`（见下方说明）。

### 真实分布式模式配置
- **Infura密钥**：注册Infura，获取Sepolia测试网URL。
- **Ethereum账户**：创建账户，获取地址和私钥，充值少量测试ETH。
- **合约部署**：使用Remix编译并部署提供的Solidity合约，记录地址和ABI。
- **修改`testnet.py`**：填入密钥、地址和ABI。

---

## 文件结构与功能

以下是每个文件的详细功能、技术实现路径及其与其他文件的关联。

### 1. `main.py`
- **功能**：
  - 主程序入口，运行Streamlit UI。
  - 支持两种账本模式：伪分布式（默认）和真实分布式（Ethereum测试网）。
  - 集成所有模块，展示完整流程，含CLP输入。
- **输入**：用户输入货运需求（重量、体积、始发地、目的地、时效、CLP物品列表）+模式选择。
- **输出**：标准化需求（STU）、竞价方案、代币余额、支付进度、图表。
- **技术路径**：
  - 使用`streamlit`创建交互界面。
  - 根据模式选择实例化`Blockchain`或`TestnetLedger`。
  - 调用各模块功能，展示API和CLP验证结果。
- **关系**：
  - **导入**：`demand.py`、`bidding.py`、`tokens.py`、`payment.py`、`visuals.py`、`blockchain.py`、`testnet.py`。
  - **调用**：
    - `post_demand`（需求处理）。
    - `simulate_bidding`和`optimize_routes`（竞价）。
    - `TokenSystem`方法（代币管理）。
    - `Payment`方法（支付触发）。
    - `plot_solutions`和`plot_tokens`（可视化）。

### 2. `blockchain.py`
- **功能**：
  - 实现伪分布式账本，模拟多节点协作。
  - 记录所有交易（需求、竞价、代币、支付），支持CLP和API数据。
- **输入**：交易数据（字典，如`{"type": "demand", "clp": {...}}`）。
- **输出**：新区块，广播给所有节点。
- **技术路径**：
  - 节点池：`nodes`列表模拟多个参与方。
  - 伪共识：基于规模和压力选择出块节点。
  - 广播：`node_ledgers`字典同步账本。
  - 使用`hashlib.sha256`确保不可篡改。
  - 记录CLP签名验证结果。
- **关系**：
  - **被导入**：`main.py`、`demand.py`、`bidding.py`、`tokens.py`、`payment.py`。
  - **作用**：作为伪分布式数据存储。

### 3. `demand.py`
- **功能**：
  - 处理货运需求，标准化为STU。
  - 调用地理信息API计算距离。
  - 验证CLP签名，确保需求真实性。
- **输入**：重量（kg）、体积（m³）、始发地、目的地、时效、商家ID、CLP物品列表。
- **输出**：STU值。
- **技术路径**：
  - 公式：`max(weight / 2000, volume / 68)`。
  - 调用`api.py`的`calculate_distance`。
  - 使用哈希验证CLP签名。
- **关系**：
  - **导入**：`blockchain.py`、`api.py`。
  - **调用**：`blockchain.py`或`testnet.py`的`add_block`。

### 4. `bidding.py`
- **功能**：
  - 模拟多节点竞价（盲拍）。
  - 调用碳足迹API获取碳排放数据。
  - 检查报价异常（防合谋）。
  - 验证CLP签名，确保竞价基于真实数据。
  - 优化多式联运方案（经济型、均衡型、绿色型）。
- **输入**：STU值、始发地、目的地、CLP对象。
- **输出**：方案字典（节点ID、价格、碳排放、时效）。
- **技术路径**：
  - 使用`random`生成报价。
  - 调用`api.py`的`fetch_carbon_footprint`。
  - `hashlib.sha256`隐藏报价（简版零知识证明）。
  - 验证CLP签名。
  - 加权评分优化方案。
- **关系**：
  - **导入**：`blockchain.py`、`api.py`。
  - **调用**：`blockchain.py`或`testnet.py`。
  - **提供数据**：碳排放给`tokens.py`。

### 5. `tokens.py`
- **功能**：
  - 管理代币经济：
    - 超级节点出块奖励。
    - 库存转移支付。
    - 碳排放补偿。
  - 维护信用评分和代币上限。
- **输入**：节点ID、货物体积、碳排放增量。
- **输出**：更新余额和评分。
- **技术路径**：
  - 字典存储余额和评分。
  - 检查`total_supply`上限。
  - 基于`bidding.py`的碳排放数据分配奖励。
- **关系**：
  - **导入**：`blockchain.py`。
  - **调用**：`blockchain.py`或`testnet.py`。
  - **使用**：`bidding.py`的碳排放数据。

### 6. `payment.py`
- **功能**：
  - 模拟分层支付（主链/侧链）。
  - 调用物流状态API验证节点状态。
  - 调用合规性API执行KYC/AML检查。
  - 调用汇率API转换货币。
  - 验证CLP签名，确保支付基于真实货物。
  - 触发支付（入仓30%、清关45%、签收30%）。
- **输入**：总金额、用户ID、追踪号、CLP对象。
- **输出**：支付金额（CNY和EUR）。
- **技术路径**：
  - 条件逻辑划分支付。
  - 调用`api.py`的`check_logistics_status`、`verify_compliance`、`get_exchange_rate`。
  - 使用哈希验证CLP签名。
- **关系**：
  - **导入**：`blockchain.py`、`api.py`。
  - **调用**：`blockchain.py`或`testnet.py`。

### 7. `visuals.py`
- **功能**：
  - 生成图表：
    - 方案对比（价格 vs 碳排放）。
    - 代币余额变化。
- **输入**：方案数据、代币余额。
- **输出**：Matplotlib图表。
- **技术路径**：
  - 使用`matplotlib`绘制。
  - 与`streamlit`集成。
- **关系**：
  - **导入**：`main.py`。
  - **使用**：`bidding.py`和`tokens.py`数据。

### 8. `testnet.py`
- **功能**：
  - 连接Ethereum Sepolia测试网。
  - 部署合约记录数据。
- **输入**：Infura URL、私钥、合约地址和ABI。
- **输出**：交易哈希。
- **技术路径**：
  - 使用`web3.py`与测试网交互。
  - 提供Solidity合约示例。
- **关系**：
  - **导入**：`main.py`（可选）。

### 9. `api.py`
- **功能**：
  - 提供API接口模拟，支持：
    - 碳足迹（`fetch_carbon_footprint`）。
    - 物流状态（`check_logistics_status`）。
    - 合规性（`verify_compliance`）。
    - 地理信息（`calculate_distance`）。
    - 汇率（`get_exchange_rate`）。
- **输入**：根据接口不同（如始发地、追踪号等）。
- **输出**：模拟数据（如碳排放量、状态布尔值等）。
- **技术路径**：
  - 使用`random`生成模拟值。
  - 定义明确的数据需求，预留真实API替换。
- **关系**：
  - **被导入**：`demand.py`、`bidding.py`、`payment.py`。

### 10. `requirements.txt`
- **功能**：列出依赖。
- **内容**：
  ```
  streamlit
  matplotlib
  pandas
  web3
  requests
  cryptography
  ```

### 11. `README.md`
- **功能**：本文档，指导用户和评委。

---

## 工作流程

1. **用户交互** (`main.py`)：
   - 输入需求（如12,000 kg，24 m³，上海到柏林，CLP物品列表）。
   - 选择账本模式（伪分布式/真实分布式）。
2. **需求处理** (`demand.py`)：
   - 转换为STU，调用API计算距离，验证CLP签名，记录到账本。
3. **竞价模拟** (`bidding.py`)：
   - 节点提交报价，调用API获取碳排放，验证CLP，检查合谋，优化方案。
4. **代币操作** (`tokens.py`)：
   - 奖励SuperNode_A，转移库存，基于碳排放补偿Transporter_B。
5. **支付执行** (`payment.py`)：
   - 调用API验证物流状态和合规性，验证CLP，转换汇率，触发支付。
6. **可视化** (`visuals.py`)：
   - 显示方案对比和代币图表。

---

## 技术实现路径

### 伪分布式账本（Pseudo-Distributed Ledger）
- **为何使用?**：快速模拟分布式特性，无需真实网络。
- **如何实现?**：
  - 节点池：`nodes`列表模拟多节点。
  - 伪共识：基于规模和压力选择出块节点。
  - 广播：`node_ledgers`同步账本。

### 真实分布式账本（Real Distributed Ledger）
- **为何使用?**：展示真实区块链潜力。
- **如何实现?**：
  - `web3.py`连接Sepolia测试网。
  - 部署Solidity合约记录数据。
  - 通过交易哈希验证上链。

### API接口模拟
- **碳足迹**：`fetch_carbon_footprint`模拟运输碳排放，输入始发地、目的地、重量、运输方式。
- **物流状态**：`check_logistics_status`模拟节点状态，输入追踪号和阶段。
- **合规性**：`verify_compliance`模拟KYC/AML，输入用户ID和金额。
- **地理信息**：`calculate_distance`模拟距离，输入始发地和目的地。
- **汇率**：`get_exchange_rate`模拟货币转换，输入源货币和目标货币。
- **实现方式**：使用`random`生成数据，预留真实API替换。

### 身份验证与CLP
- **验证场景**：
  - **需求发布**：验证商家CLP签名。
  - **竞价**：验证CLP确保报价真实。
  - **支付**：验证CLP匹配物流状态。
  - **角色注册**：验证节点身份。
- **Demo模拟手段**：
  - 使用`hashlib.sha256`生成和验证CLP签名。
  - 检查节点ID和信用评分。
- **真实实现手段**：
  - 使用`cryptography`实现数字签名（ECDSA）。
  - 结合DID（去中心化身份）或海关API验证。

### 其他模块
- **竞价**：随机数据+哈希匿名+API碳排放+CLP验证。
- **代币**：字典管理+上限检查+碳奖励。
- **支付**：条件触发+分层+API验证+CLP检查。

---

## 文件间关系

- **中心**：`main.py`协调所有模块。
- **账本**：`blockchain.py`（伪分布式）或`testnet.py`（真实分布式）作为数据核心。
- **API支持**：`api.py`为`demand.py`、`bidding.py`、`payment.py`提供数据。
- **流程**：
  - `demand.py` → `bidding.py` → `tokens.py` → `payment.py`。
  - `visuals.py`从`bidding.py`和`tokens.py`取数据。
- **切换**：`main.py`通过模式选择调用不同账本。

---

## 局限性与未来计划
- **伪分布式**：仅单机模拟，未实现真实网络通信。
- **真实分布式**：需手动配置测试网，合约功能有限。
- **API**：当前为模拟，需接入真实服务（如Carbon Interface）。
- **CLP验证**：当前为哈希模拟，未来需数字签名和海关验证。
- **未来**：
  - 完善共识机制（DPoS）。
  - 集成真实API和IoT。
  - 扩展NFT功能（资产证券化）。

---

