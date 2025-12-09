"""
密碼強度驗證工具
提供密碼強度檢查和安全性相關功能
"""
import re
from typing import Tuple, List, Dict


class PasswordValidator:
    """密碼強度驗證器"""
    
    @staticmethod
    def validate_strength(password: str) -> Tuple[bool, List[str]]:
        """
        驗證密碼強度
        
        Args:
            password: 要驗證的密碼
            
        Returns:
            Tuple[是否有效, 錯誤訊息列表]
        """
        errors = []
        
        if len(password) < 8:
            errors.append("密碼長度至少需要 8 個字元")
        
        if len(password) > 128:
            errors.append("密碼長度不能超過 128 個字元")
        
        if not re.search(r"[A-Z]", password):
            errors.append("密碼必須包含至少一個大寫字母")
        
        if not re.search(r"[a-z]", password):
            errors.append("密碼必須包含至少一個小寫字母")
        
        if not re.search(r"\d", password):
            errors.append("密碼必須包含至少一個數字")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            errors.append("密碼必須包含至少一個特殊字元 (!@#$%^&*(),.?:{}|<>)")
        
        # 檢查常見密碼
        common_passwords = [
            "12345678", "password", "admin123", "123456789", "qwerty123",
            "password123", "admin", "123456", "1234567890", "abc123"
        ]
        if password.lower() in common_passwords:
            errors.append("密碼太常見，請選擇更安全的密碼")
        
        # 檢查連續字元
        if re.search(r'(.)\‍{2,}', password):  # 修正 Unicode 問題
            errors.append("密碼不能包含 3 個以上的連續相同字元")
        
        if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            errors.append("密碼不能包含連續的數字或字母序列")
        
        return len(errors) == 0, errors
    
    @staticmethod
    def get_strength_score(password: str) -> Tuple[int, str, str]:
        """
        計算密碼強度分數
        
        Args:
            password: 要評分的密碼
            
        Returns:
            Tuple[分數(0-100), 強度等級(weak/medium/strong/very_strong), 描述]
        """
        score = 0
        
        # 長度分數
        length = len(password)
        if length >= 8:
            score += 10
        if length >= 10:
            score += 10
        if length >= 12:
            score += 10
        if length >= 16:
            score += 10
        
        # 字元類型分數
        if re.search(r"[a-z]", password):
            score += 15
        if re.search(r"[A-Z]", password):
            score += 15
        if re.search(r"\d", password):
            score += 15
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 15
        
        # 多樣性加分
        types_count = sum([
            bool(re.search(r"[a-z]", password)),
            bool(re.search(r"[A-Z]", password)),
            bool(re.search(r"\d", password)),
            bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        ])
        if types_count >= 3:
            score += 10
        
        # 確定強度等級
        if score < 30:
            level = "weak"
            desc = "密碼強度弱，建議使用更複雜的密碼"
        elif score < 50:
            level = "medium"
            desc = "密碼強度中等，還可以更安全"
        elif score < 80:
            level = "strong"
            desc = "密碼強度良好"
        else:
            level = "very_strong"
            desc = "密碼強度非常強！"
        
        return min(score, 100), level, desc
    
    @staticmethod
    def generate_suggestions(password: str) -> List[str]:
        """
        生成密碼改進建議
        
        Args:
            password: 當前密碼
            
        Returns:
            改進建議列表
        """
        suggestions = []
        
        if len(password) < 12:
            suggestions.append("建議將密碼長度增加到 12 個字元以上")
        
        if not re.search(r"[A-Z]", password):
            suggestions.append("添加大寫字母以提高安全性")
        
        if not re.search(r"[a-z]", password):
            suggestions.append("添加小寫字母以提高安全性")
        
        if not re.search(r"\d", password):
            suggestions.append("添加數字以提高安全性")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            suggestions.append("添加特殊字元 (!@#$%^&*(),.?:{}|<>) 以提高安全性")
        
        if re.search(r'(.)\1{2,}', password):
            suggestions.append("避免使用連續重複的字元")
        
        if re.search(r'(012|123|234|345|456|567|678|789|890|abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)', password.lower()):
            suggestions.append("避免使用連續的字元序列")
        
        if password.lower() in ["password", "admin", "123456"]:
            suggestions.append("避免使用常見的字詞")
        
        return suggestions
    
    @staticmethod
    def mask_password(password: str) -> str:
        """
        遮罩密碼以便顯示
        
        Args:
            password: 原始密碼
            
        Returns:
            遮罩後的字串（只顯示第一和最後一個字元）
        """
        if len(password) <= 2:
            return "*" * len(password)
        return password[0] + "*" * (len(password) - 2) + password[-1]


# 全域實例
password_validator = PasswordValidator()
