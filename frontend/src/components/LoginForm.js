import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import './LoginForm.css';

const LoginForm = () => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('登錄表單提交:', formData);
    // 這裡添加實際的登錄邏輯
  };

  return (
    <div className="login-form-container">
      <h2>{t('login.title', '登錄')}</h2>
      <form onSubmit={handleSubmit} className="login-form">
        <div className="form-group">
          <label htmlFor="username">
            {t('login.username', '使用者名稱')}
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder={t('login.username', '使用者名稱')}
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password">
            {t('login.password', '密碼')}
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder={t('login.password', '密碼')}
            required
          />
        </div>
        
        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              name="rememberMe"
            />
            {t('login.rememberMe', '記住我')}
          </label>
        </div>
        
        <button type="submit" className="login-button">
          {t('login.signIn', '登入')}
        </button>
        
        <div className="form-footer">
          <a href="#forgot-password">
            {t('login.forgotPassword', '忘記密碼？')}
          </a>
        </div>
      </form>
    </div>
  );
};

export default LoginForm;