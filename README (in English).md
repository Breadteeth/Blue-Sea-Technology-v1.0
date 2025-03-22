 # Cross-Border E-Commerce Logistics Demo

Welcome to the **Cross-Border E-Commerce Logistics Demo**, a blockchain-based prototype project aimed at revolutionizing the cross-border e-commerce logistics ecosystem in East Asia and Southeast Asia. This project leverages distributed ledger technology to optimize logistics processes, replace traditional freight forwarders, and create a transparent, efficient, and eco-friendly logistics collaboration platform. Designed for fintech competitions, the demo showcases innovative features such as multi-stage bidding, carbon emission token incentives, automated payments, and container load plan (CLP) verification, all presented through an intuitive Streamlit interface with visualization effects.

---

## Project Overview

### Project Features
This demo simulates a public blockchain platform connecting cross-border e-commerce merchants, warehousing companies, transport companies, and buyers, achieving the following through a distributed ledger:
- **Demand-Supply Matching**: A transparent multi-stage bidding system provides optimal pricing solutions.
- **Green Transport Incentives**: Token rewards based on carbon emissions promote eco-friendly transportation.
- **Automated Payments**: Payments are triggered in real-time, linked to logistics milestones (e.g., warehousing, customs clearance, delivery).
- **Distributed Records**: All operations are logged on a distributed ledger, ensuring transparency and consistency.
- **API Support**: Integrates simulated interfaces for carbon footprint, logistics status, compliance, geographic data, and exchange rates.
- **Identity Verification**: Ensures transaction authenticity via CLP signatures and node credit scores.

### Core Technical Highlights
1. **Distributed Ledger**:
   - **Pseudo-Distributed Mode**: Simulates multi-node collaboration on a single machine with Proof of Work consensus (`blockchain.py`).
   - **Real Distributed Mode**: Supports Ethereum Sepolia testnet (`testnet.py`).
2. **Decentralized Bidding**:
   - Multi-stage bidding process (initial blind auction + secondary optimization) (`bidding.py`).
   - Offers multimodal transport solutions: cost-effective, green, and balanced.
3. **Token Economy**:
   - Super nodes earn rewards for block generation (`tokens.py`).
   - Carbon emission compensation incentivizes low-emission transport.
   - Credit scoring tracks node reliability (`blockchain.py`).
4. **Smart Payments**:
   - Staged payments (warehousing 30%, customs 40%, transport 20%, delivery 10%) (`payment.py`).
   - Payments triggered by logistics milestones with compliance checks.
5. **API Simulation**:
   - Simulates carbon footprint, logistics status, compliance, distance, and exchange rate interfaces (`api.py`).
6. **CLP Verification**:
   - Uses SHA-256 hashing to verify CLP signatures for demands, bids, and payments (`demand.py`, `payment.py`).
   - Supports future ECDSA or DID extensions.
7. **Visualization**:
   - Interactive Streamlit interface (`main.py`).
   - Matplotlib charts for solution comparisons, token flow, and carbon emission analysis (`visuals.py`).

### Innovations
- **Disintermediation**: Eliminates freight forwarder intermediaries, reducing logistics costs by 18%-22%.
- **Carbon Reduction**: Ties economic incentives to carbon emissions, lowering per-unit transport emissions by 25%-30%.
- **Dual-Mode Ledger**: Balances demo simplicity (pseudo-distributed) with scalability (testnet support).
- **Enhanced Trust**: Combines API integration and CLP verification to improve compliance and authenticity.

---

## Installation and Running

### Prerequisites
- Python 3.8 or higher
- Git (for cloning the repository)
- (Optional) Ethereum Sepolia testnet account and Infura key (for real distributed mode)

### Installation Steps
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   `requirements.txt` primarily includes:
   - `streamlit`: Web interactive interface.
   - `matplotlib`, `pandas`: Data visualization and processing.
   - `web3`: Ethereum testnet interaction.
   - `requests`: API call support.
   - `cryptography`: Digital signature support.
2. **Run the Demo**:
   ```bash
   streamlit run main.py
   ```
   - Launches in pseudo-distributed mode by default; access at `http://localhost:8501`.
   - For real distributed mode, configure `testnet.py` (see below).

### Real Distributed Mode Configuration
- **Infura Key**: Register with Infura to obtain a Sepolia testnet RPC URL.
- **Ethereum Account**: Create an account, obtain a private key, and fund it with test ETH.
- **Contract Deployment**: Compile and deploy Solidity contracts using Remix, noting the address and ABI.
- **Modify `testnet.py`**:
  - Add `SEPOLIA_RPC_URL`, `PRIVATE_KEY`, `LOGISTICS_CONTRACT_ADDRESS`, and `TOKEN_CONTRACT_ADDRESS` to a `.env` file.

---

## File Structure and Functions

Below is an overview of each file’s functionality and their relationships.

### 1. `main.py`
- **Function**: Program entry point, runs the Streamlit interface, integrates all modules.
- **Input**: User inputs (demand details, mode selection).
- **Output**: STU, bidding solutions, payment status, visualization charts.
- **Implementation**: Provides interactive tabs for demand submission, bidding, payment, and system status; auto-simulates bidding and payments.
- **Relationship**: Calls all core modules to drive the full workflow.

### 2. `blockchain.py`
- **Function**: Implements a pseudo-distributed ledger, simulating multi-node collaboration.
- **Input**: Transaction data (demands, bids, payments, etc.).
- **Output**: New blocks added to the chain.
- **Implementation**: Manages a node pool (super nodes, transport companies, etc.), executes Proof of Work, tracks credit scores and balances.
- **Relationship**: Used by `demand.py`, `bidding.py`, `tokens.py`, `payment.py` to record transactions.

### 3. `demand.py`
- **Function**: Processes logistics demands, standardizes them into STU.
- **Input**: Weight, volume, origin, destination, cargo type, CLP list.
- **Output**: Demand object with STU and CLP signature.
- **Implementation**: Calculates STU (\( \max(weight/1000, volume/3) \)), verifies CLP via SHA-256, logs to ledger.
- **Relationship**: Calls `api.py` for distance, logs to `blockchain.py`.

### 4. `bidding.py`
- **Function**: Manages multi-stage bidding, generates optimized solutions.
- **Input**: Demand data, carrier bids.
- **Output**: Cost-effective, green, and balanced solutions.
- **Implementation**: Simulates initial blind auction (24 hours) and secondary optimization (30 minutes), scores based on price, emissions, and timeliness.
- **Relationship**: Calls `api.py` for carbon footprint, logs to `blockchain.py`.

### 5. `tokens.py`
- **Function**: Manages token economy, including mining rewards and carbon compensation.
- **Input**: Node ID, carbon emissions.
- **Output**: Updated balances and transaction records.
- **Implementation**: Tracks balances with a dictionary, rewards super nodes (10 tokens/block), calculates carbon compensation at 8 tokens/unit.
- **Relationship**: Logs to `blockchain.py`, uses emission data from `bidding.py`.

### 6. `payment.py`
- **Function**: Automates staged payments based on logistics milestones.
- **Input**: Solution data, payer ID, tracking number.
- **Output**: Payment status and amounts per stage.
- **Implementation**: Staged payments (warehousing 30%, customs 40%, transport 20%, delivery 10%), verifies logistics status and compliance.
- **Relationship**: Calls `api.py` for status and compliance checks, logs to `blockchain.py`.

### 7. `visuals.py`
- **Function**: Generates charts for solution comparisons, token flow, logistics status, and carbon emission analysis.
- **Input**: Solutions, token transactions, payment status, carbon data.
- **Output**: Matplotlib charts.
- **Implementation**: Plots solution scatter charts, token network graphs, logistics timelines, and carbon emission histograms.
- **Relationship**: Called by `main.py`, retrieves data from `bidding.py` and `tokens.py`.

### 8. `testnet.py`
- **Function**: Connects to Ethereum Sepolia testnet for a real distributed ledger.
- **Input**: RPC URL, private key, contract info.
- **Output**: Transaction hashes.
- **Implementation**: Logs demands, bids, and payments via `web3.py`, supports asynchronous operations.
- **Relationship**: Optionally integrated in `main.py`.

### 9. `api.py`
- **Function**: Simulates logistics-related external APIs.
- **Input**: Varies by interface (e.g., origin, tracking number).
- **Output**: Simulated data (e.g., distance, carbon footprint).
- **Implementation**: Provides random yet reasonable values, syncs logistics status with payment stages.
- **Relationship**: Called by `demand.py`, `bidding.py`, `payment.py`.

### 10. `init_data.py`
- **Function**: Initializes demo data for testing and demonstration.
- **Input**: Number of demands (default 10).
- **Output**: Populated ledger and token system.
- **Implementation**: Simulates demands, bids, payments, and token transactions.

### 11. `requirements.txt`
- **Function**: Lists project dependencies (e.g., `streamlit==1.31.0`, `web3==6.15.1`).

### 12. `README.md`
- **Function**: This document, providing project details.

---

## Workflow
1. **User Interaction (`main.py`)**: Submit a demand (e.g., 1000 kg, 5 m³, Shanghai to Singapore).
2. **Demand Processing (`demand.py`)**: Generate STU, verify CLP, log to ledger.
3. **Bidding Simulation (`bidding.py`)**: Simulate carrier bids, optimize solutions, log results.
4. **Token Operations (`tokens.py`)**: Reward super nodes, compensate carriers based on emissions.
5. **Payment Execution (`payment.py`)**: Trigger payments by logistics stages, log transactions.
6. **Visualization (`visuals.py`)**: Display solution comparisons and token flow.

---

## Technical Implementation Details

### Pseudo-Distributed Ledger
- **Purpose**: Quickly simulate distributed features without a real network.
- **Implementation**: Uses a node pool, Proof of Work (requires first 4 hash bits as 0), stores ledger in a dictionary.

### Real Distributed Ledger
- **Purpose**: Demonstrate real blockchain potential.
- **Implementation**: Connects to Sepolia testnet via `web3.py`, deploys Solidity contracts.

### API Simulation
- **Carbon Footprint**: Randomly generates emissions based on transport type and weather.
- **Logistics Status**: Global dictionary synced with payment stages.
- **Compliance**: Simplified checks based on node credit scores.

### CLP Verification
- **Current**: Verifies CLP item list with SHA-256 hashing.
- **Future**: Supports ECDSA signatures or DID integration.

---

