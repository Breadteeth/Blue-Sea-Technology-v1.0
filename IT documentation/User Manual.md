 ## User Manual

### 1. Overview

This user manual is designed to help you quickly install, run, and use the "Cross-Border E-Commerce Logistics Demo." This is a blockchain-based prototype for a cross-border logistics platform, offering an interactive interface via Streamlit to demonstrate the complete process of demand submission, multi-stage bidding, automated payments, and token economics. The demo primarily operates in pseudo-distributed mode, fully showcasing the project’s core innovations, making it suitable for competition judges, developers, or test users to explore.

---

### 2. System Requirements

Before starting, ensure your device meets the following requirements:
- **Operating System**: Windows, MacOS, or Linux.
- **Python Version**: 3.8 or higher (3.9 or 3.10 recommended).
- **Network**: Pseudo-distributed mode requires no real-time internet connection; for real distributed mode, access to the Ethereum Sepolia testnet is needed.
- **Browser**: A modern web browser (e.g., Chrome, Firefox) to access the Streamlit interface.

---

### 3. Installation Steps

#### 3.1 Installing Dependencies
1. Ensure Python 3.8+ is installed; check with:
   ```bash
   python --version
   ```
   or
   ```bash
   python3 --version
   ```
2. Install required Python libraries from the project root directory:
   ```bash
   pip install -r requirements.txt
   ```
   - `requirements.txt` includes all dependencies, such as `streamlit`, `matplotlib`, `web3`, etc.
   - If permission issues arise, try:
     ```bash
     pip install -r requirements.txt --user
     ```
   - If using a virtual environment, activate it first:
     ```bash
     python -m venv venv
     source venv/bin/activate  # Linux/MacOS
     venv\Scripts\activate     # Windows
     ```

#### 3.2 Running the Program
1. Launch the demo from the project directory with:
   ```bash
   streamlit run main.py
   ```
2. **Initialization Notes**:
   - Upon startup, the system runs `init_data.py`, initializing 10 simulated demands and related transactions (including bidding, payments, and token compensation).
   - Initialization generates multiple blocks and transactions (approximately 40-50 transactions, 10+ blocks), simulating multi-node collaboration and mining, so **first-time loading may take about 5 minutes**.
   - Wait patiently for terminal output like:
     ```
     Initialization completed: Generated X blocks, Y transactions, token circulation Z
     You can now view your Streamlit app in your browser.
     Local URL: http://localhost:8501
     ```
   - Once initialized, the ledger and token system are pre-populated with data for subsequent operations.
3. Open a browser and visit `http://localhost:8501` to access the demo interface.

#### 3.3 Operation Mode Notes
- **Pseudo-Distributed Mode (Default, Recommended)**:
  - Simulates a blockchain on a single machine, requiring no complex setup.
  - Fully demonstrates core innovations like multi-stage bidding, carbon emission incentives, and automated payments.
  - Ideal for quick exploration and competition demos.
- **Real Distributed Mode (Optional)**:
  - Connects to the Ethereum Sepolia testnet, requiring a configured `.env` file (including RPC URL, private key, contract address, etc.).
  - Due to complex on-chain setup and its non-focus in this demo, pseudo-distributed mode is prioritized.

---

### 4. Usage Guide

#### 4.1 Main Interface Overview
After launching, you’ll see the Streamlit interface titled “Cross-Border E-Commerce Logistics Demo,” featuring:
- **Sidebar**: System settings and status overview.
- **Main Area**: Four tabs:
  - **Demand Submission**: Submit logistics demands.
  - **Bidding Solutions**: View and select transport solutions.
  - **Payment Management**: Track payment progress.
  - **System Status**: View ledger and token statistics.

#### 4.2 Sidebar Operations
1. **Select Operation Mode**:
   - **Pseudo-Distributed Mode** (default): Single-machine simulation, recommended.
   - **Testnet Mode**: Connects to a real blockchain, requires additional setup, for extended demonstration only.
   - Pseudo-distributed mode suffices to showcase all innovations without needing testnet functionality.
2. **Status Overview**:
   - Displays block count, active node count, token circulation, and total carbon compensation.

#### 4.3 Demand Submission
1. Go to the “Demand Submission” tab.
2. Fill out the form:
   - **Weight (kg)**: e.g., 1000.
   - **Volume (m³)**: e.g., 5.
   - **Origin**: e.g., “Shanghai”.
   - **Destination**: e.g., “Singapore”.
   - **Expected Timeliness**: e.g., “Standard (5-7 days)”.
   - **Cargo Type**: e.g., “General cargo”.
   - **CLP Info**: JSON-formatted container load plan, e.g.:
     ```json
     [
       {"name": "Sample Item", "quantity": 100, "weight": 10, "volume": 0.05, "category": "General cargo", "dangerous": false}
     ]
     ```
3. Click “Submit Demand”:
   - System validates CLP and generates STU.
   - Automatically simulates bidding by 3 carriers (Carrier_1, Carrier_2, Carrier_3), generates solutions, and triggers payment.
   - Displays success message and current block count.

#### 4.4 Bidding Solutions
1. Go to the “Bidding Solutions” tab.
2. Check bidding status:
   - Without a submitted demand, it prompts “Please submit a logistics demand first.”
   - After submission, it shows stages (initial, secondary, or completed).
3. Operate bidding process: (Now automated after version updates; simply view solutions in the tab)
   - **Initial Bidding**: Click “Simulate First Round Bidding” to proceed to secondary.
   - **Secondary Bidding**: Click “Simulate Second Round Bidding and Generate Solutions” to produce cost-effective, green, and balanced solutions.
4. Select a solution:
   - Displays a solution table (price, carbon emissions, timeliness) and comparison chart.
   - Choose a solution (e.g., “Solution 1: economic”) and click “Confirm Solution” to create a payment order.

#### 4.5 Payment Management
1. Go to the “Payment Management” tab.
2. Check payment status:
   - Without a confirmed solution, it prompts “Please confirm a solution first.”
   - After order creation, it shows payment details (JSON format).
3. Progress payments:
   - Displays logistics status chart (from “warehouse” to “delivery”).
   - Click “Trigger Next Stage Payment” to simulate stage progression (e.g., “warehouse” to “customs”).
   - System updates status, transfers tokens, and generates a new block.

#### 4.6 System Status
1. Go to the “System Status” tab.
2. View statistics:
   - **Ledger Status**: Block count, transaction count, active node count.
   - **Token System**: Issuance, circulation, total carbon compensation.
   - **Node Credit Scores**: Ratings for key nodes.
3. View visualizations:
   - **Token Flow**: Network graph of the last 10 transactions.
   - **Carbon Emission Analysis**: Box plots and histograms of emissions and compensation.

---

### 5. Sample Operation Workflow

#### 5.1 Full Experience Workflow
1. Run `streamlit run main.py`, wait ~5 minutes for initialization, then visit `http://localhost:8501`.
2. In “Demand Submission,” enter:
   - Weight: 1000 kg
   - Volume: 5 m³
   - Origin: Shanghai
   - Destination: Singapore
   - Timeliness: Standard (5-7 days)
   - Cargo Type: General cargo
   - CLP:
     ```json
     [{"name": "Test Goods", "quantity": 50, "weight": 20, "volume": 0.1, "category": "General cargo", "dangerous": false}]
     ```
3. Click “Submit Demand” and wait for the prompt.
4. Go to “Bidding Solutions,” select and confirm a solution.
5. Go to “Payment Management,” click “Trigger Next Stage Payment” multiple times to observe progression.
6. Go to “System Status,” review statistics and charts.

---

### 6. Frequently Asked Questions (FAQ)

#### Q1: Why doesn’t the interface appear after startup?
- **A**:
  - First-time runs initialize 10 demands and transactions, taking ~5 minutes; wait for the terminal to show “Local URL.”
  - Ensure Python version and dependencies are correctly installed.

#### Q2: Why does CLP validation fail?
- **A**:
  - Verify JSON format is correct.
  - Check total weight ≤ 28,000 kg and total volume ≤ 67.7 m³.

#### Q3: Why can’t payments progress?
- **A**:
  - Confirm a solution is selected and an order created.
  - In pseudo-distributed mode, logistics status syncs automatically.

#### Q4: Why aren’t charts displayed?
- **A**:
  - Ensure `matplotlib` and `seaborn` are installed.
  - Refresh the page or restart the program.

---

### 7. User Insights and Benefits

Through a full demo experience, you’ll gain the following insights and valuable information:
- **Potential of Disintermediation**: Learn how multi-stage bidding and automated payments eliminate traditional freight forwarders, reducing logistics costs.
- **Green Logistics Incentives**: Observe how carbon compensation via token economics encourages eco-friendly transport choices, reducing per-unit emissions.
- **Blockchain Transparency**: The pseudo-distributed ledger records every step, demonstrating how distributed technology boosts trust and efficiency.
- **Payment-Logistics Linkage**: Experience real-time binding of payments to logistics milestones (e.g., warehousing, customs), understanding future trends in smart payments.
- **Visualization Insights**: Use solution comparison charts and token flow networks to intuitively grasp trade-offs between price, carbon emissions, and timeliness, as well as token economy dynamics.
- **Simplicity of Innovation**: Pseudo-distributed mode showcases core ideas without complex setup, offering a reference for rapid blockchain prototyping.

This demo is not just a technical showcase but an exploration of digitizing and greening the cross-border logistics industry, inspiring users to consider applying blockchain in real-world scenarios.

---

### 8. Notes

- **Initialization Time**: First run takes ~5 minutes to generate initial data; do not interrupt the process.
- **Demo Optimization**: Post-demand submission, bidding and payments complete automatically for quick demonstration.
- **Log Debugging**: Terminal outputs debug info, useful for troubleshooting.

---

