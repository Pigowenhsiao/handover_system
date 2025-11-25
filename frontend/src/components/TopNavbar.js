import React from 'react';
import { useTranslation } from 'react-i18next';
import LanguageSelector from './LanguageSelector';
import './TopNavbar.css';

const TopNavbar = () => {
  const { t } = useTranslation();

  return (
    <nav className="top-navbar">
      <div className="navbar-brand">
        <h1>{t('header.title', '電子交接系統')}</h1>
      </div>

      <div className="navbar-menu">
        <ul className="nav-links">
          <li><a href="/">{t('navigation.home', '首頁')}</a></li>
          <li><a href="/reports">{t('navigation.reports', '報表')}</a></li>
          <li><a href="/settings">{t('navigation.settings', '設定')}</a></li>
        </ul>
      </div>

      <div className="navbar-right">
        <div className="language-selector-wrapper">
          {/* 語言選擇下拉選單 */}
          <LanguageSelector />
        </div>

        <div className="user-menu">
          <span>{t('common.username', '用戶名稱')}</span>
          <button>{t('header.logout', '登出')}</button>
        </div>
      </div>
    </nav>
  );
};

export default TopNavbar;