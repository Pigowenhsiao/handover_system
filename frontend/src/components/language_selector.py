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
        label_text = f"{self.lang_manager.get_text(self.label_key, self.label_default)}:"
        self.label = ttk.Label(self.frame, text=label_text)
        self.label.pack(side=tk.LEFT, padx=(0, 5))
        
        # 語言選項 - 顯示完整的語言名稱而非代碼
        self.language_options = {
            "ja": "日本語",
            "en": "English", 
            "zh": "中文"
        }
        
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
            width=12
        )
        self.combo.pack(side=tk.LEFT)

        # 設置當前語言
        current_lang_code = self.lang_manager.get_current_language()
        current_lang_name = self.language_options.get(current_lang_code, "日本語")
        self.language_var.set(current_lang_name)

        # 綁定選擇事件
        self.combo.bind('<<ComboboxSelected>>', self.on_language_changed)

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
        label_text = f"{self.lang_manager.get_text(self.label_key, self.label_default)}:"
        self.label.config(text=label_text)

    def update_language_display(self, lang_code):
        """更新語言選擇器的顯示"""
        lang_name = self.language_options.get(lang_code, "日本語")
        self.language_var.set(lang_name)


class MultiLanguageLabel:
    """
    多語言標籤
    根據當前語言自動更新顯示文本
    """
    
    def __init__(self, parent, text_key=None, default_text="", font=None, style=None):
        """
        初始化多語言標籤
        
        Args:
            parent: 父組件
            text_key: 翻譯鍵
            default_text: 默認文本
            font: 字體
            style: 樣式
        """
        self.parent = parent
        self.text_key = text_key
        self.default_text = default_text
        self.font = font
        
        # 創建標籤
        self.label = ttk.Label(parent, text=default_text, font=font, style=style)
    
    def get_widget(self):
        """獲取標籤實例"""
        return self.label
    
    def update_text(self, lang_manager):
        """更新文本"""
        if self.text_key:
            new_text = lang_manager.get_text(self.text_key, self.default_text)
            self.label.config(text=new_text)
    
    def pack(self, **kwargs):
        """包裝方法"""
        self.label.pack(**kwargs)
    
    def grid(self, **kwargs):
        """網格布局方法"""
        self.label.grid(**kwargs)
    
    def config(self, **kwargs):
        """配置方法"""
        self.label.config(**kwargs)


class MultiLanguageButton:
    """
    多語言按鈕
    根據當前語言自動更新顯示文本
    """
    
    def __init__(self, parent, text_key=None, default_text="", command=None, style=None, width=None):
        """
        初始化多語言按鈕
        
        Args:
            parent: 父組件
            text_key: 翻譯鍵
            default_text: 默認文本
            command: 命令回調
            style: 樣式
            width: 寬度
        """
        self.parent = parent
        self.text_key = text_key
        self.default_text = default_text
        self.command = command
        
        # 創建按鈕
        if width:
            self.button = ttk.Button(parent, text=default_text, command=command, style=style, width=width)
        else:
            self.button = ttk.Button(parent, text=default_text, command=command, style=style)
    
    def get_widget(self):
        """獲取按鈕實例"""
        return self.button
    
    def update_text(self, lang_manager):
        """更新文本"""
        if self.text_key:
            new_text = lang_manager.get_text(self.text_key, self.default_text)
            self.button.config(text=new_text)
    
    def pack(self, **kwargs):
        """包裝方法"""
        self.button.pack(**kwargs)
    
    def grid(self, **kwargs):
        """網格布局方法"""
        self.button.grid(**kwargs)
    
    def config(self, **kwargs):
        """配置方法"""
        self.button.config(**kwargs)


class ModernLanguageLabel(ttk.Label):
    """
    現代化多語言標籤
    支援 Material Design 風格
    """
    
    def __init__(self, parent, text_key=None, default_text="", font=None, style=None, **kwargs):
        self.text_key = text_key
        self.default_text = default_text
        
        if font is None:
            font = ('Segoe UI', 10)
        
        super().__init__(parent, text=default_text, font=font, style=style, **kwargs)


# 工具函數
def create_modern_label(parent, text, font_size=10, bold=False, color='text_primary', **kwargs):
    """創建現代化標籤"""
    font = ('Segoe UI', font_size, 'bold' if bold else 'normal')
    
    from frontend.src.components.modern_main_frame import ModernMainFrame
    colors = ModernMainFrame.COLORS
    
    fg = colors.get(color, colors['text_primary'])
    
    return ttk.Label(parent, text=text, font=font, foreground=fg, **kwargs)


def create_modern_button(parent, text, command, style='Accent.TButton', width=None, **kwargs):
    """創建現代化按鈕"""
    if width:
        return ttk.Button(parent, text=text, command=command, style=style, width=width, **kwargs)
    else:
        return ttk.Button(parent, text=text, command=command, style=style, **kwargs)
