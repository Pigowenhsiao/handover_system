import React, { createContext, useContext, useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import LanguageStorage from '../utils/languageStorage';

// 創建語言上下文
const LanguageContext = createContext();

// 自定義 Hook 以使用語言上下文
export const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

// 語言上下文提供者組件
export const LanguageProvider = ({ children }) => {
  const { i18n } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState(i18n.language);
  const [isInitialized, setIsInitialized] = useState(false);

  // 語言切換函數
  const changeLanguage = async (languageCode) => {
    try {
      // 更新 i18n 實例的語言
      await i18n.changeLanguage(languageCode);

      // 更新 HTML 標籤的語言屬性
      document.documentElement.lang = languageCode;

      // 更新文字方向 (此系統僅支援 LTR)
      document.documentElement.dir = 'ltr';

      // 存儲用戶選擇的語言到本地存儲
      LanguageStorage.storeLanguagePreference(languageCode);

      // 更新本地狀態
      setCurrentLanguage(languageCode);

      console.log(`語言已成功切換至: ${languageCode}`);
    } catch (error) {
      console.error('語言切換失敗:', error);
    }
  };

  // 初始化語言設置
  useEffect(() => {
    const initializeLanguage = async () => {
      // 從本地存儲獲取語言偏好
      const storedLanguage = LanguageStorage.getLanguagePreference();
      
      if (storedLanguage && storedLanguage !== i18n.language) {
        // 如果存儲的語言與當前語言不同，則切換
        await changeLanguage(storedLanguage);
      } else if (!storedLanguage) {
        // 如果沒有存儲的語言，設置默認為日文
        if (i18n.language !== 'ja') {
          await changeLanguage('ja');
        }
      }
      
      setIsInitialized(true);
    };

    initializeLanguage();
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

  // 上下文值
  const value = {
    currentLanguage,
    isInitialized,
    changeLanguage,
    supportedLanguages: ['zh', 'ja', 'en']  // 支援的語言列表
  };

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
};

export default LanguageContext;