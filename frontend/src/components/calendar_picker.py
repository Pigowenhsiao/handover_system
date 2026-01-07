"""Simple date picker helper for Tkinter entry fields."""

from datetime import datetime
import tkinter as tk
from tkinter import ttk


def create_date_picker(parent, var, width=16, translate=None):
    """Create an entry + button date picker stub."""
    frame = ttk.Frame(parent)
    entry = ttk.Entry(frame, textvariable=var, width=width, style="Modern.TEntry")
    entry.pack(side="left", fill="x", expand=True)

    def _set_today():
        today = datetime.now().strftime("%Y-%m-%d")
        var.set(today)

    button_text = "..."
    if translate:
        button_text = translate("common.pickDate", button_text)

    button = ttk.Button(frame, text=button_text, width=3, command=_set_today)
    button.pack(side="left", padx=(4, 0))
    return frame, entry, button
