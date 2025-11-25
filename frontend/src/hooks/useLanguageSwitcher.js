import { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageStorage from '../utils/languageStorage';

/**
 * 自定義 Hook: 語言切換管理
 * 提供語言切換的狀態管理和副作用處理
 */
const useLanguageSwitcher = () => {
  const { i18n } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState(i18n.language);
  const [isSwitching, setIsSwitching] = useState(false);
  const [error, setError] = useState(null);

  // 更新語言偏好到後端 API
  const updateLanguageOnServer = async (languageCode) => {
    try {
      const response = await fetch('/api/languages/settings', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language_code: languageCode }),
        credentials: 'include' // 包含 cookies（如果需要身份驗證）
      });

      if (!response.ok) {
        throw new Error(`更新語言偏好失敗: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('語言偏好已成功更新到服務器:', data);
    } catch (err) {
      console.error('更新語言偏好到服務器時發生錯誤:', err);
      throw err;
    }
  };

  // 切換語言
  const switchLanguage = async (languageCode) => {
    setIsSwitching(true);
    setError(null);

    try {
      // 更新 i18n 實例的語言
      await i18n.changeLanguage(languageCode);

      // 更新 HTML 標籤的語言屬性
      document.documentElement.lang = languageCode;

      // 更新文字方向 (此系統僅支援 LTR)
      document.documentElement.dir = 'ltr';

      // 存儲用戶選擇的語言到本地存儲
      await LanguageStorage.updateLanguagePreference(
        languageCode,
        updateLanguageOnServer  // 同步到後端 API
      );

      // 更新本地狀態
      setCurrentLanguage(languageCode);

      console.log(`語言已成功切換至: ${languageCode}`);
    } catch (err) {
      setError(err.message);
      console.error('語言切換失敗:', err);
    } finally {
      setIsSwitching(false);
    }
  };

  // 組件掛載時，從存儲中恢復語言偏好
  useEffect(() => {
    const storedLanguage = LanguageStorage.getLanguagePreference();
    if (storedLanguage && storedLanguage !== i18n.language) {
      switchLanguage(storedLanguage);
    } else if (!storedLanguage) {
      // 如果沒有存儲的語言，設置默認為日文
      if (i18n.language !== 'ja') {
        switchLanguage('ja');
      }
    }
  }, []);

  // 監聽 i18n 語言變化事件，保持狀態同步
  useEffect(() => {
    const handleLanguageChange = (lng) => {
      setCurrentLanguage(lng);
    };

    i18n.on('languageChanged', handleLanguageChange);

    return () => {
      i18n.off('languageChanged', handleLanguageChange);
    };
  }, [i18n]);

  return {
    currentLanguage,
    isSwitching,
    error,
    switchLanguage,
    supportedLanguages: ['zh', 'ja', 'en']  // 支援的語言列表
  };
};

export default useLanguageSwitcher;