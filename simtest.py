import os
import time
import sys
import argparse

try:
    import shioaji as sj
    from shioaji.constant import Status
except ImportError:
    print("錯誤: 找不到 'shioaji' 模組。")
    print("請先使用 'pip install -r requirements.txt' 指令安裝必要的套件。")
    exit(1)

def run_simtest(api_key, secret_key, stock_code, stock_price, futures_price, quantity):
    """
    Executes the Sinotrade API simulation test for stocks and futures.

    Args:
        api_key (str): Your Shioaji API Key.
        secret_key (str): Your Shioaji Secret Key.
        stock_code (str): The stock code to trade.
        stock_price (float): The price for the stock order.
        futures_price (float): The price for the futures order.
        quantity (int): The quantity for both orders.
    """
    # 登入
    api = sj.Shioaji(simulation=True)
    try:
        api.login(api_key=api_key, secret_key=secret_key)
        print("模擬測試登入成功。")
    except Exception as e:
        print(f"登入失敗: {e}")
        return

    # 證券下單測試
    try:
        print("\n--- 開始證券下單模擬測試 ---")
        contract = api.Contracts.Stocks.TSE[stock_code]
        order = api.Order(
            price=stock_price,
            quantity=quantity,
            action=sj.constant.Action.Buy,
            price_type=sj.constant.StockPriceType.LMT,
            order_type=sj.constant.OrderType.ROD,
            account=api.stock_account
        )
        trade = api.place_order(contract, order)
        if trade.status.status == Status.Submitted:
            print("證券委託單已成功送出。")
            print(f"委託單詳細資料: {trade}")
        else:
            print(f"證券委託單失敗: {trade.status.status}")

    except Exception as e:
        print(f"證券下單測試時發生錯誤: {e}")

    # 根據官方要求，證券與期貨下單需間隔 1 秒以上
    print("\n等待 1 秒後進行期貨下單...")
    time.sleep(1)

    # 期貨下單測試
    try:
        print("\n--- 開始期貨下單模擬測試 ---")
        # 取得近月台指期貨合約
        futures_contracts = [
            x for x in api.Contracts.Futures.TXF
            if x.code[-2:] not in ["R1", "R2"]
        ]
        if not futures_contracts:
            print("找不到可用的台指期貨合約。")
            return
            
        contract = min(futures_contracts, key=lambda x: x.delivery_date)
        print(f"使用期貨合約: {contract.code}")

        order = api.Order(
            action=sj.constant.Action.Buy,
            price=futures_price,
            quantity=quantity,
            price_type=sj.constant.FuturesPriceType.LMT,
            order_type=sj.constant.OrderType.ROD,
            octype=sj.constant.FuturesOCType.Auto,
            account=api.futopt_account
        )
        trade = api.place_order(contract, order)
        if trade.status.status == Status.Submitted:
            print("期貨委託單已成功送出。")
            print(f"委託單詳細資料: {trade}")
        else:
            print(f"期貨委託單失敗: {trade.status.status}")

    except Exception as e:
        print(f"期貨下單測試時發生錯誤: {e}")
    finally:
        api.logout()
        print("\n已登出模擬測試帳號。")

def check_api_test_status(api_key, secret_key):
    """
    Checks if the API test has been passed by logging into production.
    Returns True if all accounts have passed, False otherwise.

    Args:
        api_key (str): Your Shioaji API Key.
        secret_key (str): Your Shioaji Secret Key.
    """
    api = sj.Shioaji(simulation=False) # Production Mode
    all_passed = False
    try:
        accounts = api.login(api_key=api_key, secret_key=secret_key)
        print("正式環境登入成功，正在檢查帳戶狀態...")

        if not accounts:
            print("找不到任何帳戶可供檢查。")
            return False

        passed_accounts = 0
        for acc in accounts:
            signed_status = "已通過 (signed=True)" if acc.signed else "未通過或未簽署 (signed=False)"
            print(f"帳戶類型: {type(acc).__name__}, 帳號: {acc.account_id}, 狀態: {signed_status}")
            if acc.signed:
                passed_accounts += 1
        
        if passed_accounts > 0 and passed_accounts == len(accounts):
            all_passed = True

    except Exception as e:
        print(f"登入正式環境或檢查狀態時發生錯誤: {e}")
        return False
    finally:
        api.logout()
        print("已登出正式環境。")
    return all_passed

if __name__ == "__main__":
    # For better security, load credentials from environment variables if not provided via command line
    api_key_env = os.environ.get("SHIOAJI_API_KEY")
    secret_key_env = os.environ.get("SHIOAJI_SECRET_KEY")

    parser = argparse.ArgumentParser(description="Sinotrade API 模擬下單與狀態檢查工具")
    parser.add_argument("--api-key", type=str, default=api_key_env, help="您的 Shioaji API Key (or set SHIOAJI_API_KEY env var)")
    parser.add_argument("--secret-key", type=str, default=secret_key_env, help="您的 Shioaji Secret Key (or set SHIOAJI_SECRET_KEY env var)")
    parser.add_argument("--stock-code", type=str, default="2890", help="要進行模擬下單的證券代號")
    parser.add_argument("--stock-price", type=float, default=18.0, help="證券模擬下單的價格")
    parser.add_argument("--futures-price", type=float, default=15000.0, help="期貨模擬下單的價格")
    parser.add_argument("--quantity", type=int, default=1, help="模擬下單的數量")
    parser.add_argument("--wait-time", type=int, default=10, help="輪詢狀態的最長等待分鐘數 (逾時時間)")
    args = parser.parse_args()

    if not args.api_key or not args.secret_key:
        print("錯誤: 請提供 API Key 和 Secret Key。")
        print("您可以透過 --api-key 和 --secret-key 參數，或設定 SHIOAJI_API_KEY 和 SHIOAJI_SECRET_KEY 環境變數來提供。")
        sys.exit(1)
    
    try:
        run_simtest(api_key=args.api_key, 
                    secret_key=args.secret_key, 
                    stock_code=args.stock_code, 
                    stock_price=args.stock_price, 
                    futures_price=args.futures_price, 
                    quantity=args.quantity)
    except Exception as e:
        print(f"執行模擬測試時發生未預期的錯誤: {e}")
        sys.exit(1)

    print("\n模擬下單測試已完成。")
    print(f"開始輪詢 API 測試狀態，每分鐘檢查一次，最長等待 {args.wait_time} 分鐘...")

    all_passed = False
    for i in range(args.wait_time):
        print(f"\n--- 第 {i+1} 分鐘，開始檢查 ---")
        if check_api_test_status(api_key=args.api_key, secret_key=args.secret_key):
            all_passed = True
            print("\n恭喜！所有帳戶均已通過 API 測試。")
            break
        if i < args.wait_time - 1:
            print("尚未全部通過，將於 1 分鐘後再次檢查...")
            time.sleep(60)

    if not all_passed:
        print(f"\n已達到最長等待時間 ({args.wait_time} 分鐘)，仍有帳戶未通過測試。")
        print("請稍後手動登入永豐金證券官網確認，或聯繫您的營業員。")