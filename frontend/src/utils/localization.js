/**
 * 本地化工具函數
 * 提供數字、日期和貨幣的本地化格式
 */

/**
 * 格式化數字根據當前語言
 * @param {number} number - 要格式化的數字
 * @param {string} language - 語言代碼 (zh, ja, en)
 * @param {object} options - 格式化選項
 * @returns {string} 格式化後的數字字符串
 */
export const formatNumber = (number, language = 'ja', options = {}) => {
  try {
    return new Intl.NumberFormat(language, options).format(number);
  } catch (error) {
    console.warn('數字格式化失敗，使用默認格式:', error);
    // 如果格式化失敗，返回原始數字
    return number?.toString() || '0';
  }
};

/**
 * 格式化百分比根據當前語言
 * @param {number} value - 要格式化的數值 (例如 0.75 表示 75%)
 * @param {string} language - 語言代碼 (zh, ja, en)
 * @param {object} options - 格式化選項
 * @returns {string} 格式化後的百分比字符串
 */
export const formatPercent = (value, language = 'ja', options = {}) => {
  try {
    return new Intl.NumberFormat(language, {
      style: 'percent',
      ...options
    }).format(value);
  } catch (error) {
    console.warn('百分比格式化失敗，使用默認格式:', error);
    return `${(value * 100).toFixed(2)}%`;
  }
};

/**
 * 格式化日期根據當前語言
 * @param {Date|string} date - 要格式化的日期
 * @param {string} language - 語言代碼 (zh, ja, en)
 * @param {object} options - 格式化選項
 * @returns {string} 格式化後的日期字符串
 */
export const formatDate = (date, language = 'ja', options = {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit'
}) => {
  try {
    // 如果輸入是字符串，轉換為Date對象
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    if (!(dateObj instanceof Date) || isNaN(dateObj.getTime())) {
      console.warn('無效的日期值:', date);
      return date?.toString() || '';
    }
    
    return new Intl.DateTimeFormat(language, options).format(dateObj);
  } catch (error) {
    console.warn('日期格式化失敗，使用默認格式:', error);
    // 如果格式化失敗，返回ISO字符串
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj?.toString() || '';
  }
};

/**
 * 格式化時間根據當前語言
 * @param {Date|string} date - 要格式化的時間
 * @param {string} language - 語言代碼 (zh, ja, en)
 * @param {object} options - 格式化選項
 * @returns {string} 格式化後的時間字符串
 */
export const formatTime = (date, language = 'ja', options = {
  hour: '2-digit',
  minute: '2-digit'
}) => {
  try {
    // 如果輸入是字符串，轉換為Date對象
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    if (!(dateObj instanceof Date) || isNaN(dateObj.getTime())) {
      console.warn('無效的時間值:', date);
      return date?.toString() || '';
    }
    
    return new Intl.DateTimeFormat(language, options).format(dateObj);
  } catch (error) {
    console.warn('時間格式化失敗，使用默認格式:', error);
    // 如果格式化失敗，返回時間部分
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj ? dateObj.toTimeString().substring(0, 5) : '';
  }
};

/**
 * 格式化日期時間根據當前語言
 * @param {Date|string} date - 要格式化的日期時間
 * @param {string} language - 語言代碼 (zh, ja, en)
 * @param {object} options - 格式化選項
 * @returns {string} 格式化後的日期時間字符串
 */
export const formatDateTime = (date, language = 'ja', options = {
  year: 'numeric',
  month: '2-digit',
  day: '2-digit',
  hour: '2-digit',
  minute: '2-digit'
}) => {
  try {
    // 如果輸入是字符串，轉換為Date對象
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    
    if (!(dateObj instanceof Date) || isNaN(dateObj.getTime())) {
      console.warn('無效的日期時間值:', date);
      return date?.toString() || '';
    }
    
    return new Intl.DateTimeFormat(language, options).format(dateObj);
  } catch (error) {
    console.warn('日期時間格式化失敗，使用默認格式:', error);
    // 如果格式化失敗，返回ISO字符串
    const dateObj = typeof date === 'string' ? new Date(date) : date;
    return dateObj?.toISOString()?.substring(0, 16)?.replace('T', ' ') || '';
  }
};

/**
 * 格式化貨幣根據當前語言
 * @param {number} amount - 金額
 * @param {string} currency - 貨幣代碼，默認為 JPY
 * @param {string} language - 語言代碼 (zh, ja, en)
 * @param {object} options - 格式化選項
 * @returns {string} 格式化後的貨幣字符串
 */
export const formatCurrency = (amount, currency = 'JPY', language = 'ja', options = {}) => {
  try {
    return new Intl.NumberFormat(language, {
      style: 'currency',
      currency: currency,
      ...options
    }).format(amount);
  } catch (error) {
    console.warn('貨幣格式化失敗，使用默認格式:', error);
    return `${currency} ${amount}`;
  }
};

/**
 * 獲取當前語言的日期格式模式
 * @param {string} language - 語言代碼 (zh, ja, en)
 * @returns {object} 日期格式選項
 */
export const getDatePattern = (language = 'ja') => {
  const patterns = {
    'ja': { year: 'numeric', month: '2-digit', day: '2-digit' }, // YYYY/MM/DD
    'en': { year: 'numeric', month: '2-digit', day: '2-digit' }, // MM/DD/YYYY
    'zh': { year: 'numeric', month: '2-digit', day: '2-digit' }  // YYYY/MM/DD
  };
  
  return patterns[language] || patterns['ja'];
};

/**
 * 獲取當前語言的時間格式模式
 * @param {string} language - 語言代碼 (zh, ja, en)
 * @returns {object} 時間格式選項
 */
export const getTimePattern = (language = 'ja') => {
  const patterns = {
    'ja': { hour: '2-digit', minute: '2-digit', hour12: false }, // 24小時制
    'en': { hour: '2-digit', minute: '2-digit', hour12: true },  // 12小時制
    'zh': { hour: '2-digit', minute: '2-digit', hour12: false }  // 24小時制
  };
  
  return patterns[language] || patterns['ja'];
};

/**
 * 本地化比較函數 - 用於字符串排序
 * @param {string} strA - 第一個字符串
 * @param {string} strB - 第二個字符串
 * @param {string} language - 語言代碼 (zh, ja, en)
 * @returns {number} 比較結果
 */
export const localizedCompare = (strA, strB, language = 'ja') => {
  try {
    return strA.localeCompare(strB, language, { numeric: true });
  } catch (error) {
    console.warn('本地化比較失敗，使用默認比較:', error);
    return strA < strB ? -1 : strA > strB ? 1 : 0;
  }
};

// 導出默認對象以支持多種導入方式
const Localization = {
  formatNumber,
  formatPercent,
  formatDate,
  formatTime,
  formatDateTime,
  formatCurrency,
  getDatePattern,
  getTimePattern,
  localizedCompare
};

export default Localization;