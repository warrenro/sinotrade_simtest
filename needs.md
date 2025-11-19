API測試¶
  確保您完全理解如何使用，需在模擬模式完成測試報告，內容包含以下功能:

登入測試 login
下單測試 place_order
Attention

可測試時間:

因應公司資訊安全規定，測試報告服務為星期一至五 08:00 ~ 20:00
18:00 ~ 20:00: 只允許台灣IP
08:00 ~ 18:00: 沒有限制
版本限制:

版本 >= 1.2:

安裝指令: uv add shioaji or pip install -U shioaji

其他:

API下單簽署時間須早於API測試的時間，以利審核通過
證券、期貨戶須各別測試
證券/期貨下單測試，需間隔1秒以上，以利系統留存測試紀錄
查詢使用版本¶
版本

import shioaji as sj

print(sj.__version__)
# 1.0.0
請注意版本限制
登入測試¶
登入


version>=1.0
version<1.0
api = sj.Shioaji(simulation=True) # 模擬模式
api.login(
    api_key="金鑰",     # 請修改此處
    secret_key="密鑰"   # 請修改此處
)

版本 >= 1.0: 使用 API Key 進行登入，若您尚未申請 API Key，可參考 Token
版本 < 1.0: 使用身分證字號進行登入
證券下單測試¶
證券


version>=1.0
version<1.0
# 商品檔 - 請修改此處
contract = api.Contracts.Stocks.TSE["2890"]

# 證券委託單 - 請修改此處
order = api.Order(
    price=18,                                       # 價格
    quantity=1,                                     # 數量
    action=sj.constant.Action.Buy,                  # 買賣別
    price_type=sj.constant.StockPriceType.LMT,      # 委託價格類別
    order_type=sj.constant.OrderType.ROD,           # 委託條件
    account=api.stock_account                       # 下單帳號
)

# 下單
trade = api.place_order(contract, order)
trade

Out

Response Code: 0 | Event Code: 0 | Info: host '218.32.76.102:80', IP 218.32.76.102:80 (host 1 of 1) (host connection attempt 1 of 1) (total connection attempt 1 of 1) | Event: Session up

Trade(
    contract=Stock(...), 
    order=Order(...),
    status=OrderStatus(
        id='531e27af', 
        status=<Status.Submitted: 'Submitted'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 11, 18, 3, 867490), 
        order_quantity=1,
        deals=[]
    )
)
收到此訊息，Response Code: 0 | Event Code: 0 | Info: host '218.32.76.102:80' ...，代表您成功連結上測試伺服器。此訊息只有首次下單會顯示。若您未收到此訊息，請確認一下狀況均符合

在可測試時間進行測試
版本限制
signed 未在您的帳號中顯示
委託單狀態不應為Failed，若您的委託單狀態Failed，請正確的修改委託單然後再次執行place_order

商品檔
證券委託下單
期貨下單測試¶
期貨


verion>=1.0
verion<1.0
# 商品檔 - 近月台指期貨, 請修改此處
contract = min(
    [
        x for x in api.Contracts.Futures.TXF 
        if x.code[-2:] not in ["R1", "R2"]
    ],
    key=lambda x: x.delivery_date
)

# 期貨委託單 - 請修改此處
order = api.Order(
    action=sj.constant.Action.Buy,                   # 買賣別
    price=15000,                                     # 價格
    quantity=1,                                      # 數量
    price_type=sj.constant.FuturesPriceType.LMT,     # 委託價格類別
    order_type=sj.constant.OrderType.ROD,            # 委託條件
    octype=sj.constant.FuturesOCType.Auto,           # 倉別
    account=api.futopt_account                       # 下單帳號
)

# 下單
trade = api.place_order(contract, order)

Out

Response Code: 0 | Event Code: 0 | Info: host '218.32.76.102:80', IP 218.32.76.102:80 (host 1 of 1) (host connection attempt 1 of 1) (total connection attempt 1 of 1) | Event: Session up

Trade(
    contract=Stock(...), 
    order=Order(...),
    status=OrderStatus(
        id='531e27af', 
        status=<Status.Submitted: 'Submitted'>, 
        status_code='00', 
        order_datetime=datetime.datetime(2023, 1, 12, 11, 18, 3, 867490), 
        order_quantity=1,
        deals=[]
    )
)
收到此訊息，Response Code: 0 | Event Code: 0 | Info: host '218.32.76.102:80' ...，代表您成功連結上測試伺服器。此訊息只有首次下單會顯示。若您未收到此訊息，請確認一下狀況均符合

在可測試時間進行測試
版本限制
signed 未在您的帳號中顯示
委託單狀態不應為Failed，若您的委託單狀態Failed，請正確的修改委託單然後再次執行place_order

商品檔
期貨委託下單
查詢是否通過API測試¶
Attention

在查詢前，請確認以下狀況均符合

API下單簽署時間須早於API測試的時間，以利審核通過
在可測試時間進行測試
證券、期貨戶須各別測試
等待API測試審核(約5分鐘)
簽署狀態


version>=1.0
version<1.0
import shioaji as sj

api = sj.Shioaji(simulation=False)   # Production Mode
accounts = api.login(
    api_key="YOUR_API_KEY",         # edit it
    secret_key="YOUR_SECRET_KEY"    # edit it
)
accounts

Out

Response Code: 0 | Event Code: 0 | Info: host '203.66.91.161:80', hostname '203.66.91.161:80' IP 203.66.91.161:80 (host 1 of 1) (host connection attempt 1 of 1) (total connection attempt 1 of 1) | Event: Session up

[FutureAccount(person_id='QBCCAIGJBJ', broker_id='F002000', account_id='9100020', signed=True, username='PAPIUSER01'),
StockAccount(person_id='QBCCAIGJBJ', broker_id='9A95', account_id='0504350', username='PAPIUSER01')]
signed=True: 恭喜完成測試! Ex: FutureAccount.
signed=False 或 signed 未顯示: 此帳號尚未通過API測試或尚未簽署API下單文件. Ex: StockAccount.

啟用憑證¶

若是使用測試帳號無需啟用憑證
如果您使用macOS，可能會遇到版本上的問題。我們建議您使用 docker 去運行shioaji。
In

result = api.activate_ca(
    ca_path="/c/your/ca/path/Sinopac.pfx",
    ca_passwd="YOUR_CA_PASSWORD",
    person_id="Person ID of this Ca",
)

print(result)
# True
憑證路徑

在 Windows 系統中，如果文件路徑使用 \ 來分隔文件，您需要將它替換為 /。

確認憑證效期¶
In

api.get_ca_expiretime("Person ID")