"""
語言選擇器組件
實現前端語言切換功能，包含多語言標籤和按鈕
"""

import tkinter as tk
from tkinter import ttk


class LanguageSelector:
    """
    語言選擇器組件
    提供界面讓用戶選擇系統顯示語言（日文、中文、英文）
    """

    def __init__(self, parent, lang_manager, callback=None):
        """
        初始化語言選擇器

        Args:
            parent: 父組件
            lang_manager: 語言管理器實例
            callback: 語言切換後的回調函數
        """
        self.parent = parent
        self.lang_manager = lang_manager
        self.callback = callback

        # 創建界面元素
        self.frame = ttk.Frame(parent)

        # 標籤
        self.label_key = "header.languageSwitch"
        self.label_default = "語言切換"
        label_text = (
            f"{self.lang_manager.get_text(self.label_key, self.label_default)}:"
        )
        self.label = ttk.Label(self.frame, text=label_text)
        self.label.pack(side=tk.LEFT, padx=(0, 5))

        # 語言選項 - 顯示完整的語言名稱而非代碼
        self.language_options = {"ja": "日本語", "en": "English", "zh": "中文"}

        # 創建反向映射，從顯示名稱到代碼
        self.reverse_language_map = {v: k for k, v in self.language_options.items()}

        # 語言變量
        self.language_var = tk.StringVar()

        # 創建下拉選單
        language_values = sorted(self.language_options.values(), key=str.lower)
        self.combo = ttk.Combobox(
            self.frame,
            textvariable=self.language_var,
            values=language_values,
            state="readonly",
            width=12,
        )
        self.combo.pack(side=tk.LEFT)

        # 設置當前語言
        current_lang_code = self.lang_manager.get_current_language()
        current_lang_name = self.language_options.get(current_lang_code, "日本語")
        self.language_var.set(current_lang_name)

        # 綁定選擇事件
        self.combo.bind("<<ComboboxSelected>>", self.on_language_changed)

    def on_language_changed(self, event):
        """處理語言選擇變化"""
        selected_name = self.language_var.get()

        # 從顯示名稱獲取語言代碼
        lang_code = self.reverse_language_map.get(selected_name)

        if lang_code:
            # 更新語言管理器中的當前語言
            self.lang_manager.set_language(lang_code)

            # 如果提供了回調函數，則執行
            if self.callback:
                self.callback(lang_code)

    def get_widget(self):
        """獲取組件主框架"""
        return self.frame

    def update_text(self):
        """更新語言選擇器標籤文字"""
        label_text = (
            f"{self.lang_manager.get_text(self.label_key, self.label_default)}:"
        )
        self.label.config(text=label_text)

    def update_language_display(self, lang_code):
        """更新語言選擇器的顯示"""
        lang_name = self.language_options.get(lang_code, "日本語")
        self.language_var.set(lang_name)
