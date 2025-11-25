import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './LanguagePackManager.css';

const LanguagePackManager = () => {
  const { t } = useTranslation();
  const [languagePacks, setLanguagePacks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingPack, setEditingPack] = useState(null);
  const [newPack, setNewPack] = useState({
    language_code: 'ja',
    pack_name: '',
    version: '1.0.0',
    is_active: true
  });

  // 支援的語言
  const supportedLanguages = [
    { code: 'ja', name: t('common.japanese', '日本語') },
    { code: 'en', name: t('common.english', 'English') },
    { code: 'zh', name: t('common.chinese', '中文') }
  ];

  // 獲取語言包列表
  const fetchLanguagePacks = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/admin/languages/packs');
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setLanguagePacks(data);
    } catch (err) {
      setError(err.message);
      console.error('獲取語言包時發生錯誤:', err);
    } finally {
      setLoading(false);
    }
  };

  // 組件掛載時獲取語言包
  useEffect(() => {
    fetchLanguagePacks();
  }, []);

  // 處理表單輸入變化
  const handleInputChange = (field, value) => {
    if (editingPack) {
      setEditingPack({ ...editingPack, [field]: value });
    } else {
      setNewPack({ ...newPack, [field]: value });
    }
  };

  // 創建新語言包
  const handleCreatePack = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('/api/admin/languages/packs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newPack)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 重置表單
      setNewPack({
        language_code: 'ja',
        pack_name: '',
        version: '1.0.0',
        is_active: true
      });

      // 重新獲取語言包列表
      fetchLanguagePacks();
    } catch (err) {
      setError(err.message);
      console.error('創建語言包時發生錯誤:', err);
    }
  };

  // 更新語言包
  const handleUpdatePack = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch(`/api/admin/languages/packs/${editingPack.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pack_name: editingPack.pack_name,
          version: editingPack.version,
          is_active: editingPack.is_active
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 退出編輯模式
      setEditingPack(null);

      // 重新獲取語言包列表
      fetchLanguagePacks();
    } catch (err) {
      setError(err.message);
      console.error('更新語言包時發生錯誤:', err);
    }
  };

  // 刪除語言包
  const handleDeletePack = async (packId) => {
    if (!window.confirm(t('common.confirmDelete', '確定要刪除此語言包嗎？'))) {
      return;
    }

    try {
      const response = await fetch(`/api/admin/languages/packs/${packId}`, {
        method: 'DELETE'
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      // 重新獲取語言包列表
      fetchLanguagePacks();
    } catch (err) {
      setError(err.message);
      console.error('刪除語言包時發生錯誤:', err);
    }
  };

  // 編輯語言包
  const startEditing = (pack) => {
    setEditingPack({ ...pack });
  };

  // 取消編輯
  const cancelEditing = () => {
    setEditingPack(null);
  };

  if (error) {
    return (
      <div className="language-pack-manager">
        <h2>{t('common.languagePackManager', '語言包管理')}</h2>
        <div className="error-message">
          {t('errors.errorOccurred', '發生錯誤')}: {error}
        </div>
      </div>
    );
  }

  return (
    <div className="language-pack-manager">
      <h2>{t('common.languagePackManager', '語言包管理')}</h2>

      {/* 創建新語言包表單 */}
      <div className="create-form">
        <h3>{t('common.createNewPack', '創建新語言包')}</h3>
        <form onSubmit={handleCreatePack}>
          <select
            value={newPack.language_code}
            onChange={(e) => handleInputChange('language_code', e.target.value)}
          >
            {supportedLanguages.map(lang => (
              <option key={lang.code} value={lang.code}>{lang.name}</option>
            ))}
          </select>
          <input
            type="text"
            placeholder={t('common.packName', '包名稱')}
            value={newPack.pack_name}
            onChange={(e) => handleInputChange('pack_name', e.target.value)}
            required
          />
          <input
            type="text"
            placeholder={t('common.version', '版本')}
            value={newPack.version}
            onChange={(e) => handleInputChange('version', e.target.value)}
            required
          />
          <label>
            <input
              type="checkbox"
              checked={newPack.is_active}
              onChange={(e) => handleInputChange('is_active', e.target.checked)}
            />
            {t('common.isActive', '啟用')}
          </label>
          <button type="submit">{t('common.create', '創建')}</button>
        </form>
      </div>

      {/* 語言包列表 */}
      <div className="packs-list">
        <h3>{t('common.packsList', '語言包列表')}</h3>
        {loading ? (
          <div className="loading">{t('common.loading', '載入中...')}</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>{t('common.id', 'ID')}</th>
                <th>{t('common.language', '語言')}</th>
                <th>{t('common.packName', '包名稱')}</th>
                <th>{t('common.version', '版本')}</th>
                <th>{t('common.status', '狀態')}</th>
                <th>{t('common.actions', '操作')}</th>
              </tr>
            </thead>
            <tbody>
              {languagePacks.map(pack => (
                <tr key={pack.id}>
                  <td>{pack.id}</td>
                  <td>{supportedLanguages.find(lang => lang.code === pack.language_code)?.name || pack.language_code}</td>
                  <td>
                    {editingPack && editingPack.id === pack.id ? (
                      <input
                        type="text"
                        value={editingPack.pack_name}
                        onChange={(e) => handleInputChange('pack_name', e.target.value)}
                      />
                    ) : (
                      pack.pack_name
                    )}
                  </td>
                  <td>
                    {editingPack && editingPack.id === pack.id ? (
                      <input
                        type="text"
                        value={editingPack.version}
                        onChange={(e) => handleInputChange('version', e.target.value)}
                      />
                    ) : (
                      pack.version
                    )}
                  </td>
                  <td>
                    {editingPack && editingPack.id === pack.id ? (
                      <label>
                        <input
                          type="checkbox"
                          checked={editingPack.is_active}
                          onChange={(e) => handleInputChange('is_active', e.target.checked)}
                        />
                        {t('common.active', '啟用')}
                      </label>
                    ) : (
                      pack.is_active ? t('common.active', '啟用') : t('common.inactive', '停用')
                    )}
                  </td>
                  <td>
                    {editingPack && editingPack.id === pack.id ? (
                      <>
                        <button onClick={handleUpdatePack}>{t('common.save', '保存')}</button>
                        <button onClick={cancelEditing}>{t('common.cancel', '取消')}</button>
                      </>
                    ) : (
                      <>
                        <button onClick={() => startEditing(pack)}>{t('common.edit', '編輯')}</button>
                        <button onClick={() => handleDeletePack(pack.id)}>{t('common.delete', '刪除')}</button>
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

export default LanguagePackManager;