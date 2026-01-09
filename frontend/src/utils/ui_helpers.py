"""UI helper functions for shared layout patterns."""

from __future__ import annotations
from typing import Callable, Dict, Tuple, Any

import tkinter as tk
from tkinter import ttk


def create_section_header(
    parent: tk.Widget,
    text: str,
    *,
    style: str | None = None,
    font: tuple[str, int, str] | None = None,
) -> Tuple[ttk.Frame, ttk.Label]:
    frame = ttk.Frame(parent)
    label = ttk.Label(frame, text=text, style=style, font=font)
    label.pack(side="left")
    return frame, label


def create_labeled_input(
    parent: tk.Widget,
    row: int,
    text: str,
    *,
    label_column: int = 0,
    field_column: int = 1,
    variable: tk.StringVar | None = None,
    widget_type: str = "entry",
    width: int = 20,
    values: list[str] | None = None,
    label_font: tuple[str, int, str] | None = None,
    entry_style: str | None = None,
    label_padx: int = 0,
    label_pady: int = 0,
    field_padx: int = 0,
    field_pady: int = 0,
    column_span: int = 1,
    state: str | None = None,
    widget_kwargs: Dict[str, Any] | None = None,
) -> Tuple[ttk.Label, ttk.Entry | ttk.Combobox, tk.StringVar]:
    label = ttk.Label(parent, text=text, font=label_font)
    label.grid(
        row=row,
        column=label_column,
        sticky="w",
        padx=label_padx,
        pady=label_pady,
    )

    if variable is None:
        variable = tk.StringVar()

    widget_opts = dict(widget_kwargs or {})
    if widget_type == "combo":
        widget = ttk.Combobox(
            parent,
            textvariable=variable,
            values=values or [],
            state=state or "readonly",
            width=width,
            **widget_opts,
        )
    else:
        widget = ttk.Entry(
            parent,
            textvariable=variable,
            width=width,
            style=entry_style,
            **widget_opts,
        )
        if state:
            widget.configure(state=state)

    widget.grid(
        row=row,
        column=field_column,
        sticky="ew",
        padx=(field_padx, 0),
        pady=field_pady,
        columnspan=column_span,
    )
    parent.columnconfigure(field_column, weight=1)
    return label, widget, variable


def build_button_row(
    parent: tk.Widget,
    specs: list[Dict[str, Any]],
    *,
    default_side: str = tk.LEFT,
) -> Tuple[ttk.Frame, Dict[str, ttk.Button]]:
    frame = ttk.Frame(parent)
    buttons = {}
    for spec in specs:
        key = spec.get("key")
        options = dict(spec.get("options", {}))
        btn = ttk.Button(frame, **options)
        pack_opts = dict(spec.get("pack", {}))
        if "side" not in pack_opts:
            pack_opts["side"] = spec.get("side", default_side)
        btn.pack(**pack_opts)
        if key:
            buttons[key] = btn
    return frame, buttons


def create_treeview_with_scrollbars(
    parent: tk.Widget,
    columns: tuple[str, ...],
    header_keys: list[tuple[str, str]],
    widths: Dict[str, int] | None = None,
    anchors: Dict[str, str] | None = None,
    stretchable_cols: list[str] | None = None,
    height: int = 14,
    selectmode: str | None = None,
    vertical_scrollbar: bool = True,
    horizontal_scrollbar: bool = False,
    use_grid_layout: bool = False,
    double_click_handler: Callable[[Any], None] | None = None,
    context_menu_handler: Callable[[Any], None] | None = None,
    translate: Callable[[str, str], str] | None = None,
    tree_config: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    """
    Unified function to create a Treeview with scrollbars and configure headers.

    Args:
        parent: Parent widget
        columns: Tuple of column names
        header_keys: List of (i18n_key, default_text) tuples for headings
        widths: Dict mapping column names to widths
        anchors: Dict mapping column names to anchor positions
        stretchable_cols: List of column names that can stretch
        height: Treeview height (default: 14)
        selectmode: Selection mode ("extended", "browse", or None)
        vertical_scrollbar: Whether to show vertical scrollbar (default: True)
        horizontal_scrollbar: Whether to show horizontal scrollbar (default: False)
        use_grid_layout: Use grid layout instead of pack (default: False)
        double_click_handler: Callback for <Double-1> event
        context_menu_handler: Callback for <Button-3> event
        translate: i18n translate function
        tree_config: Additional configuration for Treeview widget

    Returns:
        Dict with tree, v_scrollbar, h_scrollbar, and configure function
    """
    tree_config = tree_config or {}

    tree = ttk.Treeview(
        parent,
        columns=columns,
        show="headings",
        height=height,
        **({} if selectmode is None else {"selectmode": selectmode}),
        **tree_config,
    )

    v_scrollbar = None
    h_scrollbar = None

    if use_grid_layout:
        parent.columnconfigure(0, weight=1)
        parent.rowconfigure(0, weight=1)
        tree.grid(row=0, column=0, sticky="nsew")
        if vertical_scrollbar:
            v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=v_scrollbar.set)
            v_scrollbar.grid(row=0, column=1, sticky="ns")
        if horizontal_scrollbar:
            h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
            tree.configure(xscrollcommand=h_scrollbar.set)
            h_scrollbar.grid(row=1, column=0, sticky="ew")
    else:
        tree.pack(side="left", fill="both", expand=True)
        if vertical_scrollbar:
            v_scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=v_scrollbar.set)
            v_scrollbar.pack(side="right", fill="y")
        if horizontal_scrollbar:
            h_scrollbar = ttk.Scrollbar(parent, orient="horizontal", command=tree.xview)
            tree.configure(xscrollcommand=h_scrollbar.set)
            h_scrollbar.pack(side="bottom", fill="x")

    if double_click_handler:
        tree.bind("<Double-1>", double_click_handler)
    if context_menu_handler:
        tree.bind("<Button-3>", context_menu_handler)

    def configure_tree() -> None:
        """Configure headers and columns - can be called on language change"""
        if translate:
            for col, (key, default) in zip(columns, header_keys):
                tree.heading(col, text=translate(key, default))
        for col in columns:
            config = {"width": widths.get(col, 100) if widths else 100}
            if stretchable_cols:
                config["stretch"] = col in stretchable_cols
            if anchors:
                config["anchor"] = anchors.get(col, "center")
            tree.column(col, **config)

    configure_tree()
    return {
        "tree": tree,
        "v_scrollbar": v_scrollbar,
        "h_scrollbar": h_scrollbar,
        "configure": configure_tree,
    }
