/**
 * 多語言功能單元測試
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import { renderHook, act } from '@testing-library/react-hooks';
import useLanguageSwitcher from '../hooks/useLanguageSwitcher';
import { switchLanguage } from '../i18n/switcher';
import { getTranslationWithFallback } from '../i18n/fallback';
import { preloadCommonResources } from '../i18n/preload';

// 模擬翻譯資源
const mockResources = {
  en: {
    translation: {
      "hello": "Hello",
      "welcome": "Welcome",
      "user": "User",
      "nested": {
        "deep": "Deep Translation"
      }
    }
  },
  zh: {
    translation: {
      "hello": "你好",
      "welcome": "歡迎",
      "user": "用戶",
      "nested": {
        "deep": "深度翻譯"
      }
    }
  },
  ja: {
    translation: {
      "hello": "こんにちは",
      "welcome": "ようこそ",
      "user": "ユーザー",
      "nested": {
        "deep": "深層翻訳"
      }
    }
  }
};

// 初始化i18next
i18n
  .use(initReactI18next)
  .init({
    resources: mockResources,
    lng: 'ja',  // 默認日文
    fallbackLng: 'ja',
    interpolation: {
      escapeValue: false
    }
  });

describe('多語言功能測試', () => {
  describe('語言切換功能', () => {
    test('應該成功切換語言', async () => {
      // 初始語言應該是日文
      expect(i18n.language).toBe('ja');
      
      // 切換到中文
      await act(async () => {
        await switchLanguage('zh');
      });
      
      // 驗證語言已切換
      expect(i18n.language).toBe('zh');
      
      // 切換到英文
      await act(async () => {
        await switchLanguage('en');
      });
      
      // 驗證語言已切換
      expect(i18n.language).toBe('en');
      
      // 切換回日文
      await act(async () => {
        await switchLanguage('ja');
      });
      
      // 驗證語言已切換
      expect(i18n.language).toBe('ja');
    });

    test('應該正確翻譯內容', async () => {
      // 測試日文翻譯
      expect(i18n.t('hello')).toBe('こんにちは');
      expect(i18n.t('welcome')).toBe('ようこそ');
      expect(i18n.t('nested.deep')).toBe('深層翻訳');
      
      // 切換到中文並測試
      await act(async () => {
        await switchLanguage('zh');
      });
      
      expect(i18n.t('hello')).toBe('你好');
      expect(i18n.t('welcome')).toBe('歡迎');
      expect(i18n.t('nested.deep')).toBe('深度翻譯');
      
      // 切換到英文並測試
      await act(async () => {
        await switchLanguage('en');
      });
      
      expect(i18n.t('hello')).toBe('Hello');
      expect(i18n.t('welcome')).toBe('Welcome');
      expect(i18n.t('nested.deep')).toBe('Deep Translation');
    });
  });

  describe('語言切換 Hook', () => {
    test('應該能夠使用 useLanguageSwitcher Hook', async () => {
      const { result } = renderHook(() => useLanguageSwitcher());
      
      // 初始狀態
      expect(result.current.currentLanguage).toBe('ja');
      expect(result.current.supportedLanguages).toEqual(['zh', 'ja', 'en']);
      
      // 測試切換到中文
      await act(async () => {
        await result.current.switchLanguage('zh');
      });
      
      expect(result.current.currentLanguage).toBe('zh');
      expect(result.current.isSwitching).toBe(false);
      expect(result.current.error).toBeNull();
      
      // 測試切換到英文
      await act(async () => {
        await result.current.switchLanguage('en');
      });
      
      expect(result.current.currentLanguage).toBe('en');
      
      // 切換回日文以便其他測試
      await act(async () => {
        await result.current.switchLanguage('ja');
      });
    });
    
    test('應該處理錯誤情況', async () => {
      const { result } = renderHook(() => useLanguageSwitcher());
      
      // 嘗試切換到不支援的語言
      await act(async () => {
        await result.current.switchLanguage('fr'); // 不支援的語言
      });
      
      // 驗證錯誤狀態
      expect(result.current.error).not.toBeNull();
    });
  });

  describe('回退機制', () => {
    test('應該在缺少翻譯時使用回退語言', () => {
      // 添加一個只有特定語言才有的翻譯鍵
      i18n.addResourceBundle('en', 'translation', { 'unique_en_key': 'Unique English' }, true, true);
      
      // 浮動到沒有此翻譯的語言，應返回默認值或鍵本身
      const fallbackResult = getTranslationWithFallback('unique_en_key', 'Default Value', { lng: 'zh' });
      expect(fallbackResult).toBe('Default Value');
      
      // 如果使用當前語言有此鍵，則應返回正確翻譯
      i18n.changeLanguage('en');
      const englishResult = i18n.t('unique_en_key');
      expect(englishResult).toBe('Unique English');
    });
  });

  describe('預載入功能', () => {
    test('應該能夠預載入通用資源', async () => {
      // 測試預載入功能
      const result = await preloadCommonResources('ja');
      expect(result).toBe(true);
    });
  });

  describe('性能測試', () => {
    test('語言切換應該在合理時間內完成', async () => {
      const startTime = performance.now();
      
      // 執行語言切換
      await act(async () => {
        await switchLanguage('zh');
        await switchLanguage('ja'); // 切換回來
      });
      
      const endTime = performance.now();
      const duration = endTime - startTime;
      
      // 語言切換應該在500ms內完成
      expect(duration).toBeLessThan(500);
    });
  });
});