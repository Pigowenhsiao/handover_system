import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';
import Backend from 'i18next-http-backend';

// 從本地資源加載翻譯
import zhTranslation from '../../public/locales/zh.json';
import jaTranslation from '../../public/locales/ja.json';
import enTranslation from '../../public/locales/en.json';

// 應用文字方向性
function setDirection(language) {
  // 此系統僅支援從左到右 (LTR) 的文字方向
  document.documentElement.dir = 'ltr';
  document.documentElement.lang = language;
}

i18n
  .use(Backend)  // 從後端加載翻譯資源
  .use(LanguageDetector)  // 自動檢測用戶語言
  .use(initReactI18next)
  .init({
    // 從本地加載的翻譯資源
    resources: {
      zh: { translation: zhTranslation },
      ja: { translation: jaTranslation },
      en: { translation: enTranslation }
    },
    fallbackLng: 'ja',  // 默認為日文
    debug: process.env.NODE_ENV === 'development',
    
    // 後端配置 - 從 API 端點加載翻譯
    backend: {
      loadPath: '/api/languages/resources?lang={{lng}}&namespace={{ns}}',
    },
    
    // 檢測順序 - URL 參數 > cookie > localStorage > navigator > header > sessionStorage
    detection: {
      order: ['querystring', 'cookie', 'localStorage', 'sessionStorage', 'navigator', 'htmlTag'],
      caches: ['cookie', 'localStorage'],
      lookupQuerystring: 'lng',
      lookupCookie: 'i18next',
      lookupLocalStorage: 'i18nextLng',
      lookupSessionStorage: 'i18nextLng'
    },
    
    interpolation: {
      escapeValue: false,  // React 已經安全處理了 XSS
    },
    
    // 文字方向處理 - 此系統僅支援 LTR
    react: {
      useSuspense: false,
    },
    
    // 調整語言切換回調以設置文字方向
    lng: undefined,  // 使用檢測到的語言
    preload: ['zh', 'ja', 'en'],  // 預加載所有支持的語言
  }, (err, t) => {
    if (err) return console.error('i18next 多語言加載錯誤:', err);
    
    // 設置當前語言的文字方向
    setDirection(i18n.language);
    
    // 當語言改變時更新文字方向
    i18n.on('languageChanged', (lng) => {
      setDirection(lng);
    });
  });

export default i18n;