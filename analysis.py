import json
import matplotlib.pyplot as plt
import numpy as np
from collections import Counter

def load_data(scores_file='wallet_scores.json', features_file='wallet_features.json'):
    """
    Loads wallet scores and features from JSON files.
    """
    try:
        with open(scores_file, 'r', encoding='utf-8') as f:
            scores = json.load(f)
        print(f"Loaded scores from {scores_file}")
    except FileNotFoundError:
        print(f"Error: Scores file '{scores_file}' not found. Please run credit_scorer.py first.", file=sys.stderr)
        return {}, {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from scores file '{scores_file}': {e}", file=sys.stderr)
        return {}, {}
    
    try:
        with open(features_file, 'r', encoding='utf-8') as f:
            features = json.load(f)
        print(f"Loaded features from {features_file}")
    except FileNotFoundError:
        print(f"Error: Features file '{features_file}' not found. Please run credit_scorer.py first.", file=sys.stderr)
        return scores, {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from features file '{features_file}': {e}", file=sys.stderr)
        return scores, {}

    return scores, features

def plot_score_distribution(scores, output_filename='score_distribution.png'):
    """
    Generates and saves a histogram of wallet credit scores.
    """
    if not scores:
        print("No scores to plot.")
        return

    score_values = list(scores.values())
    
    # Define bins for 0-100, 100-200, ..., 900-1000
    bins = np.arange(0, 1001, 100) # 0, 100, 200, ..., 1000

    plt.figure(figsize=(12, 7))
    n, bins, patches = plt.hist(score_values, bins=bins, edgecolor='black', alpha=0.7, color='skyblue')

    plt.title('Distribution of Wallet Credit Scores (0-1000)', fontsize=16)
    plt.xlabel('Credit Score Range', fontsize=12)
    plt.ylabel('Number of Wallets', fontsize=12)
    plt.xticks(bins, [f'{int(b)}-{int(b+99)}' if b < 1000 else '1000' for b in bins[:-1]] + [''], rotation=45, ha='right')
    plt.grid(axis='y', alpha=0.75, linestyle='--')

    # Add count labels on top of bars
    for i in range(len(n)):
        if n[i] > 0:
            plt.text(bins[i] + (bins[1]-bins[0])/2, n[i] + len(scores)*0.005, str(int(n[i])), ha='center', va='bottom', fontsize=10)

    plt.tight_layout()
    plt.savefig(output_filename)
    print(f"Score distribution graph saved as {output_filename}")
    plt.show() # Display the plot

def analyze_wallet_behavior(scores, features, num_samples=5):
    """
    Analyzes and prints characteristics of wallets in lower and higher score ranges.
    """
    if not scores or not features:
        print("No scores or features available for behavioral analysis.")
        return

    # Sort wallets by score
    sorted_wallets = sorted(scores.items(), key=lambda item: item[1]) # Ascending order for low scores

    # Get top N lowest scoring wallets
    lowest_score_wallets = sorted_wallets[:num_samples]
    # Get top N highest scoring wallets
    highest_score_wallets = sorted_wallets[-num_samples:]
    highest_score_wallets.reverse() # Reverse to show highest first

    print("\n--- Behavioral Analysis of Wallets ---")

    print("\n### Wallets in the Lower Score Range (Risky/Exploitative Behavior)")
    print(f"Displaying top {num_samples} lowest scoring wallets and their key features:")
    for wallet_id, score in lowest_score_wallets:
        feats = features.get(wallet_id, {})
        print(f"\nWallet: {wallet_id} | Score: {score}")
        print(f"  Total Deposits (USD): {feats.get('total_deposits_usd', 0):.2f}")
        print(f"  Total Borrows (USD): {feats.get('total_borrows_usd', 0):.2f}")
        print(f"  Total Repays (USD): {feats.get('total_repays_usd', 0):.2f}")
        print(f"  Repayment Ratio: {feats.get('repayment_ratio', 0):.2f}")
        print(f"  Number of Liquidations: {feats.get('num_liquidations', 0)}")
        print(f"  Net Asset Flow (USD): {feats.get('net_asset_flow_usd', 0):.2f}")
        print(f"  Active Days: {feats.get('active_days_count', 0)}")
        print(f"  Transaction Duration (days): {feats.get('transaction_duration_days', 0):.2f}")
        print(f"  Total Actions: {feats.get('num_actions', 0)}")
    
    print("\n**Common characteristics of low-scoring wallets often include:**")
    print("- High number of liquidations relative to total actions or duration.")
    print("- Low repayment ratio (e.g., significantly less than 1.0), indicating outstanding debt.")
    print("- Large borrow volumes with disproportionately small repay volumes.")
    print("- Potentially short transaction durations or infrequent activity, suggesting 'hit-and-run' behavior.")
    print("- Negative net asset flow (more redemptions/withdrawals than deposits).")
    print("- Few active days, indicating sporadic engagement.")


    print("\n### Wallets in the Higher Score Range (Reliable/Responsible Usage)")
    print(f"Displaying top {num_samples} highest scoring wallets and their key features:")
    for wallet_id, score in highest_score_wallets:
        feats = features.get(wallet_id, {})
        print(f"\nWallet: {wallet_id} | Score: {score}")
        print(f"  Total Deposits (USD): {feats.get('total_deposits_usd', 0):.2f}")
        print(f"  Total Borrows (USD): {feats.get('total_borrows_usd', 0):.2f}")
        print(f"  Total Repays (USD): {feats.get('total_repays_usd', 0):.2f}")
        print(f"  Repayment Ratio: {feats.get('repayment_ratio', 0):.2f}")
        print(f"  Number of Liquidations: {feats.get('num_liquidations', 0)}")
        print(f"  Net Asset Flow (USD): {feats.get('net_asset_flow_usd', 0):.2f}")
        print(f"  Active Days: {feats.get('active_days_count', 0)}")
        print(f"  Transaction Duration (days): {feats.get('transaction_duration_days', 0):.2f}")
        print(f"  Total Actions: {feats.get('num_actions', 0)}")

    print("\n**Common characteristics of high-scoring wallets often include:**")
    print("- Zero or very few liquidations.")
    print("- Repayment ratio close to or greater than 1.0, indicating full and timely debt repayment.")
    print("- Substantial total deposits and often balanced with responsible borrowing and repayment.")
    print("- Long transaction durations and many active days, showing sustained engagement.")
    print("- Positive net asset flow, contributing to the protocol's liquidity.")
    print("- Consistent and predictable transaction patterns.")


def main():
    print("Starting analysis of wallet scores...")
    scores, features = load_data()

    if not scores:
        print("Analysis cannot proceed without scores.")
        return

    # Generate and save the score distribution graph
    plot_score_distribution(scores)

    # Perform behavioral analysis
    analyze_wallet_behavior(scores, features)

    print("\nAnalysis completed. Review 'score_distribution.png' and the console output for insights.")

if __name__ == "__main__":
    main()
