/**
 * 瀏覽器語言檢測器
 * 檢測用戶的瀏覽器語言設置並自動建議合適的應用語言
 */

import i18n from 'i18next';

// 支援的語言列表
const SUPPORTED_LANGUAGES = ['zh', 'ja', 'en'];

// 瀏覽器語言到應用語言的映射
const LANGUAGE_MAP = {
  // 中文相關
  'zh': 'zh', 'zh-CN': 'zh', 'zh-TW': 'zh', 'zh-HK': 'zh', 'zh-SG': 'zh',
  // 日文相關
  'ja': 'ja', 'ja-JP': 'ja',
  // 英文相關
  'en': 'en', 'en-US': 'en', 'en-GB': 'en', 'en-CA': 'en', 'en-AU': 'en'
};

/**
 * 獲取瀏覽器語言
 * @returns {string|null} 瀏覽器語言代碼或 null
 */
export const getBrowserLanguage = () => {
  try {
    // 檢查多種可能的瀏覽器語言屬性
    const browserLang = 
      navigator.language || 
      navigator.userLanguage || 
      navigator.browserLanguage || 
      navigator.systemLanguage || 
      'ja'; // 默認為日文

    return browserLang;
  } catch (error) {
    console.warn('無法獲取瀏覽器語言:', error);
    return null;
  }
};

/**
 * 將瀏覽器語言映射到應用支援的語言
 * @param {string} browserLang - 瀏覽器語言代碼
 * @returns {string|null} 應用支援的語言代碼或 null
 */
export const mapToSupportedLanguage = (browserLang) => {
  if (!browserLang) return null;

  // 直接匹配
  if (SUPPORTED_LANGUAGES.includes(browserLang)) {
    return browserLang;
  }

  // 通過映射表匹配
  const mappedLang = LANGUAGE_MAP[browserLang];
  if (mappedLang && SUPPORTED_LANGUAGES.includes(mappedLang)) {
    return mappedLang;
  }

  // 去掉國家代碼後匹配
  const langCode = browserLang.split('-')[0];
  if (SUPPORTED_LANGUAGES.includes(langCode)) {
    return langCode;
  }

  // 檢查映射表中的簡化語言代碼
  const simplifiedLang = LANGUAGE_MAP[langCode];
  if (simplifiedLang && SUPPORTED_LANGUAGES.includes(simplifiedLang)) {
    return simplifiedLang;
  }

  return null;
};

/**
 * 檢測並獲取建議的應用語言
 * @returns {string} 建議的語言代碼
 */
export const detectRecommendedLanguage = () => {
  // 1. 首先檢查本地存儲中是否有用戶選擇的語言
  try {
    const storedLang = localStorage.getItem('selectedLanguage');
    if (storedLang && SUPPORTED_LANGUAGES.includes(storedLang)) {
      return storedLang;
    }
  } catch (error) {
    console.warn('無法訪問本地存儲:', error);
  }

  // 2. 檢測瀏覽器語言
  const browserLang = getBrowserLanguage();
  if (browserLang) {
    const appLang = mapToSupportedLanguage(browserLang);
    if (appLang) {
      return appLang;
    }
  }

  // 3. 如果都無法檢測到，返回默認語言（日文）
  return 'ja';
};

/**
 * 自動設置語言根據瀏覽器設置
 * @param {boolean} autoChange - 是否自動更改當前語言
 * @returns {Promise<string>} 設置的語言代碼
 */
export const autoSetLanguageFromBrowser = async (autoChange = true) => {
  const recommendedLang = detectRecommendedLanguage();

  if (autoChange && recommendedLang !== i18n.language) {
    try {
      await i18n.changeLanguage(recommendedLang);
      console.log(`語言已根據瀏覽器設置自動切換至: ${recommendedLang}`);
      
      // 更新HTML標籤的語言屬性
      document.documentElement.lang = recommendedLang;
      
      // 更新文字方向 (此系統僅支援LTR)
      document.documentElement.dir = 'ltr';
    } catch (error) {
      console.error('自動設置語言時發生錯誤:', error);
      return i18n.language; // 返回當前語言
    }
  }

  return recommendedLang;
};

/**
 * 初始化語言檢測器
 * @param {boolean} autoDetect - 是否啟用自動檢測
 * @param {boolean} autoChange - 是否自動更改語言
 */
export const initLanguageDetector = (autoDetect = true, autoChange = true) => {
  if (autoDetect) {
    // 立即執行一次語言檢測
    autoSetLanguageFromBrowser(autoChange);
    
    // 監聽語言變化事件
    window.addEventListener('languagechange', () => {
      console.log('檢測到瀏覽器語言變化');
      autoSetLanguageFromBrowser(autoChange);
    });
  }

  console.log('語言檢測器已初始化');
};

/**
 * 獲取語言名稱
 * @param {string} langCode - 語言代碼
 * @returns {string} 語言名稱
 */
export const getLanguageName = (langCode) => {
  const names = {
    'zh': '中文',
    'ja': '日本語', 
    'en': 'English'
  };
  return names[langCode] || langCode;
};

/**
 * 獲取語言列表及其檢測狀態
 * @returns {Array} 語言列表及狀態
 */
export const getDetectedLanguages = () => {
  const browserLang = getBrowserLanguage();
  const mappedLang = mapToSupportedLanguage(browserLang);
  const recommended = detectRecommendedLanguage();
  
  return {
    browser: {
      code: browserLang,
      mapped: mappedLang,
      name: browserLang ? getLanguageName(mappedLang || 'unknown') : 'Unknown'
    },
    recommended: {
      code: recommended,
      name: getLanguageName(recommended)
    },
    current: {
      code: i18n.language,
      name: getLanguageName(i18n.language)
    }
  };
};

// 導出默認對象以支持多種導入方式
const LanguageDetector = {
  getBrowserLanguage,
  mapToSupportedLanguage,
  detectRecommendedLanguage,
  autoSetLanguageFromBrowser,
  initLanguageDetector,
  getLanguageName,
  getDetectedLanguages
};

export default LanguageDetector;