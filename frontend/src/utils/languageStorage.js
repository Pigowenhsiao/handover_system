/**
 * 語言偏好存儲工具
 * 使用 localStorage 管理用戶的語言偏好
 */

const LANGUAGE_PREFERENCE_KEY = 'selectedLanguage';
const LANGUAGE_PREFERENCE_EXPIRY_KEY = 'selectedLanguageExpiry';

// 支援的語言列表
const SUPPORTED_LANGUAGES = ['zh', 'ja', 'en'];

/**
 * 存儲語言偏好到 localStorage
 * @param {string} languageCode - 語言代碼
 * @param {number} expiryHours - 過期時間（小時），默認為 30 天
 */
export const storeLanguagePreference = (languageCode, expiryHours = 720) => { // 720 小時 = 30 天
  if (!SUPPORTED_LANGUAGES.includes(languageCode)) {
    console.warn(`不支援的語言代碼: ${languageCode}`);
    return;
  }

  try {
    // 存儲語言代碼
    localStorage.setItem(LANGUAGE_PREFERENCE_KEY, languageCode);

    // 計算過期時間並存儲
    const expiryTime = new Date().getTime() + (expiryHours * 60 * 60 * 1000);
    localStorage.setItem(LANGUAGE_PREFERENCE_EXPIRY_KEY, expiryTime.toString());

    console.log(`語言偏好已存儲: ${languageCode}`);
  } catch (error) {
    console.error('存儲語言偏好時發生錯誤:', error);
  }
};

/**
 * 從 localStorage 獲取語言偏好
 * @returns {string|null} 語言代碼或 null（如果過期或不存在）
 */
export const getLanguagePreference = () => {
  try {
    // 檢查過期時間
    const expiryTime = localStorage.getItem(LANGUAGE_PREFERENCE_EXPIRY_KEY);
    if (expiryTime) {
      const currentTime = new Date().getTime();
      if (currentTime > parseInt(expiryTime)) {
        // 首選項已過期，清除存儲
        clearLanguagePreference();
        return null;
      }
    }

    // 獲取存儲的語言代碼
    const storedLanguage = localStorage.getItem(LANGUAGE_PREFERENCE_KEY);

    // 驗證語言代碼是否支援
    if (storedLanguage && SUPPORTED_LANGUAGES.includes(storedLanguage)) {
      return storedLanguage;
    }

    return null;
  } catch (error) {
    console.error('獲取語言偏好時發生錯誤:', error);
    return null;
  }
};

/**
 * 清除語言偏好存儲
 */
export const clearLanguagePreference = () => {
  try {
    localStorage.removeItem(LANGUAGE_PREFERENCE_KEY);
    localStorage.removeItem(LANGUAGE_PREFERENCE_EXPIRY_KEY);
    console.log('語言偏好已清除');
  } catch (error) {
    console.error('清除語言偏好時發生錯誤:', error);
  }
};

/**
 * 檢查語言偏好是否有效
 * @returns {boolean} 語言偏好是否有效
 */
export const isLanguagePreferenceValid = () => {
  return getLanguagePreference() !== null;
};

/**
 * 更新語言偏好（包含 API 同步）
 * @param {string} languageCode - 新的語言代碼
 * @param {Function} apiCallback - 同步到後端 API 的回調函數
 */
export const updateLanguagePreference = async (languageCode, apiCallback = null) => {
  if (!SUPPORTED_LANGUAGES.includes(languageCode)) {
    console.warn(`不支援的語言代碼: ${languageCode}`);
    return false;
  }

  // 存儲到本地
  storeLanguagePreference(languageCode);

  // 如果提供了 API 回調，則同步到服務器
  if (apiCallback && typeof apiCallback === 'function') {
    try {
      const result = await apiCallback(languageCode);
      if (!result) {
        console.warn('語言偏好同步到服務器失敗');
      }
    } catch (error) {
      console.error('同步語言偏好到服務器時發生錯誤:', error);
    }
  }

  return true;
};

// 導出默認對象以支持多種導入方式
const LanguageStorage = {
  storeLanguagePreference,
  getLanguagePreference,
  clearLanguagePreference,
  isLanguagePreferenceValid,
  updateLanguagePreference
};

export default LanguageStorage;