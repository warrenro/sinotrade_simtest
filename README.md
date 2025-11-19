# Sinotrade Shioaji API 模擬測試與啟用腳本

[!Python](https://www.python.org/)

這是一個命令列工具，旨在幫助永豐金證券 Shioaji API 的使用者自動完成 API 啟用所需的模擬交易測試，並驗證帳號的啟用狀態。

## 開發歷程

永豐金 Shioaji API 要求使用者在啟用前，必須先在模擬環境中成功送出至少一筆證券委託和一筆期貨委託。許多初次接觸程式交易的使用者可能會在此步驟卡關，不確定該如何下單、要下什麼商品、以及如何確認自己是否成功。

為了解決這個痛點，我開發了這個 `simtest.py` 腳本，其開發歷程如下：

1.  **確立目標**：將官方文件中的模擬測試要求（T02 證券委託、T03 期貨委託）規格化，並將其轉化為一個自動化腳本。同時，也需要一個方法來確認帳號是否真的「啟用成功」。

2.  **功能拆分**：
    -   **模擬測試 (`test`)**：專注於在 `simulation=True` 環境下，依序送出證券和期貨的委託單。為了通用性，腳本選擇了常見的 `2890 永豐金` 作為證券標的，並自動選擇 `台指期近月合約` 作為期貨標的。
    -   **啟用驗證 (`verify`)**：專注於在 `simulation=False` 的正式環境下，登入並檢查帳號的 `signed` 狀態，以確認帳號是否已被後台系統開通。

3.  **使用者體驗優化**：
    -   **命令列介面**：使用 Python 內建的 `argparse` 函式庫，提供 `test` 和 `verify` 兩個清晰的子命令，並附上說明，讓使用者能輕易上手。
    -   **敏感資訊處理**：為了安全性與便利性，腳本設計為優先讀取環境變數 (`os.environ.get`)。如果找不到環境變數，則會引導使用者手動輸入，並使用 `getpass` 模組來隱藏密碼等機密資訊的輸入過程。
    -   **清晰的輸出**：在每個步驟（登入、下單、驗證）都提供明確的 Log 輸出，成功時顯示 ✅，失敗時顯示 ❌ 並附上錯誤訊息，讓使用者能清楚了解當前進度與結果。

4.  **程式碼實作**：
    -   將核心邏輯封裝在 `run_simulation_test` 和 `verify_activation_status` 兩個函式中，提高程式碼的可讀性與可維護性。
    -   撰寫 `get_env_variable` 輔助函式來統一處理環境變數的讀取與使用者輸入提示。
    -   在 `main` 函式中處理命令列參數的解析與對應函式的呼叫。

這個專案從一個簡單的想法出發，逐步演化成一個結構清晰、使用者友善且能實際解決問題的實用工具。

## 功能

-   **自動化模擬測試**：一鍵執行啟用 API 所需的證券與期貨模擬下單。
-   **帳號啟用驗證**：登入正式環境，檢查您的證券與期貨帳號是否已開通 API 交易權限。
-   **友善的引導**：若未設定環境變數，腳本會引導您輸入必要的資訊。
-   **安全性**：密碼等敏感資訊在輸入時會被隱藏。

## 安裝

1.  **安裝 Shioaji**：

    ```bash
    pip install shioaji
    ```

2.  **下載腳本**：

    下載本專案的 `simtest.py` 檔案。

## 使用方法

### 步驟一：執行模擬測試

打開您的終端機 (Terminal) 或命令提示字元 (CMD)，進入 `simtest.py` 所在的目錄，然後執行以下指令：

```bash
python simtest.py test
```

腳本會提示您輸入 API Key 與 Secret Key。成功執行後，您會看到證券與期貨下單成功的訊息。

> **注意**：請等待至少 5-10 分鐘，讓後台系統處理您的測試結果，然後再進行下一步。

### 步驟二：驗證帳號啟用狀態

執行以下指令來確認您的帳號是否已成功啟用：

```bash
python simtest.py verify
```

腳本會提示您輸入 API Key/Secret Key、憑證路徑、憑證密碼及身分證字號。

-   若帳號狀態顯示為 `🟢 Verified`，恭喜您，帳號已成功啟用！
-   若顯示為 `🟡 Not Verified`，表示後台尚未完成開通，請稍後再試。

### (建議) 使用環境變數

為了避免每次執行時都需手動輸入，建議您將以下資訊設定為環境變數：

```bash
# Linux / macOS
export SINOTRADE_API_KEY="YOUR_API_KEY"
export SINOTRADE_SECRET_KEY="YOUR_SECRET_KEY"
export SINOTRADE_CA_PATH="/path/to/your/certificate.pfx"
export SINOTRADE_CA_PASS="YOUR_CA_PASSWORD"
export SINOTRADE_PERSON_ID="YOUR_PERSON_ID"

# Windows (CMD)
set SINOTRADE_API_KEY="YOUR_API_KEY"
set SINOTRADE_SECRET_KEY="YOUR_SECRET_KEY"
...
```