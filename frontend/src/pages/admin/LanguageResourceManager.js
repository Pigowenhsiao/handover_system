import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './LanguageResourceManager.css';

const LanguageResourceManager = () => {
  const { t } = useTranslation();
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingResource, setEditingResource] = useState(null);
  const [newResource, setNewResource] = useState({
    language_code: 'ja',
    resource_key: '',
    resource_value: '',
    namespace: 'common'
  });
  const [filters, setFilters] = useState({
    search: '',
    language_code: '',
    namespace: ''
  });

  // 支援的語言
  const supportedLanguages = [
    { code: 'ja', name: t('common.japanese', '日本語') },
    { code: 'en', name: t('common.english', 'English') },
    { code: 'zh', name: t('common.chinese', '中文') }
  ];

  // 獲取語言資源
  const fetchResources = async () => {
    try {
      setLoading(true);
      const queryParams = new URLSearchParams({
        skip: '0',
        limit: '100',
        ...(filters.search && { search: filters.search }),
        ...(filters.language_code && { language_code: filters.language_code }),
        ...(filters.namespace && { namespace: filters.namespace })
      });

      const response = await fetch(`/api/admin/languages/resources?${queryParams}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setResources(data);
    } catch (err) {
      setError(err.message);
      console.error('獲取語言資源時發生錯誤:', err);
    } finally {
      setLoading(false);
    }
  };

  // 組件掛載時獲取資源
  useEffect(() => {
    fetchResources();
  }, [filters]);

  // 處理表單輸入變化
  const handleInputChange = (field, value) => {
    if (editingResource) {
      setEditingResource({ ...editingResource, [field]: value });
    } else {
      setNewResource({ ...newResource, [field]: value });
    }
  };

  // 創建新資源
  const handleCreateResource = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/admin/languages/resources', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newResource)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 重置表單
      setNewResource({
        language_code: 'ja',
        resource_key: '',
        resource_value: '',
        namespace: 'common'
      });

      // 重新獲取資源列表
      fetchResources();
    } catch (err) {
      setError(err.message);
      console.error('創建語言資源時發生錯誤:', err);
    }
  };

  // 更新資源
  const handleUpdateResource = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`/api/admin/languages/resources/${editingResource.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          resource_value: editingResource.resource_value,
          namespace: editingResource.namespace
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 退出編輯模式
      setEditingResource(null);

      // 重新獲取資源列表
      fetchResources();
    } catch (err) {
      setError(err.message);
      console.error('更新語言資源時發生錯誤:', err);
    }
  };

  // 刪除資源
  const handleDeleteResource = async (resourceId) => {
    if (!window.confirm(t('common.confirmDelete', '確定要刪除此資源嗎？'))) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/languages/resources/${resourceId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 重新獲取資源列表
      fetchResources();
    } catch (err) {
      setError(err.message);
      console.error('刪除語言資源時發生錯誤:', err);
    }
  };

  // 編輯資源
  const startEditing = (resource) => {
    setEditingResource({ ...resource });
  };

  // 取消編輯
  const cancelEditing = () => {
    setEditingResource(null);
  };

  if (error) {
    return (
      <div className="language-resource-manager">
        <h2>{t('common.languageResourceManager', '語言資源管理')}</h2>
        <div className="error-message">
          {t('errors.errorOccurred', '發生錯誤')}: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="language-resource-manager">
      <h2>{t('common.languageResourceManager', '語言資源管理')}</h2>

      {/* 過濾器 */}
      <div className="filters">
        <input
          type="text"
          placeholder={t('common.search', '搜索')}
          value={filters.search}
          onChange={(e) => setFilters({...filters, search: e.target.value})}
        />
        <select
          value={filters.language_code}
          onChange={(e) => setFilters({...filters, language_code: e.target.value})}
        >
          <option value="">{t('common.allLanguages', '所有語言')}</option>
          {supportedLanguages.map(lang => (
            <option key={lang.code} value={lang.code}>{lang.name}</option>
          ))}
        </select>
        <select
          value={filters.namespace}
          onChange={(e) => setFilters({...filters, namespace: e.target.value})}
        >
          <option value="">{t('common.allNamespaces', '所有命名空間')}</option>
          <option value="common">common</option>
          <option value="validation">validation</option>
          <option value="dashboard">dashboard</option>
        </select>
      </div>

      {/* 創建新資源表單 */}
      <div className="create-form">
        <h3>{t('common.createNew', '創建新資源')}</h3>
        <form onSubmit={handleCreateResource}>
          <select
            value={newResource.language_code}
            onChange={(e) => handleInputChange('language_code', e.target.value)}
          >
            {supportedLanguages.map(lang => (
              <option key={lang.code} value={lang.code}>{lang.name}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder={t('common.resourceKey', '資源鍵')}
            value={newResource.resource_key}
            onChange={(e) => handleInputChange('resource_key', e.target.value)}
            required
          />
          <input
            type="text"
            placeholder={t('common.resourceValue', '資源值')}
            value={newResource.resource_value}
            onChange={(e) => handleInputChange('resource_value', e.target.value)}
            required
          />
          <input
            type="text"
            placeholder={t('common.namespace', '命名空間')}
            value={newResource.namespace}
            onChange={(e) => handleInputChange('namespace', e.target.value)}
          />
          <button type="submit">{t('common.create', '創建')}</button>
        </form>
      </div>

      {/* 資源列表 */}
      <div className="resources-list">
        <h3>{t('common.resourcesList', '資源列表')}</h3>
        {loading ? (
          <div className="loading">{t('common.loading', '載入中...')}</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>{t('common.id', 'ID')}</th>
                <th>{t('common.language', '語言')}</th>
                <th>{t('common.resourceKey', '資源鍵')}</th>
                <th>{t('common.resourceValue', '資源值')}</th>
                <th>{t('common.namespace', '命名空間')}</th>
                <th>{t('common.actions', '操作')}</th>
              </tr>
            </thead>
            <tbody>
              {resources.map(resource => (
                <tr key={resource.id}>
                  <td>{resource.id}</td>
                  <td>{supportedLanguages.find(lang => lang.code === resource.language_code)?.name || resource.language_code}</td>
                  <td>{resource.resource_key}</td>
                  <td>
                    {editingResource && editingResource.id === resource.id ? (
                      <input
                        type="text"
                        value={editingResource.resource_value}
                        onChange={(e) => handleInputChange('resource_value', e.target.value)}
                      />
                    ) : (
                      resource.resource_value
                    )}
                  </td>
                  <td>
                    {editingResource && editingResource.id === resource.id ? (
                      <input
                        type="text"
                        value={editingResource.namespace}
                        onChange={(e) => handleInputChange('namespace', e.target.value)}
                      />
                    ) : (
                      resource.namespace
                    )}
                  </td>
                  <td>
                    {editingResource && editingResource.id === resource.id ? (
                      <>
                        <button onClick={handleUpdateResource}>{t('common.save', '保存')}</button>
                        <button onClick={cancelEditing}>{t('common.cancel', '取消')}</button>
                      </>
                    ) : (
                      <>
                        <button onClick={() => startEditing(resource)}>{t('common.edit', '編輯')}</button>
                        <button onClick={() => handleDeleteResource(resource.id)}>{t('common.delete', '刪除')}</button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default LanguageResourceManager;