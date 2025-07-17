# Aave V2 Wallet Credit Scoring System

This project implements a transparent, rule-based credit scoring system for wallets interacting with the Aave V2 DeFi protocol. The score, ranging from **0 to 1000**, reflects a wallet’s historical behavior — rewarding responsible usage and penalizing risky or exploitative patterns.

---

## 📌 Table of Contents

- [1. Overview](#1-overview)
- [2. Problem Statement](#2-problem-statement)
- [3. Solution Architecture](#3-solution-architecture)
- [4. Feature Engineering](#4-feature-engineering)
- [5. Scoring Logic](#5-scoring-logic)
- [6. Setup Instructions](#6-setup-instructions)
- [7. Running the Script](#7-running-the-script)
- [8. Sample Output](#8-sample-output)
- [9. Further Analysis](#9-further-analysis)
- [10. Future Enhancements](#10-future-enhancements)
- [11. License](#11-license)

---

## 1. Overview

This project assigns a **credit score (0-1000)** to wallets using **Aave V2** based on their **on-chain historical transaction behavior**. It is a **rule-based**, interpretable scoring method.

---

## 2. Problem Statement

Given raw, transaction-level data from the Aave V2 protocol:

- 🧠 Engineer relevant features per wallet  
- ⚙️ Implement a scoring script from JSON input  
- 📊 Ensure transparent, explainable logic for the scores  

---

## 🧱 Solution Architecture

```mermaid
graph TD
    A[Raw Transaction JSON Data] --> B[Data Loading]
    B --> C[Feature Engineering]
    C --> D[Credit Score Assignment]
    D --> E[Score Normalization]
    E --> F[Wallet Scores]



---

## 📘 Rule-Based Scoring Overview

- **Rule-Based Scoring**: Uses behavioral heuristics instead of a trained model.
- **Transparent Logic**: Clear weightage for every behavior.
- **One-Step Execution**: Just provide the JSON file and run the script.

---

## 🧠 Feature Engineering

Each wallet is evaluated using the following features:

| Feature | Description |
|--------|-------------|
| `total_deposits_usd` | Sum of all deposits |
| `total_borrows_usd` | Sum of all borrows |
| `total_repays_usd` | Sum of all repayments |
| `total_redemptions_usd` | Total withdrawn amount |
| `num_liquidations` | Count of liquidation events |
| `num_actions` | Total number of interactions |
| `repayment_ratio` | Ratio of repaid to borrowed funds |
| `active_days_count` | Number of unique active days |
| `net_asset_flow_usd` | Deposits minus redemptions |
| `first_tx_timestamp` | First interaction timestamp |
| `last_tx_timestamp` | Last interaction timestamp |
| `transaction_duration_days` | Time span between first and last interaction |

> **Note:** Amounts are converted from smallest units (e.g., wei) to USD using an `asset_decimals` mapping.

---

## 🧮 Scoring Logic

### 🔹 Base Score

- All wallets start with a base score of **500**

### ✅ Positive Indicators

| Behavior | Weight |
|----------|--------|
| Deposit Volume | +0.0001 pts/USD |
| Repay Volume | +0.0002 pts/USD |
| Repayment Ratio ≥ 1.0 | +100 pts |
| Active Days | +5 pts per day |
| Net Asset Flow | +0.00005 pts/USD |
| Total Actions | +0.5 pts per action |

### ❌ Negative Indicators

| Behavior | Penalty |
|----------|---------|
| Liquidation Event | -300 pts each |
| Unrepaid Borrowing | -0.0001 pts/USD |
| Repayment Ratio < 0.5 | -200 pts (scaled) |

### 📏 Normalization

- Final scores are normalized to the **0–1000** range using **Min-Max scaling**.
- Clamped to stay within the bounds of 0 and 1000.

---

## ⚙️ Setup Instructions

### 📦 Prerequisites

- Python **3.8+** installed

### 📁 Download Dataset

Download the raw data file:  
➡️ [user-wallet-transactions.json (~87MB)](https://drive.google.com/file/d/1ISFbAXxadMrt7Zl96rmzzZmEKZnyW7FS/view?usp=sharing)

Place it in your project directory.

---

### 🛠️ Virtual Environment Setup

```bash
cd path/to/your/project
python -m venv venv
