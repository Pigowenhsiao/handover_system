/**
 * CDN 配置文件 - 優化翻譯資源加載速度
 * 
 * 此文件描述如何配置 CDN 來優化多語言應用的性能
 */

/*
 * 1. CDN 選擇建議
 * 推薦使用的 CDN 服務:
 * - Cloudflare: 易於設置，支持智能緩存
 * - AWS CloudFront: 與 AWS 服務集成
 * - Azure CDN: 與 Azure 服務集成
 * - Alibaba Cloud CDN: 在亞洲地區表現優異
 */

/*
 * 2. 翻譯資源緩存配置
 * 為以下路徑設置適當的緩存策略:
 */
const CDN_CACHE_RULES = {
  // 語言資源文件 - 高緩存時間（例如 24 小時）
  "/frontend/public/locales/*.json": {
    "cache_time": "24h",
    "compress": true,
    "mime_type": "application/json"
  },
  
  // 前端 i18n 相關文件 - 中等緩存時間（例如 12 小時）
  "/frontend/src/i18n/*.js": {
    "cache_time": "12h",
    "compress": true,
    "mime_type": "application/javascript"
  },
  
  // 語言切換相關組件 - 中等緩存時間（例如 12 小時）
  "/frontend/src/components/LanguageSelector.js": {
    "cache_time": "12h",
    "compress": true,
    "mime_type": "application/javascript"
  },
  
  // 國際化相關工具函數 - 中等緩存時間（例如 12 小時）
  "/frontend/src/utils/localization.js": {
    "cache_time": "12h",
    "compress": true,
    "mime_type": "application/javascript"
  }
};

/*
 * 3. 動態資源緩存策略
 * 對於通過 API 獲取的動態翻譯資源，需注意:
 * - API 響應也應緩存，但時間較短（例如 1-2 小時）
 * - 語言包更新時需使用版本控制使 CDN 緩存失效
 */
const API_CACHE_RULES = {
  // 語言資源 API - 1小時緩存
  "/api/languages/resources": {
    "cache_time": "1h",
    "cache_headers": {
      "Cache-Control": "public, max-age=3600",
      "Vary": "Accept-Language"
    }
  }
};

/*
 * 4. 地理位置優化
 * 配置 CDN 根據用戶地理位置提供最佳服務器
 */
const GEO_OPTIMIZATION = {
  "ja": { // 日文用戶優化
    "primary_regions": ["APAC"], 
    "backup_regions": ["US", "EU"]
  },
  "zh": { // 中文用戶優化
    "primary_regions": ["APAC"],
    "backup_regions": ["US", "EU"]
  },
  "en": { // 英文用戶優化
    "primary_regions": ["US", "EU"],
    "backup_regions": ["APAC"]
  }
};

/*
 * 5. 壓縮和優化設置
 */
const OPTIMIZATION_SETTINGS = {
  "compression": {
    "enabled": true,
    "types": ["json", "js", "css", "html"],
    "algorithm": "gzip"  // 或 "brotli" 如果 CDN 支持
  },
  "minification": {
    "js": true,
    "css": true,
    "html": true
  }
};

/*
 * 6. 預加載和預取設置
 * 配置 CDN 預加載策略以優化用戶體驗
 */
const PRELOAD_SETTINGS = {
  // 預加載常用語言資源
  "preload_common_resources": {
    "enabled": true,
    "languages": ["ja", "en", "zh"],
    "namespaces": ["common", "header", "navigation"]
  },
  // 預取機制
  "prefetch": {
    "enabled": true,
    "pattern": "/frontend/public/locales/*/*.json"
  }
};

/*
 * 7. 性能監控設置
 */
const MONITORING_SETTINGS = {
  "performance_metrics": {
    "cache_hit_ratio": true,
    "avg_response_time": true,
    "error_rate": true
  },
  "analytics": {
    "enabled": true,
    "custom_metrics": [
      "language_resource_load_time",
      "translation_cache_efficiency"
    ]
  }
};

/*
 * 示例 Cloudflare 配置 (cloudflare.conf)
 * 
 * # 緩存語言資源文件
 * [zone.rules]
 *   language_resources = {
 *     "match": "path == '/frontend/public/locales/*'",
 *     "actions": {
 *       "cache_level": "cache_everything",
 *       "edge_cache_ttl": 86400  # 24小時
 *     }
 *   }
 * 
 * # 為 API 響應設置緩存頭
 * [http.headers]
 *   vary_language = {
 *     "match": "path == '/api/languages/resources'",
 *     "headers": {
 *       "Cache-Control": "public, max-age=3600",
 *       "Vary": "Accept-Language"
 *     }
 *   }
 */

console.log("CDN 配置指南完成 - 用於優化翻譯資源加載速度");
export default {
  CDN_CACHE_RULES,
  API_CACHE_RULES,
  GEO_OPTIMIZATION,
  OPTIMIZATION_SETTINGS,
  PRELOAD_SETTINGS,
  MONITORING_SETTINGS
};