import i18n from 'i18next';

/**
 * 語言切換邏輯模組
 * 提供應用程序中語言切換的統一方法
 */

// 語言代碼映射表
const languageMap = {
  'zh': { name: '中文', flag: '🇨🇳' },
  'ja': { name: '日本語', flag: '🇯🇵' },
  'en': { name: 'English', flag: '🇺🇸' }
};

/**
 * 切換應用程序語言
 * @param {string} languageCode - 目標語言代碼 (zh, ja, en)
 * @returns {Promise} 切換語言的Promise對象
 */
export const switchLanguage = async (languageCode) => {
  if (!languageMap[languageCode]) {
    console.warn(`不支援的語言代碼: ${languageCode}`);
    return false;
  }

  try {
    // 更新i18n實例的語言
    await i18n.changeLanguage(languageCode);
    
    // 更新HTML標籤的語言屬性
    document.documentElement.lang = languageCode;
    
    // 更新文字方向 (此系統僅支援LTR)
    document.documentElement.dir = 'ltr';
    
    // 存儲用戶選擇的語言到本地存儲
    localStorage.setItem('selectedLanguage', languageCode);
    
    console.log(`語言已切換至: ${languageCode}`);
    return true;
  } catch (error) {
    console.error('切換語言時發生錯誤:', error);
    return false;
  }
};

/**
 * 獲取當前語言
 * @returns {string} 當前語言代碼
 */
export const getCurrentLanguage = () => {
  return i18n.language;
};

/**
 * 獲取支持的語言列表
 * @returns {Array} 支持的語言代碼數組
 */
export const getSupportedLanguages = () => {
  return Object.keys(languageMap);
};

/**
 * 獲取語言名稱
 * @param {string} languageCode - 語言代碼
 * @returns {string} 語言名稱
 */
export const getLanguageName = (languageCode) => {
  return languageMap[languageCode]?.name || languageCode;
};

/**
 * 獲取語言標誌
 * @param {string} languageCode - 語言代碼
 * @returns {string} 語言標誌
 */
export const getLanguageFlag = (languageCode) => {
  return languageMap[languageCode]?.flag || '';
};

/**
 * 檢查語言是否支持
 * @param {string} languageCode - 語言代碼
 * @returns {boolean} 是否支持該語言
 */
export const isLanguageSupported = (languageCode) => {
  return !!languageMap[languageCode];
};

// 導出默認對象以支持多種導入方式
const LanguageSwitcher = {
  switchLanguage,
  getCurrentLanguage,
  getSupportedLanguages,
  getLanguageName,
  getLanguageFlag,
  isLanguageSupported
};

export default LanguageSwitcher;