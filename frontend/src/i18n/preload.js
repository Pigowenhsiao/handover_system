/**
 * 前端語言資源預載入機制
 * 在適當的時機預載入可能需要的語言資源以提升性能
 */

import { getCachedResources, setCachedResources, preloadResources } from './cache';
import { loadNamespaces, preloadCommonNamespaces } from './lazyLoad';

// 預載入配置
const PRELOAD_CONFIG = {
  // 常用命名空間，始終預載入
  COMMON_NAMESPACES: ['common', 'header', 'navigation', 'errors'],
  
  // 用戶可能訪問的頁面的命名空間
  ANTICIPATED_NAMESPACES: {
    'ja': ['login', 'dashboard', 'reports', 'settings'],
    'en': ['login', 'dashboard', 'reports', 'settings'],
    'zh': ['login', 'dashboard', 'reports', 'settings']
  },
  
  // 預載入延遲時間（毫秒）
  PRELOAD_DELAY: 2000,
  
  // 預載入超時時間（毫秒）
  PRELOAD_TIMEOUT: 10000
};

/**
 * 預載入當前語言的常用資源
 * @param {string} language - 語言代碼
 * @returns {Promise} 預載入完成的Promise
 */
export const preloadCommonResources = async (language) => {
  try {
    console.log(`開始預載入語言 ${language} 的常用資源`);
    return await preloadCommonNamespaces(language);
  } catch (error) {
    console.error(`預載入常用資源失敗 (${language}):`, error);
    return false;
  }
};

/**
 * 預載入特定頁面的資源
 * @param {string} language - 語言代碼
 * @param {Array} pageNamespaces - 頁面命名空間數組
 * @returns {Promise} 預載入完成的Promise
 */
export const preloadPageResources = async (language, pageNamespaces) => {
  try {
    console.log(`開始預載入語言 ${language} 的頁面資源:`, pageNamespaces);
    return await loadNamespaces(language, pageNamespaces);
  } catch (error) {
    console.error(`預載入頁面資源失敗 (${language}):`, error);
    return false;
  }
};

/**
 * 智能預載入 - 根據用戶行為預測可能需要的資源
 * @param {string} currentLanguage - 當前語言
 * @param {string} currentPage - 當前頁面
 * @returns {Promise} 預載入完成的Promise
 */
export const smartPreload = async (currentLanguage, currentPage = 'home') => {
  try {
    // 根據當前頁面預測可能訪問的頁面
    const predictedPages = predictNextPages(currentPage);
    
    // 獲取預測頁面的命名空間
    const namespacesToPreload = [
      ...PRELOAD_CONFIG.COMMON_NAMESPACES,  // 通用資源
      ...predictedPages.flatMap(page => PRELOAD_CONFIG.ANTICIPATED_NAMESPACES[currentLanguage] || [])
    ];
    
    console.log(`智能預載入 - 當前頁面: ${currentPage}, 預測頁面:`, predictedPages);
    
    // 預載入資源（延遲執行以避免阻塞當前操作）
    setTimeout(async () => {
      try {
        await loadNamespaces(currentLanguage, [...new Set(namespacesToPreload)]);
        console.log(`智能預載入完成: ${currentLanguage}`);
      } catch (preloadError) {
        console.error('智能預載入失敗:', preloadError);
      }
    }, PRELOAD_CONFIG.PRELOAD_DELAY);
    
    return true;
  } catch (error) {
    console.error('智能預載入設置失敗:', error);
    return false;
  }
};

/**
 * 根據當前頁面預測下一個可能訪問的頁面
 * @param {string} currentPage - 當前頁面
 * @returns {Array} 預測的下一個頁面數組
 */
const predictNextPages = (currentPage) => {
  // 定義頁面轉換關係
  const pageTransitions = {
    'login': ['dashboard', 'home'],
    'home': ['dashboard', 'reports', 'settings'],
    'dashboard': ['reports', 'settings', 'profile'],
    'reports': ['dashboard', 'export', 'filter'],
    'settings': ['profile', 'dashboard', 'account'],
    'profile': ['settings', 'dashboard'],
    'default': ['home', 'dashboard', 'reports']
  };
  
  return pageTransitions[currentPage] || pageTransitions['default'];
};

/**
 * 預載入所有支援語言的通用資源（用於語言切換優化）
 * @returns {Promise} 預載入完成的Promise
 */
export const preloadAllLanguagesCommonResources = async () => {
  const supportedLanguages = ['zh', 'ja', 'en'];
  const preloadPromises = supportedLanguages.map(lang => 
    preloadCommonNamespaces(lang).catch(error => {
      console.error(`預載入語言 ${lang} 通用資源失敗:`, error);
    })
  );
  
  try {
    await Promise.all(preloadPromises);
    console.log('所有支援語言的通用資源預載入完成');
    return true;
  } catch (error) {
    console.error('批量預載入失敗:', error);
    return false;
  }
};

/**
 * 檢查資源是否已載入或緩存
 * @param {string} language - 語言代碼
 * @param {Array} namespaces - 命名空間數組
 * @returns {object} 檢查結果
 */
export const checkResourcesAvailability = (language, namespaces) => {
  const result = {
    available: [],
    missing: [],
    fromCache: [],
    needsLoad: []
  };
  
  namespaces.forEach(ns => {
    // 檢查緩存中是否有資源
    const cached = getCachedResources(language, ns);
    if (cached) {
      result.available.push(ns);
      result.fromCache.push(ns);
    } else {
      // 在i18next中檢查資源是否已載入
      if (window.i18n && window.i18n.hasResourceBundle) {
        if (window.i18n.hasResourceBundle(language, ns)) {
          result.available.push(ns);
          result.needsLoad.push(ns); // 技術上已載入，但不在緩存中
        } else {
          result.missing.push(ns);
        }
      } else {
        result.missing.push(ns);
      }
    }
  });
  
  return result;
};

/**
 * 連接資源載入進度回調
 * @param {Function} onProgress - 進度回調函數 (progress: 0-100)
 * @param {Function} onComplete - 完成回調函數
 */
export const setupProgressiveLoading = (onProgress, onComplete) => {
  let totalNamespaces = 0;
  let loadedNamespaces = 0;
  
  // 監聽i18next的載入事件
  if (window.i18n) {
    window.i18n.on('loaded', (loaded) => {
      totalNamespaces = Object.keys(loaded).length;
      loadedNamespaces = Object.values(loaded).filter(resources => resources).length;
      
      if (totalNamespaces > 0) {
        const progress = Math.round((loadedNamespaces / totalNamespaces) * 100);
        if (onProgress) onProgress(progress);
      }
    });
    
    window.i18n.on('initialized', () => {
      if (onComplete) onComplete();
    });
  }
};

/**
 * 預載入與用戶角色相關的資源
 * @param {string} language - 語言代碼
 * @param {string} userRole - 用戶角色
 * @returns {Promise} 預載入完成的Promise
 */
export const preloadRoleBasedResources = async (language, userRole = 'user') => {
  try {
    // 定義不同角色需要的命名空間
    const roleNamespaces = {
      'admin': ['admin', 'management', 'users', 'system'],
      'manager': ['management', 'reports', 'analytics'],
      'user': ['common', 'user', 'profile'],
      'default': ['common', 'user']
    };
    
    const namespaces = roleNamespaces[userRole] || roleNamespaces['default'];
    console.log(`預載入角色 ${userRole} 的資源:`, namespaces);
    
    return await loadNamespaces(language, namespaces);
  } catch (error) {
    console.error(`預載入角色相關資源失敗 (${userRole}):`, error);
    return false;
  }
};

/**
 * 啟動應用程序時的全面預載入
 * @param {string} initialLanguage - 初始語言
 * @param {object} userInfo - 用戶信息（可選）
 */
export const startupPreload = async (initialLanguage, userInfo = null) => {
  console.log('開始應用程序啟動預載入...');
  
  try {
    // 1. 預載入通用資源
    await preloadCommonResources(initialLanguage);
    
    // 2. 如果有用戶信息，預載入基於角色的資源
    if (userInfo && userInfo.role) {
      await preloadRoleBasedResources(initialLanguage, userInfo.role);
    }
    
    // 3. 預載入當前頁面資源（如果可以確定的話）
    // 這通常在應用程序的路由組件中調用
    
    // 4. 啟動智能預載入（根據用戶行為）
    // 這通常在用戶與應用程序交互後啟動
    
    console.log('應用程序啟動預載入完成');
  } catch (error) {
    console.error('應用程序啟動預載入失敗:', error);
  }
};

// 導出默認為對象以支持多種導入方式
const PreloadManager = {
  preloadCommonResources,
  preloadPageResources,
  smartPreload,
  preloadAllLanguagesCommonResources,
  checkResourcesAvailability,
  setupProgressiveLoading,
  preloadRoleBasedResources,
  startupPreload,
  PRELOAD_CONFIG
};

export default PreloadManager;