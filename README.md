# Zeru-Project
1. Introduction
This project aims to develop a system for assigning a credit score to wallets interacting with the Aave V2 decentralized finance (DeFi) protocol. The score, ranging from 0 to 1000, is based purely on historical on-chain transaction behavior. A higher score signifies reliable and responsible protocol usage, while a lower score indicates potentially risky, bot-like, or exploitative behavior.

2. Problem Statement
Given raw, transaction-level data from the Aave V2 protocol, where each record corresponds to a wallet's interaction (e.g., deposit, borrow, repay, redeemunderlying, liquidationcall), the challenge is to:

Engineer relevant features from this DeFi transaction data.

Implement a one-step script that generates wallet scores from a JSON file containing user transactions.

Validate and explain the score logic for transparency and extensibility.

3. Solution Overview
Methodology: Rule-Based Scoring
For this project, a rule-based scoring system has been implemented. While a full-fledged machine learning model (e.g., a regression model) would typically be trained on labeled data to predict scores, this rule-based approach offers immediate transparency and interpretability, aligning with the requirement to "explain the score logic." It simulates the output of an ML model by assigning weights and penalties to various behavioral features derived from transaction data.

Architecture and Processing Flow
The solution follows a straightforward, sequential processing flow:

Data Loading: The script begins by loading the raw transaction data from a specified JSON file. This file contains a comprehensive history of wallet interactions with the Aave V2 protocol.

Feature Engineering: For each unique wallet identified in the dataset, a set of meaningful features is extracted and aggregated. These features quantify various aspects of a wallet's interaction, such as total deposit volume, repayment consistency, and liquidation history.

Credit Score Assignment: Based on the engineered features, a credit score between 0 and 1000 is calculated for each wallet. This calculation uses a predefined set of weights and penalties for different behaviors.

Score Normalization: The raw scores are then normalized to fit the 0-1000 range, ensuring consistency and comparability across all wallets.

Output: The final scores for each wallet are printed to the console, sorted in descending order for easy review.

graph TD
    A[Raw Transaction JSON Data] --> B{Data Loading};
    B --> C{Feature Engineering};
    C --> D{Credit Score Assignment};
    D --> E{Score Normalization};
    E --> F[Wallet Scores (0-1000)];

4. Feature Engineering
The following features are engineered for each unique userWallet from the raw transaction data:

total_deposits_usd: Sum of all deposited amounts, converted to USD.

total_borrows_usd: Sum of all borrowed amounts, converted to USD.

total_repays_usd: Sum of all repaid amounts, converted to USD.

total_redemptions_usd: Sum of all redeemed (withdrawn) amounts, converted to USD.

num_liquidations: Count of liquidationcall actions. A critical negative indicator.

num_deposits: Total count of deposit transactions.

num_borrows: Total count of borrow transactions.

num_repays: Total count of repay transactions.

num_redemptions: Total count of redeemunderlying transactions.

num_actions: Total number of all recorded actions.

first_tx_timestamp: Unix timestamp of the wallet's earliest transaction.

last_tx_timestamp: Unix timestamp of the wallet's latest transaction.

active_days_count: The number of unique days on which the wallet performed a transaction, indicating consistent activity.

transaction_duration_days: The total duration in days from the first to the last transaction, indicating the wallet's longevity of engagement.

net_asset_flow_usd: total_deposits_usd - total_redemptions_usd. A positive value implies net assets flowing into the protocol from the wallet.

repayment_ratio: total_repays_usd / total_borrows_usd. A ratio 
ge1.0 indicates that the wallet has repaid all (or more than) its borrowed funds.

Important Note on Amount Conversion:
The amount field in the raw data is typically in wei (or similar smallest units). To convert these to human-readable USD values, the script uses a mapping of assetSymbol to its standard decimal places (e.g., USDC: 6, ETH/DAI: 18). It's crucial to ensure this asset_decimals mapping is comprehensive for all assets in the full dataset for accurate calculations.

5. Credit Score Logic Explained
The credit score is assigned using a rule-based system that combines positive and negative behavioral indicators. The final score is normalized to a range of 0 to 1000.

Base Score
Every wallet starts with a BASE_SCORE of 500. This serves as a neutral starting point.

Positive Contributions
Points are added to the raw score for behaviors indicating responsible and reliable usage:

WEIGHT_DEPOSIT (0.0001 points/USD): Rewards wallets for the total value of assets deposited.

WEIGHT_REPAY (0.0002 points/USD): Rewards wallets for the total value of assets repaid. This has a higher weight than deposits, emphasizing responsible debt management.

WEIGHT_REPAYMENT_RATIO (100 points): A significant bonus is awarded if the repayment_ratio is 
ge1.0, indicating full repayment of borrowed funds.

WEIGHT_ACTIVE_DAYS (5 points/day): Encourages consistent engagement with the protocol over time.

WEIGHT_NET_FLOW (0.00005 points/USD): Rewards wallets with a positive net asset flow (deposits > redemptions), indicating a net contribution to the protocol's liquidity.

WEIGHT_NUM_ACTIONS (0.5 points/action): A small bonus for overall activity, regardless of type, to acknowledge active participation.

Negative Contributions
Penalties are subtracted from the raw score for behaviors indicating risky or exploitative usage:

PENALTY_LIQUIDATION (300 points/liquidation): A severe penalty is applied for each liquidationcall event, as this is a strong indicator of poor risk management or failed positions.

PENALTY_BORROW_NO_REPAY (0.0001 points/USD): A penalty for any outstanding borrowed amount that has not been repaid (total_borrows_usd - total_repays_usd).

PENALTY_LOW_REPAYMENT_RATIO (200 points): A significant penalty is applied if the repayment_ratio falls below 0.5 (i.e., less than half of borrowed funds have been repaid), scaled by how far below 1.0 the ratio is.

Normalization (0-1000)
After calculating a raw score for all wallets, these scores are normalized using Min-Max scaling to fit precisely within the 0-1000 range. This ensures that the final credit score is consistent and easily comparable. The score is also clamped to ensure it doesn't go below 0 or above 1000.

6. Setup and Running the Script
Follow these steps to set up the environment and run the credit scoring script on your local machine.

Prerequisites
Python 3.8+ installed on your system.

Virtual Environment Setup
It's highly recommended to use a virtual environment to manage project dependencies.

Navigate to your project directory:
Open your terminal or command prompt and go to the folder where you plan to save your script and data.

cd path/to/your/project

Create a virtual environment:

python -m venv venv

Activate the virtual environment:

On Windows:

.\venv\Scripts\activate

On macOS/Linux:

source venv/bin/activate

Your terminal prompt should now show (venv) indicating the environment is active.

Data Download
Download the full ~87MB user-wallet-transactions.json file from the provided Google Drive link:

https://drive.google.com/file/d/1ISFbAXxadMrt7Zl96rmzzZmEKZnyW7FS/view?usp=sharing

Alternatively, the compressed zip file (~10MB):

https://drive.google.com/file/d/14ceBCLQ-BTcydDrFJauVA_PKAZ7VtDor/view?usp=sharing

Place the downloaded user-wallet-transactions.json file into your project directory (the same folder where you will save the Python script).

Modifying the Script for Local Data
The provided Python script (e.g., credit_scorer.py) needs a small adjustment to read from your local file path.

Open the credit_scorer.py file.

Locate the fetch_user_wallet_transactions_data() function.

Uncomment the lines for local file loading and comment out the content_fetcher.fetch block as shown below:

def fetch_user_wallet_transactions_data():
    try:
        # --- START LOCAL FILE LOADING MODIFICATION ---
        # UNCOMMENT the lines below for local execution:
        file_path = 'user-wallet-transactions.json' # Adjust path if your file is elsewhere
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
        # --- END LOCAL FILE LOADING MODIFICATION ---

        # # --- START CONTENT_FETCHER BLOCK (COMMENT OUT FOR LOCAL RUNS) ---
        # # This block is for execution within specific interactive environments.
        # # data_string = content_fetcher.fetch(
        # #     query="Fetch content of user wallet transactions file for processing.",
        # #     source_references=["uploaded:user-wallet-transactions.json"]
        # # )
        # # data = json.loads(data_string)
        # # return data
        # # --- END CONTENT_FETCHER BLOCK ---

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it's in the same directory as the script.", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"An unexpected error occurred while reading '{file_path}': {e}", file=sys.stderr)
        return []

Important: If your user-wallet-transactions.json file is not in the same directory as your script, adjust file_path accordingly (e.g., file_path = 'C:/path/to/your/file/user-wallet-transactions.json').

Running the Script
With the virtual environment active and the script modified, run the script from your terminal:

python credit_scorer.py

The script will process the data and print the wallet scores to your console.

7. Output
The script will output a list of wallet addresses and their assigned credit scores, sorted from highest to lowest score.

Example output:

--- Wallet Credit Scores ---
Wallet: 0xWalletAddressHighScore1... | Score: 987
Wallet: 0xWalletAddressMediumScore... | Score: 654
Wallet: 0xWalletAddressLowScore... | Score: 123
...

8. Further Analysis
After generating the scores, a deeper analysis of wallet behavior is crucial. This detailed analysis, including score distribution graphs and behavioral insights for different score ranges, will be provided in a separate file:

analysis.md

Please refer to analysis.md for:

Score distribution graphs (e.g., histograms showing counts of wallets in 0-100, 100-200, etc., ranges).

Detailed descriptions of the transaction patterns and characteristics observed in lower-scoring wallets (e.g., frequent liquidations, high borrowing with low repayment, short activity periods).

Detailed descriptions of the transaction patterns and characteristics observed in higher-scoring wallets (e.g., consistent deposits, timely and full repayments, long-term engagement, positive net asset flow).

9. Future Enhancements and Extensibility
This project provides a solid foundation, but several enhancements could be considered:

Machine Learning Model Training: Replace the rule-based system with a supervised machine learning regression model (e.g., Random Forest, Gradient Boosting) trained on a labeled dataset (if available or created). This could capture more nuanced patterns.

Dynamic Weighting: Implement a system to dynamically adjust the weights and penalties based on market conditions or protocol changes.

More Granular Features: Incorporate additional features like:

Loan-to-Value (LTV) ratios over time.

Health factor trends.

Asset-specific risk profiles.

Interaction with other DeFi protocols (if data is integrated).

Time-Series Analysis: Use time-series models to predict future behavior or identify anomalies.

Real-time Scoring: Develop an API or a streaming data pipeline for real-time credit score updates.

Comprehensive Asset Decimal Handling: Expand the asset_decimals dictionary to include a wider range of tokens and potentially fetch this information from an external API for maximum accuracy.

User Interface: Create a simple web interface to input a wallet address and display its credit score.

10. License
MIT License

Copyright (c) [Year] [Your Name or Organization]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
