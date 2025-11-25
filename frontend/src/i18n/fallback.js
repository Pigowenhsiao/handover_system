/**
 * 語言回退機制
 * 當特定語言的翻譯缺失時，提供適當的回退處理
 */

import i18n from 'i18next';

// 定義語言優先級順序，當前語言沒有翻譯時的回退順序
const languageFallbackOrder = {
  'zh': ['zh', 'ja', 'en'],  // 中文 -> 日文 -> 英文
  'ja': ['ja', 'zh', 'en'],  // 日文 -> 中文 -> 英文  
  'en': ['en', 'ja', 'zh']   // 英文 -> 日文 -> 中文
};

/**
 * 設置回退語言
 * @param {string} primaryLanguage - 主要語言
 * @returns {Array} 回退語言順序數組
 */
export const setFallbackLanguages = (primaryLanguage) => {
  const fallbackOrder = languageFallbackOrder[primaryLanguage] || ['ja', 'en', 'zh'];
  
  // 設置i18next的回退順序
  i18n.options.fallbackLng = {
    [primaryLanguage]: fallbackOrder.slice(1), // 除了主語言外的其他語言作為回退
    default: ['ja', 'en', 'zh'] // 默認回退順序
  };
  
  return fallbackOrder;
};

/**
 * 檢查翻譯鍵是否存在
 * @param {string} key - 翻譯鍵
 * @param {string} language - 檢查的語言
 * @returns {boolean} 翻譯是否存在
 */
export const hasTranslation = (key, language = null) => {
  if (language) {
    // 檢查特定語言是否有翻譯
    return i18n.exists(key, { lng: language });
  }
  
  // 檢查任何語言是否有翻譯
  return i18n.exists(key);
};

/**
 * 獲取翻譯，如果當前語言沒有則嘗試回退
 * @param {string} key - 翻譯鍵
 * @param {any} defaultValue - 默認值
 * @param {object} options - 翻譯選項
 * @returns {string} 翻譯結果
 */
export const getTranslationWithFallback = (key, defaultValue = '', options = {}) => {
  // 如果提供了特定語言選項，優先使用該語言
  if (options.lng) {
    if (hasTranslation(key, options.lng)) {
      return i18n.t(key, { ...options, defaultValue });
    }
    
    // 如果指定語言沒有翻譯，嘗試該語言的回退順序
    const fallbackOrder = languageFallbackOrder[options.lng] || ['ja', 'en', 'zh'];
    for (const lang of fallbackOrder) {
      if (hasTranslation(key, lang)) {
        return i18n.t(key, { ...options, lng: lang, defaultValue });
      }
    }
  } else {
    // 使用當前語言並檢查回退
    if (i18n.exists(key)) {
      return i18n.t(key, { ...options, defaultValue });
    }
    
    // 如果當前語言沒有翻譯，根據當前語言類型嘗試回退
    const currentLng = i18n.language || i18n.options.fallbackLng.default[0];
    const fallbackOrder = languageFallbackOrder[currentLng] || ['ja', 'en', 'zh'];
    
    for (const lang of fallbackOrder) {
      if (hasTranslation(key, lang)) {
        return i18n.t(key, { ...options, lng: lang, defaultValue });
      }
    }
  }
  
  // 如果所有語言都沒有翻譯，返回默認值
  return defaultValue || key;
};

/**
 * 設置自定義缺失翻譯處理器
 */
export const setupMissingTranslationHandler = () => {
  // 設置缺失翻譯時的處理
  i18n.on('missingKey', (lng, ns, key, res) => {
    console.warn(`缺少翻譯: 語言=${lng}, 命名空間=${ns}, 鍵=${key}`);
    
    // 可以在這裡記錄缺失的翻譯鍵，以便後續補充
    // 例如，發送請求到後端記錄缺失的翻譯
    try {
      navigator.sendBeacon('/api/languages/missing', JSON.stringify({
        language: lng,
        namespace: ns,
        key: key,
        timestamp: new Date().toISOString()
      }));
    } catch (e) {
      // 如果 sendBeacon 不支持或失敗，使用普通請求
      // console.log('無法發送缺失翻譯記錄');
    }
  });
};

/**
 * 更新配置以支持回退
 */
export const configureFallback = () => {
  // 設置默認回退語言
  i18n.options.fallbackLng = {
    'zh': ['ja', 'en'],
    'ja': ['zh', 'en'], 
    'en': ['ja', 'zh'],
    'default': ['ja', 'en', 'zh']
  };
  
  // 啟用回退到其他語言的翻譯
  i18n.options.load = 'languageOnly'; // 不加載帶國家代碼的語言變體
  i18n.options.saveMissing = false; // 不自動保存缺失的翻譯
  
  // 設置自定義缺失翻譯處理器
  setupMissingTranslationHandler();
};

// 導出默認對象以支持多種導入方式
const FallbackHandler = {
  setFallbackLanguages,
  hasTranslation,
  getTranslationWithFallback,
  setupMissingTranslationHandler,
  configureFallback
};

export default FallbackHandler;