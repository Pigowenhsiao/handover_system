# API Documentation

## 範圍與前提

- 本專案為桌面應用程式，倉庫內未包含 HTTP 伺服器實作。
- 下列 HTTP 端點皆為「前端程式碼中被呼叫/預期存在」的 API 介面，需由外部後端提供。
- 另附「內部介面（非 HTTP）」為程式內部資料層/流程約定，參考 `contracts/api-contracts.md`。

## HTTP API（前端程式碼中引用）

### 1) Auth

#### POST `/api/v1/auth/login`

- 來源：`frontend/main.py`
- 用途：登入取得 access token
- 請求格式：`application/x-www-form-urlencoded`
- 請求欄位：
  - `username` (string)
  - `password` (string)
- 回應（預期）：
  - `200 OK`
  - JSON：`{ "access_token": "<token>" }`
- 錯誤（預期）：
  - `401 Unauthorized`（帳號或密碼錯誤）

#### GET `/api/v1/auth/me`

- 來源：`frontend/main.py`
- 用途：取得當前使用者資訊
- Headers：`Authorization: Bearer <access_token>`
- 回應（預期）：
  - `200 OK`
  - JSON（示例）：`{ "username": "admin", "role": "admin" }`

### 2) 語言偏好

#### PUT `/api/languages/settings`

- 來源：`frontend/src/components/LanguageSelector.js`、`frontend/src/hooks/useLanguageSwitcher.js`
- 用途：更新使用者語言偏好
- 請求格式：`application/json`
- Body：`{ "language_code": "ja" | "zh" | "en" }`
- 備註：`fetch` 會帶 `credentials: include`

### 3) 語言資源

#### GET `/api/languages/resources?lang={{lng}}&namespace={{ns}}`

- 來源：`frontend/src/i18n/config.js`
- 用途：i18next 從後端載入翻譯資源
- 查詢參數：
  - `lang`：語言代碼（`ja`/`zh`/`en`）
  - `namespace`：命名空間（如 `common`、`header`）
- 回應（預期）：
  - `200 OK`
  - JSON：i18next 可解析的 key-value 物件

#### POST `/api/languages/missing` (sendBeacon)

- 來源：`frontend/src/i18n/fallback.js`
- 用途：記錄缺失翻譯
- Body（JSON）：
  - `language`
  - `namespace`
  - `key`
  - `timestamp`
- 回應：通常無（`navigator.sendBeacon`）

### 4) 管理端：語言資源

#### GET `/api/admin/languages/resources`

- 來源：`frontend/src/pages/admin/LanguageResourceManager.js`
- 查詢參數（可選）：
  - `skip` (string/int)
  - `limit` (string/int)
  - `search` (string)
  - `language_code` (string)
  - `namespace` (string)
- 回應（預期）：
  - JSON 陣列：`[{ id, language_code, resource_key, resource_value, namespace }]`

#### POST `/api/admin/languages/resources`

- Body：`{ language_code, resource_key, resource_value, namespace }`

#### PUT `/api/admin/languages/resources/{id}`

- Body：`{ resource_value, namespace }`

#### DELETE `/api/admin/languages/resources/{id}`

#### POST `/api/admin/languages/resources/bulk`

- 來源：`frontend/src/components/admin/LanguageImport.js`
- Body：`[{ language_code, resource_key, resource_value, namespace }, ...]`
- 回應（預期）：
  - JSON：`{ "created_count": <number> }`

### 5) 管理端：語言包

#### GET `/api/admin/languages/packs`

- 回應（預期）：
  - JSON 陣列：`[{ id, language_code, pack_name, version, is_active }]`

#### POST `/api/admin/languages/packs`

- Body：`{ language_code, pack_name, version, is_active }`

#### PUT `/api/admin/languages/packs/{id}`

- Body：`{ pack_name, version, is_active }`

#### DELETE `/api/admin/languages/packs/{id}`

## 內部介面（非 HTTP）

> 參考 `contracts/api-contracts.md`，此部分為 UI 與資料層的內部約定。

### 使用者管理

- `create_user(username, password, role) -> bool`
- `authenticate_user(username, password) -> User | None`
- `update_user(user_id, username?, password?, role?) -> bool`
- `delete_user(user_id) -> bool`

### 日報

- `upsert_daily_report(date, shift, area, author_id, summary_fields) -> report_id`
- `get_daily_report(date, shift, area) -> DailyReport | None`

### 出勤記錄

- `save_attendance(report_id, regular_data, contract_data) -> bool`
- `get_attendance(report_id) -> list`

### 設備異常 / 異常批次

- `add_equipment_log(report_id, payload) -> bool`
- `add_lot_log(report_id, payload) -> bool`
- `list_equipment_logs(report_id) -> list`
- `list_lot_logs(report_id) -> list`

### Delay List / Summary Actual

- `import_delay_list(rows) -> temp_cache`
- `upload_delay_list(rows) -> bool`
- `import_summary_actual(rows) -> temp_cache`
- `upload_summary_actual(rows) -> bool`

### 統計與查詢

- `build_attendance_summary(start_date, end_date, shift?, area?) -> table + chart_data`
- `search_abnormal_history(start_date, end_date, shift?, area?) -> equipment_logs + lot_logs`

### 設定

- `load_settings() -> {auto_backup, backup_interval_days}`
- `save_settings(auto_backup, backup_interval_days) -> bool`
