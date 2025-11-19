import argparse
import os
import sys
import time
from getpass import getpass

import shioaji as sj
from shioaji.contracts import Stock, Futures
from shioaji.order import Action, OrderType, StockPriceType, FuturesPriceType, FuturesOCType


def get_env_variable(var_name: str, prompt: str, secret: bool = False) -> str:
    """Fetch a variable from environment or prompt the user if not found."""
    value = os.environ.get(var_name)
    if value:
        print(f"✅ Found {var_name} in environment variables.")
        return value

    print(f"⚠️ {var_name} not found in environment variables.")
    if secret:
        return getpass(f"Please enter {prompt}: ")
    return input(f"Please enter {prompt}: ")


def run_simulation_test(api: sj.Shioaji):
    """
    Runs the simulation test by logging in, placing a stock order,
    and placing a futures order as per the specification.
    """
    print("\n--- Running Simulation Test ---")
    print("Connecting to: Simulation Environment (simulation=True)")

    # T01: Login Test
    api.login(
        api_key=get_env_variable("SINOTRADE_API_KEY", "your API Key"),
        secret_key=get_env_variable("SINOTRADE_SECRET_KEY", "your Secret Key", secret=True),
    )
    print("✅ Login successful.")

    # Fetch available accounts
    stock_account = next((acc for acc in api.accounts if acc.account_type == sj.account.AccountType.Stock), None)
    if not stock_account:
        print("❌ No stock account available. Cannot proceed with stock order test.")
        sys.exit(1)

    futopt_account = next((acc for acc in api.accounts if acc.account_type == sj.account.AccountType.Future), None)
    if not futopt_account:
        print("❌ No futures account available. Cannot proceed with futures order test.")
        sys.exit(1)

    print(f"Using Stock Account: {stock_account.account_id}")
    print(f"Using Futures Account: {futopt_account.account_id}")

    # T02: Stock Order Test
    print("\nPlacing stock order...")
    stock_contract = api.Contracts.Stocks["2890"]
    stock_order = api.Order(
        action=Action.Buy,
        price=10,
        quantity=1,
        order_type=OrderType.ROD,
        price_type=StockPriceType.LMT,
        account=stock_account,
    )
    trade = api.place_order(stock_contract, stock_order)

    if trade.status.status != sj.order.Status.Failed:
        print(f"✅ Stock order placed successfully. Status: {trade.status.status.value}")
    else:
        print(f"❌ Stock order failed: {trade.status.msg}")
        sys.exit(1)

    # Frequency Limit: Wait for 1 second
    print("\nWaiting 1 second before placing futures order...")
    time.sleep(1)

    # T03: Futures Order Test
    print("\nPlacing futures order...")
    # Get the near-month Taiwan Index Futures contract
    futures_contract = min(
        (
            c
            for c in api.Contracts.Futures.TXF
            if c.code not in ["TXFR1", "TXFR2"]
        ),
        key=lambda c: c.delivery_month,
    )
    print(f"Using futures contract: {futures_contract.code} ({futures_contract.name})")

    futures_order = api.Order(
        action=Action.Buy,
        price=18000,
        quantity=1,
        order_type=OrderType.ROD,
        price_type=FuturesPriceType.LMT,
        octype=FuturesOCType.Auto,
        account=futopt_account,
    )
    trade = api.place_order(futures_contract, futures_order)

    if trade.status.status != sj.order.Status.Failed:
        print(f"✅ Futures order placed successfully. Status: {trade.status.status.value}")
    else:
        print(f"❌ Futures order failed: {trade.status.msg}")
        sys.exit(1)

    print("\n🎉 Simulation test completed successfully!")
    print("Please wait at least 5 minutes before running the 'verify' command.")
    api.logout()


def verify_activation_status(api: sj.Shioaji):
    """
    Connects to the production environment to verify if the accounts
    have been activated.
    """
    print("\n--- Verifying Account Activation ---")
    print("Connecting to: Production Environment (simulation=False)")

    # Get credentials and certificate info
    api_key = get_env_variable("SINOTRADE_API_KEY", "your API Key")
    secret_key = get_env_variable("SINOTRADE_SECRET_KEY", "your Secret Key", secret=True)
    ca_path = get_env_variable("SINOTRADE_CA_PATH", "path to your certificate (.pfx file)")
    ca_pass = get_env_variable("SINOTRADE_CA_PASS", "your certificate password", secret=True)
    person_id = get_env_variable("SINOTRADE_PERSON_ID", "your National ID / Person ID")

    # Activate Certificate
    try:
        api.activate_ca(
            ca_path=ca_path,
            ca_passwd=ca_pass,
            person_id=person_id,
        )
        print("✅ Certificate activated.")
    except Exception as e:
        print(f"❌ Certificate activation failed: {e}")
        print("Please check your certificate path, password, and person ID.")
        sys.exit(1)

    # Login to Production
    api.login(api_key, secret_key)
    print("✅ Login successful.")

    print("-" * 40)
    print("Checking Account Activation Status...")
    print("-" * 40)

    verified_count = 0
    total_accounts = 0

    # Check Stock Account
    stock_account = next((acc for acc in api.accounts if acc.account_type == sj.account.AccountType.Stock), None)
    if stock_account:
        total_accounts += 1
        if stock_account.signed:
            print(f"🟢 Stock Account ({stock_account.account_id}): Verified")
            verified_count += 1
        else:
            print(f"🟡 Stock Account ({stock_account.account_id}): Not Verified")
    else:
        print("ℹ️ No stock account found to verify.")

    # Check Futures Account
    futopt_account = next((acc for acc in api.accounts if acc.account_type == sj.account.AccountType.Future), None)
    if futopt_account:
        total_accounts += 1
        if futopt_account.signed:
            print(f"🟢 Futures Account ({futopt_account.account_id}): Verified")
            verified_count += 1
        else:
            print(f"🟡 Futures Account ({futopt_account.account_id}): Not Verified")
    else:
        print("ℹ️ No futures account found to verify.")

    print("-" * 40)
    if total_accounts > 0 and verified_count == total_accounts:
        print("🎉 Verification complete. All available accounts are activated.")
    elif verified_count > 0:
        print("⚠️ Verification partially complete. Some accounts are not yet active.")
    else:
        print("❌ Verification failed. No accounts are active yet. Please ensure you have signed the documents and completed the test successfully.")

    api.logout()


def main():
    """Main function to parse arguments and run the script."""
    parser = argparse.ArgumentParser(
        description="Shioaji API Simulation Test and Activation Script.",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog="""
Examples:
  python simtest.py test      # Run the simulation trading test.
  python simtest.py verify    # Verify the account activation status.
"""
    )
    parser.add_argument(
        "command",
        choices=["test", "verify"],
        help="The command to execute: 'test' or 'verify'."
    )
    args = parser.parse_args()

    if args.command == "test":
        api = sj.Shioaji(simulation=True)
        run_simulation_test(api)
    elif args.command == "verify":
        api = sj.Shioaji(simulation=False)
        verify_activation_status(api)


if __name__ == "__main__":
    main()