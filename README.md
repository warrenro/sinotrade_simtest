# Sinotrade API 模擬下單測試

[![Python Script CI](https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>/actions/workflows/python-ci.yml/badge.svg)](https://github.com/<YOUR_GITHUB_USERNAME>/<YOUR_REPOSITORY_NAME>/actions/workflows/python-ci.yml)

---

本專案提供了一個 Python 腳本 (`simtest.py`)，用於自動化執行永豐金證券 Sinotrade API 的模擬下單測試，並在指定時間後自動檢查 API 測試是否通過。

## 專案結構

- `spec.md`: `simtest.py` 腳本的技術規格說明文件。
- `simtest.py`: 執行模擬測試和狀態查詢的 Python 腳本。
- `requirements.txt`: 專案所需的 Python 套件列表。
- `README.md`: 本說明文件。

## 環境設定

1.  **安裝 Python**：請確保您的電腦已安裝 Python 3.8 或以上版本。

2.  **安裝依賴套件**：在執行腳本之前，您需要先安裝所有必要的套件。

```bash
pip install -r requirements.txt
``` 

## 如何執行

**執行模擬下單測試與狀態查詢**

執行 `simtest.py` 腳本時，請透過 `--api-key` 和 `--secret-key` 參數傳入您的金鑰。

腳本會先進行證券和期貨的模擬下單，然後等待 10 分鐘，再自動查詢 API 測試狀態。在執行期間請保持程式運行。
```bash
python simtest.py --api-key "YOUR_API_KEY" --secret-key "YOUR_SECRET_KEY"
```
