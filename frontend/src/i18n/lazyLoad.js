/**
 * 延遲載入翻譯資源策略
 * 優化多語言應用的性能，僅載入需要的語言資源
 */

import i18n from 'i18next';

/**
 * 按需載入特定命名空間的翻譯資源
 * @param {string} language - 語言代碼
 * @param {string|Array} namespace - 命名空間或命名空間數組
 * @returns {Promise} 載入完成的Promise
 */
export const loadNamespaces = async (language, namespace) => {
  try {
    // 確保提供了有效的語言和命名空間
    if (!language || !namespace) {
      throw new Error('語言代碼和命名空間是必需的');
    }

    // 如果namespace是字符串，轉換為數組
    const namespaces = Array.isArray(namespace) ? namespace : [namespace];

    // 檢查當前語言是否已載入了請求的命名空間
    const notLoadedNamespaces = namespaces.filter(ns => 
      !i18n.hasResourceBundle(language, ns)
    );

    if (notLoadedNamespaces.length > 0) {
      // 載入缺失的命名空間
      await i18n.loadNamespaces(notLoadedNamespaces);
    }

    console.log(`已載入命名空間: ${notLoadedNamespaces.join(', ')} (${language})`);
    return true;
  } catch (error) {
    console.error('載入命名空間時發生錯誤:', error);
    throw error;
  }
};

/**
 * 預載入常用的命名空間
 * @param {string} language - 語言代碼
 * @returns {Promise} 預載入完成的Promise
 */
export const preloadCommonNamespaces = async (language) => {
  const commonNamespaces = ['common', 'header', 'navigation', 'errors'];
  return loadNamespaces(language, commonNamespaces);
};

/**
 * 載入頁面特定的命名空間
 * @param {string} language - 語言代碼
 * @param {Array} pageNamespaces - 頁面特定命名空間數組
 * @returns {Promise} 載入完成的Promise
 */
export const loadPageNamespaces = async (language, pageNamespaces) => {
  return loadNamespaces(language, pageNamespaces);
};

/**
 * 配置i18next的延遲載入選項
 */
export const configureLazyLoading = () => {
  // 設置i18next選項以支持延遲載入
  i18n.options.load = 'currentOnly'; // 僅載入當前語言，而非所有支援的語言
  
  // 設置命名空間分離載入
  i18n.options.ns = i18n.options.ns || ['common'];
  i18n.options.defaultNS = i18n.options.defaultNS || 'common';
  
  console.log('已配置延遲載入選項');
};

/**
 * 實現智能緩存策略
 * @param {string} language - 語言代碼
 * @param {string} namespace - 命名空間
 * @param {object} resources - 要緩存的資源
 */
export const cacheNamespaceResources = (language, namespace, resources) => {
  try {
    // 使用i18next的內建資源添加功能
    i18n.addResourceBundle(language, namespace, resources, true, false);
    console.log(`已緩存命名空間資源: ${namespace} (${language})`);
  } catch (error) {
    console.error('緩存命名空間資源時發生錯誤:', error);
  }
};

/**
 * 動態載入語言包
 * @param {string} language - 要載入的語言
 * @returns {Promise} 載入完成的Promise
 */
export const loadLanguage = async (language) => {
  if (!language) {
    console.warn('未指定要載入的語言');
    return false;
  }

  try {
    // 檢查語言包是否已經載入
    if (!i18n.options.whitelist || i18n.options.whitelist.includes(language)) {
      if (i18n.hasLanguage(language)) {
        console.log(`語言包已載入: ${language}`);
        return true;
      }
    }

    // 載入語言包
    await i18n.loadLanguages([language]);
    console.log(`已載入語言包: ${language}`);
    return true;
  } catch (error) {
    console.error(`載入語言包時發生錯誤 (${language}):`, error);
    throw error;
  }
};

/**
 * 檢查特定語言和命名空間是否已載入
 * @param {string} language - 語言代碼
 * @param {string} namespace - 命名空間
 * @returns {boolean} 是否已載入
 */
export const isNamespaceLoaded = (language, namespace) => {
  return i18n.hasResourceBundle(language, namespace);
};

/**
 * 預載入多個語言的常用命名空間
 * @param {Array} languages - 語言代碼數組
 * @returns {Promise} 預載入完成的Promise
 */
export const preloadLanguagesAndNamespaces = async (languages) => {
  const loadPromises = languages.map(lang => 
    preloadCommonNamespaces(lang).catch(error => {
      console.error(`預載入語言 ${lang} 時發生錯誤:`, error);
    })
  );
  
  await Promise.all(loadPromises);
  console.log(`已預載入語言: ${languages.join(', ')}`);
  return true;
};

// 導出默認為對象以支持多種導入方式
const LazyLoadManager = {
  loadNamespaces,
  preloadCommonNamespaces,
  loadPageNamespaces,
  configureLazyLoading,
  cacheNamespaceResources,
  loadLanguage,
  isNamespaceLoaded,
  preloadLanguagesAndNamespaces
};

export default LazyLoadManager;