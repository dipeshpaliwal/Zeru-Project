import json
import math
from collections import defaultdict
from datetime import datetime
import sys

def fetch_user_wallet_transactions_data():
    try:
        file_path = 'user-wallet-transactions.json'
        with open('C:/Users/91720/Desktop/zeru internship/user-wallet-transactions.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found. Please ensure it's in the same directory as the script.", file=sys.stderr)
        return []
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from '{file_path}': {e}", file=sys.stderr)
        return []
    except Exception as e:
        print(f"An unexpected error occurred while reading '{file_path}': {e}", file=sys.stderr)
        return []

def calculate_wallet_features(transactions):
    wallet_features = defaultdict(lambda: {
        'total_deposits_usd': 0.0,
        'total_borrows_usd': 0.0,
        'total_repays_usd': 0.0,
        'total_redemptions_usd': 0.0,
        'num_liquidations': 0,
        'num_deposits': 0,
        'num_borrows': 0,
        'num_repays': 0,
        'num_redemptions': 0,
        'num_actions': 0,
        'first_tx_timestamp': float('inf'),
        'last_tx_timestamp': 0,
        'active_days': set()
    })

    for tx in transactions:
        wallet = tx.get('userWallet')
        if not wallet:
            continue

        action = tx.get('action')
        action_data = tx.get('actionData', {})
        amount_raw = action_data.get('amount', '0')
        asset_symbol = action_data.get('assetSymbol', '').upper()
        asset_price_usd_raw = action_data.get('assetPriceUSD', '0')
        timestamp = tx.get('timestamp')

        asset_decimals = {
            'USDC': 6,
            'DAI': 18,
            'WETH': 18,
            'ETH': 18,
            'USDT': 6,
            'WBTC': 8,
        }
        
        decimals = asset_decimals.get(asset_symbol, 18)

        try:
            amount = float(amount_raw) / (10**decimals)
            asset_price_usd = float(asset_price_usd_raw)
            amount_usd = amount * asset_price_usd
        except (ValueError, TypeError):
            amount_usd = 0.0

        wallet_features[wallet]['num_actions'] += 1

        if timestamp:
            wallet_features[wallet]['first_tx_timestamp'] = min(wallet_features[wallet]['first_tx_timestamp'], timestamp)
            wallet_features[wallet]['last_tx_timestamp'] = max(wallet_features[wallet]['last_tx_timestamp'], timestamp)
            wallet_features[wallet]['active_days'].add(datetime.fromtimestamp(timestamp).date())

        if action == 'deposit':
            wallet_features[wallet]['total_deposits_usd'] += amount_usd
            wallet_features[wallet]['num_deposits'] += 1
        elif action == 'borrow':
            wallet_features[wallet]['total_borrows_usd'] += amount_usd
            wallet_features[wallet]['num_borrows'] += 1
        elif action == 'repay':
            wallet_features[wallet]['total_repays_usd'] += amount_usd
            wallet_features[wallet]['num_repays'] += 1
        elif action == 'redeemunderlying':
            wallet_features[wallet]['total_redemptions_usd'] += amount_usd
            wallet_features[wallet]['num_redemptions'] += 1
        elif action == 'liquidationcall':
            wallet_features[wallet]['num_liquidations'] += 1

    for wallet, features in wallet_features.items():
        features['active_days_count'] = len(features['active_days'])
        del features['active_days']

        if features['first_tx_timestamp'] != float('inf') and features['last_tx_timestamp'] != 0:
            duration_seconds = features['last_tx_timestamp'] - features['first_tx_timestamp']
            features['transaction_duration_days'] = duration_seconds / (60 * 60 * 24)
        else:
            features['transaction_duration_days'] = 0

        features['net_asset_flow_usd'] = features['total_deposits_usd'] - features['total_redemptions_usd']

        if features['total_borrows_usd'] > 0:
            features['repayment_ratio'] = features['total_repays_usd'] / features['total_borrows_usd']
        else:
            features['repayment_ratio'] = 1.0

    return wallet_features

def assign_credit_score(wallet_features):
    wallet_scores = {}
    
    WEIGHT_DEPOSIT = 0.0001
    WEIGHT_REPAY = 0.0002
    WEIGHT_REPAYMENT_RATIO = 100
    WEIGHT_ACTIVE_DAYS = 5
    WEIGHT_NET_FLOW = 0.00005
    WEIGHT_NUM_ACTIONS = 0.5

    PENALTY_LIQUIDATION = 300
    PENALTY_BORROW_NO_REPAY = 0.0001
    PENALTY_LOW_REPAYMENT_RATIO = 200

    BASE_SCORE = 500

    all_raw_scores = []

    for wallet, features in wallet_features.items():
        raw_score = BASE_SCORE

        raw_score += features['total_deposits_usd'] * WEIGHT_DEPOSIT
        raw_score += features['total_repays_usd'] * WEIGHT_REPAY
        raw_score += features['active_days_count'] * WEIGHT_ACTIVE_DAYS
        raw_score += features['num_actions'] * WEIGHT_NUM_ACTIONS
        
        if features['net_asset_flow_usd'] > 0:
            raw_score += features['net_asset_flow_usd'] * WEIGHT_NET_FLOW

        if features['repayment_ratio'] >= 1.0:
            raw_score += WEIGHT_REPAYMENT_RATIO
        elif features['repayment_ratio'] < 0.5 and features['total_borrows_usd'] > 0:
            raw_score -= PENALTY_LOW_REPAYMENT_RATIO * (1 - features['repayment_ratio'])

        raw_score -= features['num_liquidations'] * PENALTY_LIQUIDATION
        
        unrepaid_borrow = max(0, features['total_borrows_usd'] - features['total_repays_usd'])
        raw_score -= unrepaid_borrow * PENALTY_BORROW_NO_REPAY

        all_raw_scores.append(raw_score)

    if not all_raw_scores:
        return {}

    min_raw_score = min(all_raw_scores)
    max_raw_score = max(all_raw_scores)

    if max_raw_score == min_raw_score:
        for wallet in wallet_features:
            wallet_scores[wallet] = 500
        return wallet_scores

    for wallet, features in wallet_features.items():
        raw_score = BASE_SCORE

        raw_score += features['total_deposits_usd'] * WEIGHT_DEPOSIT
        raw_score += features['total_repays_usd'] * WEIGHT_REPAY
        raw_score += features['active_days_count'] * WEIGHT_ACTIVE_DAYS
        raw_score += features['num_actions'] * WEIGHT_NUM_ACTIONS
        
        if features['net_asset_flow_usd'] > 0:
            raw_score += features['net_asset_flow_usd'] * WEIGHT_NET_FLOW

        if features['repayment_ratio'] >= 1.0:
            raw_score += WEIGHT_REPAYMENT_RATIO
        elif features['repayment_ratio'] < 0.5 and features['total_borrows_usd'] > 0:
            raw_score -= PENALTY_LOW_REPAYMENT_RATIO * (1 - features['repayment_ratio'])

        raw_score -= features['num_liquidations'] * PENALTY_LIQUIDATION
        unrepaid_borrow = max(0, features['total_borrows_usd'] - features['total_repays_usd'])
        raw_score -= unrepaid_borrow * PENALTY_BORROW_NO_REPAY

        normalized_score = ((raw_score - min_raw_score) / (max_raw_score - min_raw_score)) * 1000
        
        final_score = max(0, min(1000, int(normalized_score)))
        wallet_scores[wallet] = final_score

    return wallet_scores

def main():
    print("Starting wallet credit scoring process...")

    try:
        transactions = fetch_user_wallet_transactions_data()
        if not transactions:
            print("No transaction data found. Exiting.")
            return
        print(f"Loaded {len(transactions)} transactions.")
    except Exception as e:
        print(f"Error loading transaction data: {e}")
        return

    print("Engineering features for wallets...")
    wallet_features = calculate_wallet_features(transactions)
    print(f"Engineered features for {len(wallet_features)} unique wallets.")

    print("Assigning credit scores...")
    wallet_scores = assign_credit_score(wallet_features)

    print("\n--- Wallet Credit Scores ---")
    if wallet_scores:
        sorted_scores = sorted(wallet_scores.items(), key=lambda item: item[1], reverse=True)
        for wallet, score in sorted_scores:
            print(f"Wallet: {wallet} | Score: {score}")
    else:
        print("No scores could be generated.")

    print("\nCredit scoring process completed.")

if __name__ == "__main__":
    main()
