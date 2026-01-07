"""Theme color helpers for the modern UI."""


class ThemeColors:
    """Color palette utilities for light/dark themes and status colors."""

    LIGHT_COLORS = {
        "primary": "#1E88E5",
        "primary_light": "#6AB7FF",
        "primary_dark": "#005CB2",
        "accent": "#FFB300",
        "success": "#2E7D32",
        "warning": "#F57C00",
        "error": "#C62828",
        "background": "#F5F7FB",
        "surface": "#FFFFFF",
        "text_primary": "#212121",
        "text_secondary": "#616161",
        "divider": "#E0E0E0",
        "sidebar": "#263238",
        "sidebar_active": "#37474F",
    }

    DARK_COLORS = {
        "primary": "#90CAF9",
        "primary_light": "#BBDEFB",
        "primary_dark": "#64B5F6",
        "accent": "#FFD54F",
        "success": "#81C784",
        "warning": "#FFB74D",
        "error": "#E57373",
        "background": "#121212",
        "surface": "#1E1E1E",
        "text_primary": "#E0E0E0",
        "text_secondary": "#B0B0B0",
        "divider": "#2C2C2C",
        "sidebar": "#1F2933",
        "sidebar_active": "#33404D",
    }

    @staticmethod
    def get_colors(is_dark=False):
        return ThemeColors.DARK_COLORS if is_dark else ThemeColors.LIGHT_COLORS

    @staticmethod
    def get_status_bg_colors(is_dark):
        if is_dark:
            return {
                "good": "#1B3B2F",
                "warning": "#4A3B1B",
                "danger": "#4A1B1B",
                "modified": "#1A2C4A",
            }
        return {
            "good": "#E8F5E9",
            "warning": "#FFF3E0",
            "danger": "#FFEBEE",
            "modified": "#E3F2FD",
        }

    @staticmethod
    def get_status_fg_colors(is_dark):
        if is_dark:
            return {
                "good": "#81C784",
                "warning": "#FFB74D",
                "danger": "#E57373",
                "modified": "#90CAF9",
            }
        return {
            "good": "#2E7D32",
            "warning": "#F57C00",
            "danger": "#C62828",
            "modified": "#1565C0",
        }

    @staticmethod
    def get_status_colors(rate, is_dark):
        if rate >= 85:
            return ("#81C784", "#A5D6A7") if is_dark else ("#2E7D32", "#66BB6A")
        if rate >= 70:
            return ("#FFB74D", "#FFE082") if is_dark else ("#F57C00", "#FFB74D")
        return ("#E57373", "#EF9A9A") if is_dark else ("#C62828", "#EF5350")
