import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import './LoadingIndicator.css';

// 加載狀態類型
const LoadingType = {
  INITIAL: 'initial',      // 初始加載
  LANGUAGE: 'language',    // 語言資源加載
  DATA: 'data',           // 數據加載
  SUBMIT: 'submit',       // 表單提交
  CUSTOM: 'custom'        // 自定義加載
};

const LoadingIndicator = ({ 
  loading = false, 
  type = LoadingType.CUSTOM, 
  message = null,
  children = null,
  showDelay = 300  // 延遲顯示時間（毫秒），避免短暫閃爍
}) => {
  const { t } = useTranslation();
  const [showLoader, setShowLoader] = useState(false);

  // 根據加載類型獲取默認消息
  const getDefaultMessage = () => {
    switch (type) {
      case LoadingType.INITIAL:
        return t('common.loading', '載入中...');
      case LoadingType.LANGUAGE:
        return t('common.loadingLanguageResources', '載入語言資源中...');
      case LoadingType.DATA:
        return t('common.loadingData', '載入數據中...');
      case LoadingType.SUBMIT:
        return t('common.processing', '處理中...');
      default:
        return t('common.loading', '載入中...');
    }
  };

  // 使用計時器控制延遲顯示
  useEffect(() => {
    let timer;
    
    if (loading) {
      timer = setTimeout(() => {
        setShowLoader(true);
      }, showDelay);
    } else {
      setShowLoader(false);
    }
    
    return () => {
      if (timer) clearTimeout(timer);
    };
  }, [loading, showDelay]);

  // 如果不需要顯示加載指示器，直接返回子組件
  if (!loading || !showLoader) {
    return children || null;
  }

  return (
    <div className="loading-overlay">
      <div className="loading-content">
        <div className="loading-spinner">
          <div className="spinner-circle"></div>
          <div className="spinner-circle circle-2"></div>
          <div className="spinner-circle circle-3"></div>
        </div>
        <div className="loading-text">
          {message || getDefaultMessage()}
        </div>
      </div>
    </div>
  );
};

// 高階組件：為組件添加加載狀態
export const withLoading = (WrappedComponent, loadingPropName = 'loading') => {
  return ({ [loadingPropName]: loading, ...props }) => {
    if (loading) {
      return (
        <LoadingIndicator loading={true} type={LoadingType.DATA}>
          <WrappedComponent {...props} />
        </LoadingIndicator>
      );
    }
    
    return <WrappedComponent {...props} />;
  };
};

// Hook：簡化加載狀態管理
export const useLoading = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const executeWithLoading = async (asyncFunction) => {
    try {
      setLoading(true);
      setError(null);
      const result = await asyncFunction();
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { loading, error, setLoading, executeWithLoading };
};

export { LoadingType, withLoading, useLoading };
export default LoadingIndicator;