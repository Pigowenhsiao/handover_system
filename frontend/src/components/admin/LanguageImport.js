import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './LanguageImport.css';

const LanguageImport = ({ onImportSuccess }) => {
  const { t } = useTranslation();
  const [file, setFile] = useState(null);
  const [languageCode, setLanguageCode] = useState('ja');
  const [namespace, setNamespace] = useState('common');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);

  // 支援的語言
  const supportedLanguages = [
    { code: 'ja', name: t('common.japanese', '日本語') },
    { code: 'en', name: t('common.english', 'English') },
    { code: 'zh', name: t('common.chinese', '中文') }
  ];

  // 處理文件選擇
  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      // 驗證文件類型
      if (selectedFile.type === 'application/json' || selectedFile.name.endsWith('.json')) {
        setFile(selectedFile);
        setError(null);
      } else {
        setError(t('errors.invalidFileType', '無效的文件類型，請選擇 JSON 文件'));
        setFile(null);
      }
    }
  };

  // 處理文件上傳
  const handleImport = async () => {
    if (!file) {
      setError(t('errors.noFileSelected', '請選擇要上傳的文件'));
      return;
    }

    setLoading(true);
    setError(null);
    setSuccessMessage(null);

    try {
      // 讀取文件內容
      const fileContent = await file.text();
      let jsonData;
      
      try {
        jsonData = JSON.parse(fileContent);
      } catch (parseError) {
        throw new Error(t('errors.invalidJsonFormat', 'JSON 格式無效'));
      }

      // 驗證 JSON 結構
      if (!isValidJsonStructure(jsonData)) {
        throw new Error(t('errors.invalidJsonStructure', 'JSON 結構不符合要求'));
      }

      // 準備批量資源數據
      const resources = flattenJsonToResources(jsonData, languageCode, namespace);

      // 發送批量創建請求
      const response = await fetch('/api/admin/languages/resources/bulk', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(resources)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      setSuccessMessage(
        t('common.importSuccess', '成功導入 {{count}} 個翻譯資源', { count: result.created_count })
      );
      
      // 如果提供了成功回調，則調用它
      if (onImportSuccess && typeof onImportSuccess === 'function') {
        onImportSuccess(result);
      }
    } catch (err) {
      setError(err.message);
      console.error('導入語言資源時發生錯誤:', err);
    } finally {
      setLoading(false);
    }
  };

  // 驗證 JSON 結構
  const isValidJsonStructure = (data) => {
    // 簡單驗證：確保數據是對象且不為空
    return typeof data === 'object' && data !== null && Object.keys(data).length > 0;
  };

  // 將嵌套 JSON 轉換為扁平的資源數組
  const flattenJsonToResources = (obj, langCode, ns, prefix = '') => {
    const resources = [];

    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        const value = obj[key];
        const fullKey = prefix ? `${prefix}.${key}` : key;

        if (typeof value === 'string') {
          // 如果值是字符串，添加到資源列表
          resources.push({
            language_code: langCode,
            resource_key: fullKey,
            resource_value: value,
            namespace: ns
          });
        } else if (typeof value === 'object' && value !== null) {
          // 如果值是對象，遞歸處理
          resources.push(...flattenJsonToResources(value, langCode, ns, fullKey));
        }
        // 忽略其他類型的值（如數字、布爾值等）
      }
    }

    return resources;
  };

  return (
    <div className="language-import">
      <h3>{t('common.importLanguageResources', '導入語言資源')}</h3>
      
      <div className="import-options">
        <label>
          {t('common.language', '語言')}:
          <select
            value={languageCode}
            onChange={(e) => setLanguageCode(e.target.value)}
          >
            {supportedLanguages.map(lang => (
              <option key={lang.code} value={lang.code}>{lang.name}</option>
            ))}
          </select>
        </label>
        
        <label>
          {t('common.namespace', '命名空間')}:
          <input
            type="text"
            value={namespace}
            onChange={(e) => setNamespace(e.target.value)}
          />
        </label>
      </div>
      
      <div className="file-upload">
        <label>
          {t('common.selectJsonFile', '選擇 JSON 文件')}:
          <input
            type="file"
            accept=".json,application/json"
            onChange={handleFileChange}
          />
        </label>
        
        {file && (
          <div className="file-info">
            {t('common.selectedFile', '已選擇文件')}: {file.name} ({(file.size / 1024).toFixed(2)} KB)
          </div>
        )}
      </div>
      
      {error && (
        <div className="error-message">
          {t('errors.error', '錯誤')}: {error}
        </div>
      )}
      
      {successMessage && (
        <div className="success-message">
          {successMessage}
        </div>
      )}
      
      <button 
        onClick={handleImport} 
        disabled={loading || !file}
        className="import-button"
      >
        {loading ? t('common.loading', '載入中...') : t('common.import', '導入')}
      </button>
      
      <div className="import-instructions">
        <h4>{t('common.importInstructions', '導入說明')}:</h4>
        <ul>
          <li>{t('common.importInstruction1', '文件必須是有效的 JSON 格式')}</li>
          <li>{t('common.importInstruction2', '嵌套對象將被轉換為點分隔的鍵（例如: header.title）')}</li>
          <li>{t('common.importInstruction3', '僅處理字符串值，其他類型的值將被忽略')}</li>
        </ul>
      </div>
    </div>
  );
};

export default LanguageImport;