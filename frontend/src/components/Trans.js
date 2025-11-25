import React from 'react';
import { useTranslation } from 'react-i18next';

/**
 * 通用翻譯組件
 * 提供簡單的界面元素翻譯功能
 */
const Trans = ({ i18nKey, defaultValue, ...props }) => {
  const { t } = useTranslation();
  
  // 如果提供了額外的屬性（如樣式），則在span元素中使用
  if (Object.keys(props).length > 0) {
    return (
      <span {...props}>
        {t(i18nKey, defaultValue)}
      </span>
    );
  }
  
  // 否則直接返回翻譯文本
  return t(i18nKey, defaultValue);
};

export default Trans;