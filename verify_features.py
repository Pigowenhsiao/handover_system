"""
電子交接系統功能實現檢查
確認電子交接系統的核心功能已實現
"""
import os
import sys
from pathlib import Path


def check_core_components():
    """檢查桌面版核心組件"""
    print("檢查核心組件...")

    core_files = [
        "handover_system.py",
        "start_modern_ui.py",
        "auth.py",
        "models.py",
        "requirements.txt",
    ]

    for core_file in core_files:
        if os.path.exists(core_file):
            print(f"✓ {core_file} 存在")
        else:
            print(f"✗ {core_file} 不存在")


def check_frontend_components():
    """檢查前端目錄（若存在）"""
    print("\n檢查前端目錄...")

    frontend_dir = "frontend"
    if not os.path.exists(frontend_dir):
        print("✗ 前端目錄不存在（無法啟動現代化介面）")
        return

    frontend_files = [
        "frontend/main.py",
        "frontend/src/components/language_selector.py",
        "frontend/src/components/attendance_section_optimized.py",
        "frontend/src/components/modern_main_frame.py",
    ]

    for frontend_file in frontend_files:
        if os.path.exists(frontend_file):
            print(f"✓ {frontend_file} 存在")
        else:
            print(f"✗ {frontend_file} 不存在")


def check_models():
    """檢查資料模型"""
    print("\n檢查資料模型...")

    model_paths = [
        "models.py",
    ]

    for model_path in model_paths:
        if os.path.exists(model_path):
            print(f"✓ {model_path} 存在")
        else:
            print(f"✗ {model_path} 不存在")


def check_spec_documents():
    """檢查規格文件"""
    print("\n檢查規格文件...")
    
    spec_paths = [
        "specs/01_multi-language-support/spec.md",
        "specs/02_multilang-labels/spec.md",
        "specs/03_attendance-enhancement/spec.md"
    ]
    
    for spec_path in spec_paths:
        if os.path.exists(spec_path):
            print(f"✓ {spec_path} 存在")
        else:
            print(f"✗ {spec_path} 不存在")


def check_language_resources():
    """檢查語言資源文件"""
    print("\n檢查語言資源文件...")
    
    locales_dir = "frontend/public/locales"
    if os.path.exists(locales_dir):
        print("✓ 語言資源目錄存在")
        
        lang_files = ["ja.json", "zh.json", "en.json"]
        for lang_file in lang_files:
            file_path = os.path.join(locales_dir, lang_file)
            if os.path.exists(file_path):
                print(f"✓ {lang_file} 存在")
            else:
                print(f"✗ {lang_file} 不存在")
    else:
        print("✗ 語言資源目錄不存在")


def main():
    """主函數 - 執行系統功能檢查"""
    print("="*50)
    print("電子交接系統功能實現檢查報告")
    print("="*50)
    
    check_core_components()
    check_frontend_components()
    check_models()
    check_spec_documents()
    check_language_resources()
    
    print("\n" + "="*50)
    print("檢查完成")
    print("如發現缺失文件，請重新運行相應的創建命令")
    print("="*50)


if __name__ == "__main__":
    main()

