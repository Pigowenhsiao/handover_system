/**
 * 語言資源緩存機制
 * 使用瀏覽器緩存優化多語言資源的載入時間
 */

// 本地存儲鍵前綴
const CACHE_PREFIX = 'lang_cache_';
const CACHE_TIMESTAMP_KEY = 'lang_cache_timestamp_';
const CACHE_SIZE_KEY = 'lang_cache_size_';
const CACHE_VERSION = 'v1.1'; // 更新版本以反映優化

// 設置默認緩存時間 (24 小時)
const DEFAULT_CACHE_DURATION = 24 * 60 * 60 * 1000; // 24小時（毫秒）
const MAX_CACHE_SIZE = 10 * 1024 * 1024; // 10MB 最大緩存大小

/**
 * 生成緩存鍵
 * @param {string} language - 語言代碼
 * @param {string} namespace - 命名空間
 * @returns {string} 緩存鍵
 */
const generateCacheKey = (language, namespace = 'common') => {
  return `${CACHE_PREFIX}${language}_${namespace}_${CACHE_VERSION}`;
};

/**
 * 生成時間戳鍵
 * @param {string} language - 語言代碼
 * @param {string} namespace - 命名空間
 * @returns {string} 時間戳鍵
 */
const generateTimestampKey = (language, namespace = 'common') => {
  return `${CACHE_TIMESTAMP_KEY}${language}_${namespace}_${CACHE_VERSION}`;
};

/**
 * 生成大小鍵
 * @param {string} language - 語言代碼
 * @param {string} namespace - 命名空間
 * @returns {string} 大小鍵
 */
const generateSizeKey = (language, namespace = 'common') => {
  return `${CACHE_SIZE_KEY}${language}_${namespace}_${CACHE_VERSION}`;
};

/**
 * 檢查緩存是否有效
 * @param {string} language - 語言代碼
 * @param {string} namespace - 命名空間
 * @param {number} duration - 緩存持續時間（毫秒）
 * @returns {boolean} 緩存是否有效
 */
const isCacheValid = (language, namespace = 'common', duration = DEFAULT_CACHE_DURATION) => {
  try {
    const timestampKey = generateTimestampKey(language, namespace);
    const cachedTimestamp = localStorage.getItem(timestampKey);

    if (!cachedTimestamp) {
      return false;
    }

    const currentTime = new Date().getTime();
    const cacheTime = parseInt(cachedTimestamp);

    return (currentTime - cacheTime) < duration;
  } catch (error) {
    console.error('檢查緩存有效性時發生錯誤:', error);
    return false;
  }
};

/**
 * 檢查存儲空間是否足夠
 * @param {string} data - 要存儲的數據
 * @returns {boolean} 空間是否足夠
 */
const isStorageAvailable = (data) => {
  try {
    const dataStr = JSON.stringify(data);
    const approxSize = new Blob([dataStr]).size;

    // 獲取當前localStorage使用情況
    let totalSize = 0;
    for (let key in localStorage) {
      if (localStorage.hasOwnProperty(key)) {
        totalSize += new Blob([localStorage[key]]).size;
      }
    }

    // 檢查是否超過限制
    return (totalSize + approxSize) < MAX_CACHE_SIZE;
  } catch (error) {
    console.error('檢查存儲空間時發生錯誤:', error);
    return false;
  }
};

/**
 * 獲取緩存的語言資源
 * @param {string} language - 語言代碼
 * @param {string} namespace - 命名空間
 * @returns {object|null} 緩存的資源或 null
 */
export const getCachedResources = (language, namespace = 'common') => {
  try {
    // 檢查緩存是否有效
    if (!isCacheValid(language, namespace)) {
      // 如果緩存過期，清除它
      clearCache(language, namespace);
      return null;
    }

    const cacheKey = generateCacheKey(language, namespace);
    const cachedData = localStorage.getItem(cacheKey);

    if (cachedData) {
      return JSON.parse(cachedData);
    }

    return null;
  } catch (error) {
    console.error('獲取緩存資源時發生錯誤:', error);
    return null;
  }
};

/**
 * 設置語言資源到緩存
 * @param {string} language - 語言代碼
 * @param {string} namespace - 命名空間
 * @param {object} resources - 要緩存的資源
 */
export const setCachedResources = (language, namespace = 'common', resources) => {
  try {
    // 檢查存儲空間
    if (!isStorageAvailable(resources)) {
      console.warn(`存儲空間不足，無法緩存資源: ${language}/${namespace}`);
      // 在空間不足時，嘗試清理一些舊緩存
      cleanupOldCaches();
      if (!isStorageAvailable(resources)) {
        console.error('即使清理後，存儲空間仍不足');
        return;
      }
    }

    const cacheKey = generateCacheKey(language, namespace);
    const timestampKey = generateTimestampKey(language, namespace);
    const sizeKey = generateSizeKey(language, namespace);

    // 轉換資源為字符串進行存儲
    const resourcesStr = JSON.stringify(resources);
    const resourcesSize = new Blob([resourcesStr]).size;

    // 存儲資源
    localStorage.setItem(cacheKey, resourcesStr);

    // 存儲時間戳
    const currentTime = new Date().getTime();
    localStorage.setItem(timestampKey, currentTime.toString());

    // 存儲大小信息
    localStorage.setItem(sizeKey, resourcesSize.toString());

    console.log(`語言資源已緩存: ${language}/${namespace}, 大小: ${resourcesSize} bytes`);
  } catch (error) {
    console.error('設置緩存資源時發生錯誤:', error);
  }
};

/**
 * 清除指定語言和命名空間的緩存
 * @param {string} language - 語言代碼
 * @param {string} namespace - 命名空間
 */
export const clearCache = (language, namespace = 'common') => {
  try {
    const cacheKey = generateCacheKey(language, namespace);
    const timestampKey = generateTimestampKey(language, namespace);
    const sizeKey = generateSizeKey(language, namespace);

    localStorage.removeItem(cacheKey);
    localStorage.removeItem(timestampKey);
    localStorage.removeItem(sizeKey);

    console.log(`緩存已清除: ${language}/${namespace}`);
  } catch (error) {
    console.error('清除緩存時發生錯誤:', error);
  }
};

/**
 * 清除所有語言緩存
 */
export const clearAllCache = () => {
  try {
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i);
      if (key && (key.startsWith(CACHE_PREFIX) ||
                  key.startsWith(CACHE_TIMESTAMP_KEY) ||
                  key.startsWith(CACHE_SIZE_KEY))) {
        localStorage.removeItem(key);
      }
    }

    console.log('所有語言緩存已清除');
  } catch (error) {
    console.error('清除所有緩存時發生錯誤:', error);
  }
};

/**
 * 清理過期或不必要的緩存
 */
export const cleanupOldCaches = () => {
  try {
    const keysToRemove = [];

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(CACHE_PREFIX) && key.includes(CACHE_VERSION)) {
        const parts = key.replace(CACHE_PREFIX, '').split('_');
        if (parts.length >= 3) {
          const lang = parts[0];
          const ns = parts[1];

          // 檢查緩存是否過期
          if (!isCacheValid(lang, ns)) {
            keysToRemove.push({lang, ns});
          }
        }
      }
    }

    // 移除過期的緩存
    keysToRemove.forEach(({lang, ns}) => {
      clearCache(lang, ns);
    });

    console.log(`清理了 ${keysToRemove.length} 個過期緩存`);
  } catch (error) {
    console.error('清理緩存時發生錯誤:', error);
  }
};

/**
 * 獲取緩存統計信息
 * @returns {object} 緩存統計信息
 */
export const getCacheStats = () => {
  try {
    let cacheCount = 0;
    let totalSize = 0;
    const cacheInfo = {};

    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith(CACHE_PREFIX) && key.includes(CACHE_VERSION)) {
        cacheCount++;

        // 提取語言和命名空間信息
        const parts = key.replace(CACHE_PREFIX, '').split('_');
        if (parts.length >= 3) {
          const lang = parts[0];
          const ns = parts[1];

          if (!cacheInfo[lang]) {
            cacheInfo[lang] = [];
          }

          if (!cacheInfo[lang].includes(ns)) {
            cacheInfo[lang].push(ns);
          }

          // 獲取大小信息
          const sizeKey = generateSizeKey(lang, ns);
          const size = localStorage.getItem(sizeKey);
          if (size) {
            totalSize += parseInt(size);
          }
        }
      }
    }

    return {
      totalCaches: cacheCount,
      totalSize: totalSize,
      totalSizeMB: (totalSize / (1024 * 1024)).toFixed(2),
      cacheByLanguage: cacheInfo,
      maxCacheSizeMB: (MAX_CACHE_SIZE / (1024 * 1024)).toFixed(2),
      cacheUsagePercent: ((totalSize / MAX_CACHE_SIZE) * 100).toFixed(2)
    };
  } catch (error) {
    console.error('獲取緩存統計時發生錯誤:', error);
    return {
      totalCaches: 0,
      totalSize: 0,
      cacheByLanguage: {},
      cacheUsagePercent: 0
    };
  }
};

/**
 * 預載入語言資源到緩存
 * @param {string} language - 語言代碼
 * @param {string} namespace - 命名空間
 * @param {Function} fetchResources - 獲取資源的函數
 */
export const preloadResources = async (language, namespace = 'common', fetchResources) => {
  try {
    // 檢查緩存是否已存在且有效
    if (isCacheValid(language, namespace)) {
      console.log(`語言資源已存在有效緩存: ${language}/${namespace}`);
      return true;
    }

    // 獲取資源
    const resources = await fetchResources(language, namespace);

    // 將資源存儲到緩存
    if (resources) {
      setCachedResources(language, namespace, resources);
      console.log(`語言資源已預載入到緩存: ${language}/${namespace}`);
      return true;
    }

    return false;
  } catch (error) {
    console.error('預載入語言資源時發生錯誤:', error);
    return false;
  }
};

/**
 * 實現LRU (Least Recently Used) 緩存淘汰策略
 */
export const implementLRUCache = () => {
  try {
    // 為每次訪問更新時間戳，實現LRU基礎
    const originalGetCachedResources = getCachedResources;
    getCachedResources = (language, namespace = 'common') => {
      const result = originalGetCachedResources(language, namespace);
      if (result) {
        // 更新訪問時間戳
        const timestampKey = generateTimestampKey(language, namespace);
        const currentTime = new Date().getTime();
        localStorage.setItem(timestampKey, currentTime.toString());
      }
      return result;
    };

    console.log('已實現LRU緩存策略');
  } catch (error) {
    console.error('實現LRU緩存時發生錯誤:', error);
  }
};

/**
 * 壓縮緩存數據以節省空間
 * @param {object} data - 要壓縮的數據
 * @returns {string} 壓縮後的數據
 */
export const compressCacheData = (data) => {
  // 在瀏覽器環境中，我們無法使用Node.js的zlib
  // 所以這裡實現一個簡化的壓縮策略
  // 主要是通過移除不必要的空白和優化結構

  try {
    const jsonString = JSON.stringify(data);
    // 移除不必要的空白字符
    return jsonString.replace(/\s+/g, '');
  } catch (error) {
    console.error('壓縮緩存數據時發生錯誤:', error);
    // 如果壓縮失敗，返回原始數據的字符串形式
    return JSON.stringify(data);
  }
};

/**
 * 解壓縮緩存數據
 * @param {string} compressedData - 壓縮後的數據
 * @returns {object} 解壓縮後的數據
 */
export const decompressCacheData = (compressedData) => {
  try {
    return JSON.parse(compressedData);
  } catch (error) {
    console.error('解壓縮緩存數據時發生錯誤:', error);
    // 如果解壓縮失敗，嘗試直接解析原始數據
    return compressedData;
  }
};

// 導出默認對象以支持多種導入方式
const LanguageCache = {
  getCachedResources,
  setCachedResources,
  clearCache,
  clearAllCache,
  cleanupOldCaches,
  isCacheValid,
  getCacheStats,
  preloadResources,
  implementLRUCache,
  compressCacheData,
  decompressCacheData,
  CACHE_VERSION,
  MAX_CACHE_SIZE
};

export default LanguageCache;