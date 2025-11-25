# 多語言功能 API 文檔

## 概述
多語言功能提供接口以支持應用程序中的國際化 (i18n)。此功能支援三種語言：日文 (ja)、英文 (en) 和中文 (zh)。

## API 端點

### 語言資源端點

#### `GET /api/languages/resources`
獲取指定語言和命名空間的翻譯資源。

**參數:**
- `lang` (string, 必填): 語言代碼 (zh, ja, en)
- `namespace` (string, 選填): 命名空間，默認為 'common'

**響應:**
```json
{
  "lang": "ja",
  "namespace": "common", 
  "resources": {
    "key1": "value1",
    "nested": {
      "key2": "value2"
    }
  }
}
```

**示例請求:**
```
GET /api/languages/resources?lang=ja&namespace=common
```

#### `GET /api/languages/resources/{resource_id}`
獲取單個翻譯資源。

#### `POST /api/languages/resources` (管理員專用)
創建新的翻譯資源。

**請求體:**
```json
{
  "language_code": "ja",
  "resource_key": "new.key",
  "resource_value": "新しい値", 
  "namespace": "common"
}
```

#### `PUT /api/languages/resources/{resource_id}` (管理員專用)
更新翻譯資源。

**請求體:**
```json
{
  "resource_value": "更新後的值",
  "namespace": "updated_namespace"
}
```

#### `DELETE /api/languages/resources/{resource_id}` (管理員專用)
刪除翻譯資源。

### 語言設置端點

#### `GET /api/languages/settings`
獲取當前用戶的語言設置。

#### `GET /api/languages/settings/available`
獲取所有可用的語言設置。

#### `PUT /api/languages/settings`
更新當前用戶的語言設置。

**請求體:**
```json
{
  "language_code": "en"
}
```

### 管理員語言管理端點

#### `GET /api/admin/languages/resources`
獲取所有語言資源（支持分頁、搜索和過濾）。

#### `POST /api/admin/languages/resources/bulk`
批量創建語言資源。

#### `GET /api/admin/languages/packs`
獲取所有語言包。

#### `POST /api/admin/languages/packs`
創建語言包。

#### `PUT /api/admin/languages/packs/{pack_id}`
更新語言包。

#### `DELETE /api/admin/languages/packs/{pack_id}`
刪除語言包。

## 使用方法

### 在前端使用翻譯

1. 使用 `useTranslation` hook:
```javascript
import { useTranslation } from 'react-i18next';

const MyComponent = () => {
  const { t, i18n } = useTranslation();
  
  return (
    <div>
      <h1>{t('header.title')}</h1>
      <button onClick={() => i18n.changeLanguage('en')}>
        {t('common.switchToEnglish')}
      </button>
    </div>
  );
};
```

2. 使用 Trans 組件:
```javascript
import Trans from './components/Trans';

const MyComponent = () => {
  return (
    <div>
      <Trans i18nKey="common.title" defaultValue="標題" />
    </div>
  );
};
```

### 應用程序初始化

在應用程序啟動時初始化 i18n:
```javascript
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// 預加載的翻譯資源
import zhTranslation from './public/locales/zh.json';
import jaTranslation from './public/locales/ja.json';
import enTranslation from './public/locales/en.json';

i18n
  .use(Backend)
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources: {
      zh: { translation: zhTranslation },
      ja: { translation: jaTranslation },
      en: { translation: enTranslation }
    },
    fallbackLng: 'ja',  // 默認為日文
    debug: process.env.NODE_ENV === 'development',
    backend: {
      loadPath: '/api/languages/resources?lang={{lng}}&namespace={{ns}}',
    },
    detection: {
      order: ['querystring', 'cookie', 'localStorage', 'sessionStorage', 'navigator', 'htmlTag'],
      caches: ['cookie', 'localStorage']
    },
    interpolation: {
      escapeValue: false
    }
  });
```

## 錯誤處理

常見的錯誤代碼:
- `400 Bad Request`: 語言代碼無效或請求參數錯誤
- `404 Not Found`: 指定的資源不存在  
- `401 Unauthorized`: 需要身份驗證（訪問受保護端點時）
- `403 Forbidden`: 權限不足（訪問管理員端點時）
- `500 Internal Server Error`: 服務器內部錯誤

## 效能優化

- 使用緩存機制減少 API 請求
- 實施按需載入（僅載入當前需要的命名空間）
- 預載入常用語言資源以提升體驗
- 利用 CDN 加速靜態翻譯文件的分發

## 最佳實踐

1. 所有用戶界面文本都應該通過翻譯鍵進行國際化
2. 使用嵌套結構組織翻譯鍵（例如 `header.title`）
3. 為管理員功能實現適當的權限控制
4. 記錄缺失的翻譯以便補充
5. 測試不同語言下的界面顯示，確保沒有文字截斷或布局問題