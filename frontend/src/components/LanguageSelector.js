import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './LanguageSelector.css';

const LanguageSelector = () => {
  const { i18n, t } = useTranslation();
  const [currentLanguage, setCurrentLanguage] = useState(i18n.language || 'ja');

  // 支援的語言列表
  const supportedLanguages = [
    { code: 'ja', name: t('common.japanese', '日本語'), flag: '🇯🇵' },
    { code: 'en', name: t('common.english', 'English'), flag: '🇺🇸' },
    { code: 'zh', name: t('common.chinese', '中文'), flag: '🇨🇳' }
  ];

  // 處理語言切換
  const handleLanguageChange = async (langCode) => {
    try {
      // 更新當前語言狀態
      setCurrentLanguage(langCode);

      // 使用 i18n 切換語言
      await i18n.changeLanguage(langCode);

      // 更新語言偏好到後端 API
      try {
        const response = await fetch('/api/languages/settings', {
          method: 'PUT',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ language_code: langCode }),
          credentials: 'include' // 包含 cookies（如果需要身份驗證）
        });

        if (!response.ok) {
          console.error('更新語言偏好到服務器失敗:', response.statusText);
        }
      } catch (error) {
        console.error('更新語言偏好時發生錯誤:', error);
      }
    } catch (error) {
      console.error('切換語言時發生錯誤:', error);
    }
  };

  // 當組件掛載時，確保當前語言設置正確
  useEffect(() => {
    if (i18n.language && !supportedLanguages.some(lang => lang.code === i18n.language)) {
      // 如果當前語言不在支援列表中，切換到默認語言（日文）
      handleLanguageChange('ja');
    }
  }, []);

  return (
    <div className="language-selector">
      <select
        value={currentLanguage}
        onChange={(e) => handleLanguageChange(e.target.value)}
        className="language-select-dropdown"
        aria-label={t('common.selectLanguage', '選擇語言')}
      >
        {supportedLanguages.map((lang) => (
          <option key={lang.code} value={lang.code}>
            {lang.flag} {lang.name}
          </option>
        ))}
      </select>
    </div>
  );
};

export default LanguageSelector;