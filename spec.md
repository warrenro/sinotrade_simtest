# `simtest.py` 腳本技術規格

本文件說明 `simtest.py` 腳本的內部執行流程與邏輯。

## 1. 腳本目的

自動化執行永豐金 Sinotrade API 的模擬下單測試，並在指定時間後檢查帳戶的 API 測試狀態。

## 2. 執行流程

1.  **參數解析**：
    -   腳本啟動時，使用 `argparse` 解析命令列參數。
    -   優先從環境變數 `SHIOAJI_API_KEY` 和 `SHIOAJI_SECRET_KEY` 讀取金鑰。若命令列參數有提供，則會覆蓋環境變數的值。
    -   若未提供金鑰，腳本將提示錯誤並終止。

2.  **模擬下單 (`run_simtest` 函式)**：
    -   初始化 `shioaji` API，設定 `simulation=True`。
    -   使用提供的金鑰登入模擬環境。
    -   **證券下單**：
        -   根據 `--stock-code` 參數取得證券合約。
        -   使用 `--stock-price` 和 `--quantity` 參數建立一個限價單 (LMT)、ROD 的買單。
        -   執行 `api.place_order` 並印出委託結果。
    -   **等待 1 秒**：為符合官方測試要求，在證券下單後，腳本會暫停 1 秒。
    -   **期貨下單**：
        -   自動查找近月的台指期貨合約 (TXF)。
        -   使用 `--futures-price` 和 `--quantity` 參數建立一個限價單 (LMT)、ROD 的買單。
        -   執行 `api.place_order` 並印出委託結果。
    -   執行完畢後，登出模擬環境。

3.  **輪詢等待 (`Polling`)**：
    -   模擬下單完成後，腳本進入輪詢模式。
    -   腳本會每隔 60 秒呼叫一次 `check_api_test_status` 函式。
    -   輪詢會持續進行，直到 `check_api_test_status` 回傳 `True` (所有帳戶皆通過)，或達到 `--wait-time` 設定的最大分鐘數為止。

4.  **狀態檢查 (`check_api_test_status` 函式)**：
    -   等待結束後，初始化 `shioaji` API，設定 `simulation=False`（正式環境）。
    -   使用相同的金鑰登入正式環境。
    -   遍歷返回的所有帳戶 (`StockAccount`, `FutureAccount`)。
    -   檢查每個帳戶的 `signed` 屬性。如果所有帳戶的 `signed` 皆為 `True`，則函式回傳 `True`，否則回傳 `False`。
    -   執行完畢後，登出正式環境。

## 3. 錯誤處理

-   **模組依賴**：啟動時檢查 `shioaji` 是否已安裝。
-   **登入與下單**：使用 `try...except` 區塊捕捉登入、下單過程中可能發生的例外，並印出錯誤訊息。
-   **資源釋放**：使用 `finally` 區塊確保無論成功或失敗，都會執行 `api.logout()`。
