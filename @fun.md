# Function Index

Scope: This file lists functions, methods, and their roles across the codebase.

## `handover_system.py`

| Function | Purpose |
| --- | --- |
| `check_dependencies` | Verify required Python packages are installed. |
| `initialize_database` | Initialize database tables and seed defaults. |
| `start_modern_ui` | Launch the modern Tkinter UI. |
| `prompt_continue` | Prompt user to continue (with non-interactive fallback). |
| `main` | Orchestrate startup checks and launch UI. |

## `auth.py`

| Function | Purpose |
| --- | --- |
| `hash_password` | Hash a password using bcrypt. |
| `verify_password` | Verify a password against a bcrypt hash. |

## `models.py`

| Function | Purpose |
| --- | --- |
| `_get_app_root` | Resolve the application root path. |
| `_get_data_dir` | Ensure and return the data directory. |
| `_set_database_fallback_notice` | Record fallback database path notice. |
| `consume_database_fallback_notice` | Read and clear the fallback notice. |
| `get_database_path` | Resolve the effective database path. |
| `_maybe_migrate_database` | Migrate legacy database file if present. |
| `_is_sqlite_busy_error` | Detect SQLite busy/locked errors. |
| `_configure_sqlite` | Apply SQLite PRAGMA settings on connect. |
| `get_db` | Yield a SQLAlchemy session generator. |
| `init_db` | Create tables and seed admin/option data. |
| `_ensure_daily_report_columns` | Add missing columns to `daily_reports`. |
| `_ensure_equipment_log_columns` | Add missing columns to `equipment_logs`. |

### Class: `RetryingSession`

| Method | Purpose |
| --- | --- |
| `commit` | Retry commits on SQLite busy/locked errors. |

### ORM Models

| Class | Purpose |
| --- | --- |
| `User` | User account model. |
| `ShiftOption` | Shift option model. |
| `AreaOption` | Area option model. |
| `DailyReport` | Daily report model with related entries. |
| `AttendanceEntry` | Attendance entry model. |
| `OvertimeEntry` | Overtime entry model. |
| `EquipmentLog` | Equipment log model. |
| `LotLog` | Lot log model. |
| `DelayEntry` | Delay list entry model. |
| `SummaryActualEntry` | Summary actual entry model. |
| `AttendanceSummaryDeleteLog` | Attendance summary delete log model. |

## `run_modern_system.py`

This script is a thin wrapper that calls `handover_system.main` (no local function definitions).

## `start_modern_ui.py`

| Function | Purpose |
| --- | --- |
| `main` | Launch the modern UI directly. |

## `system_check.py`

| Function | Purpose |
| --- | --- |
| `check_python_imports` | Validate required Python imports. |
| `test_database_connection` | Verify database connectivity. |
| `test_language_manager` | Validate language manager behavior. |
| `test_models` | Validate ORM model imports. |
| `main` | Run full system checks. |

## `verify_features.py`

| Function | Purpose |
| --- | --- |
| `check_core_components` | Check existence of core files. |
| `check_frontend_components` | Check existence of frontend files. |
| `check_models` | Check model files. |
| `check_spec_documents` | Check spec document presence. |
| `check_language_resources` | Check language JSON resources. |
| `main` | Run all feature checks. |

## `verify_implementation.py`

This script is procedural only (no function definitions).

## `scripts/build_executable.py`

| Function | Purpose |
| --- | --- |
| `build` | Placeholder build routine. |

## `frontend/main.py`

| Function | Purpose |
| --- | --- |
| `ensure_requests_installed` | Guard UI actions that require `requests`. |
| `main` | Launch the legacy Tkinter UI. |

### Class: `LoginScreen`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize login window. |
| `setup_ui` | Build login UI widgets. |
| `on_language_change` | Handle language selection. |
| `update_language` | Refresh UI strings for current language. |
| `login` | Authenticate against backend API. |

### Class: `LanguageManager`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize language manager and load translations. |
| `load_all_translations` | Load all supported language files. |
| `load_language_translations` | Load a specific language file. |
| `create_default_language_file` | Generate a default language JSON file. |
| `get_default_translations` | Provide built-in default translations. |
| `get_text` | Resolve a translation key with fallback. |
| `set_language` | Set the current language. |
| `get_current_language` | Return current language code. |
| `get_supported_languages` | Return supported language list. |

### Class: `AttendanceSection`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize attendance section UI. |
| `create_ui` | Build attendance input widgets. |
| `validate_attendance_data` | Validate attendance counts. |
| `get_data` | Return current attendance data. |
| `get_widget` | Return root widget. |
| `update_language` | Refresh UI strings for current language. |

### Class: `MainApplication`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize the main application window. |
| `on_closing` | Handle close behavior. |
| `show_login_screen` | Show login flow. |
| `login_success` | Handle successful login. |
| `fetch_current_user` | Fetch current user info from backend. |
| `logout` | Clear user session and UI. |
| `load_master_data` | Load master data from storage. |
| `save_master_data` | Persist master data to storage. |
| `setup_styles` | Configure Tkinter styles. |
| `setup_ui` | Build top-level UI layout. |
| `on_language_change` | Update language across tabs. |
| `update_ui_language` | Refresh all text labels. |
| `update_daily_report_tab_language` | Refresh daily report tab strings. |
| `update_attendance_tab_language` | Refresh attendance tab strings. |
| `update_equipment_tab_language` | Refresh equipment tab strings. |
| `update_lot_log_tab_language` | Refresh lot log tab strings. |
| `update_master_data_tab_language` | Refresh master data tab strings. |
| `update_summary_tab_language` | Refresh summary tab strings. |
| `create_daily_report_tab` | Build daily report tab. |
| `create_attendance_tab` | Build attendance tab. |
| `create_equipment_tab` | Build equipment tab. |
| `create_lot_log_tab` | Build lot log tab. |
| `create_master_data_tab` | Build master data tab. |
| `populate_area_list` | Populate area list UI. |
| `add_area` | Add area to master data. |
| `update_area` | Update selected area. |
| `delete_area` | Remove selected area. |
| `on_area_select` | Handle area selection. |
| `update_summary` | Refresh summary dashboard content. |
| `save_daily_report` | Save daily report input. |
| `save_attendance_record` | Save attendance record input. |
| `browse_equipment_image` | Pick equipment image file. |
| `add_equipment_log` | Add an equipment log entry. |
| `add_lot_log` | Add a lot log entry. |

## `frontend/i18n/language_manager.py`

### Class: `FrontendLanguageManager`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize frontend language manager. |
| `load_all_translations` | Load all language resources. |
| `load_language_translations` | Load a specific language file. |
| `get_default_translations` | Provide built-in defaults. |
| `get_text` | Resolve translation key with fallback. |
| `set_language` | Set current language. |
| `get_current_language` | Return current language. |
| `get_supported_languages` | Return supported language list. |
| `refresh_translations` | Reload translations from disk. |
| `update_translation` | Update a translation value in memory. |

## `frontend/src/utils/theme_manager.py`

| Function | Purpose |
| --- | --- |
| `apply_theme` | Placeholder theme application hook. |

## `frontend/src/utils/theme_helpers.py`

### Class: `ThemeColors`

| Method | Purpose |
| --- | --- |
| `get_colors` | Return light/dark color palette. |
| `get_status_bg_colors` | Return status background colors. |
| `get_status_fg_colors` | Return status foreground colors. |
| `get_status_colors` | Return status colors by rate. |

## `frontend/src/utils/ui_helpers.py`

| Function | Purpose |
| --- | --- |
| `create_section_header` | Build a standard section header frame and label. |
| `create_labeled_input` | Build a labeled input row (entry/combobox). |
| `build_button_row` | Build a button row from declarative specs. |

## `frontend/src/utils/table_helpers.py`

| Function | Purpose |
| --- | --- |
| `clear_tree` | Remove all rows from a Treeview. |
| `configure_treeview_columns` | Apply headings/widths for Treeview columns. |
| `attach_vertical_scrollbar` | Attach a vertical scrollbar to a Treeview. |
| `bind_treeview_context_menu` | Bind right-click to a context menu builder. |

## `frontend/src/utils/i18n_helpers.py`

### Class: `I18nRegistry`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize registry state. |
| `register` | Register a widget for translation updates. |
| `apply` | Apply translations to registered widgets. |
| `clear_page` | Clear page-scoped registrations. |

## `frontend/src/utils/report_helpers.py`

| Function | Purpose |
| --- | --- |
| `build_shift_display_options` | Build shift display values and maps. |
| `resolve_shift_code` | Resolve display label to shift code. |
| `format_report_context_label` | Format report context label text. |

## `frontend/src/utils/settings_store.py`

| Function | Purpose |
| --- | --- |
| `get_settings_path` | Resolve settings file path. |
| `load_settings_data` | Load settings JSON into a dict. |
| `save_settings_data` | Persist settings JSON to disk. |

## `frontend/src/utils/attendance_helpers.py`

| Function | Purpose |
| --- | --- |
| `build_attendance_notes` | Build attendance notes from reason fields. |
| `compute_attendance_totals` | Compute totals and overall attendance rate. |
| `validate_attendance_values` | Validate attendance counts and overtime. |

## `frontend/src/utils/crud_helpers.py`

| Function | Purpose |
| --- | --- |
| `create_crud_manager` | Build CRUD handlers for admin options. |
| `create_treeview_select_handler` | Sync form from Treeview selection. |

## `frontend/src/utils/import_helpers.py`

| Function | Purpose |
| --- | --- |
| `_select_sheet_name` | Prompt for Excel worksheet selection. |
| `open_excel_workbook` | Open workbook and select worksheet. |
| `read_table` | Read CSV/Excel into a DataFrame. |

## `frontend/src/components/attendance_section.py`

### Class: `AttendanceSection`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize attendance UI. |
| `setup_ui` | Build attendance widgets. |
| `validate_attendance_data` | Validate attendance counts. |
| `get_attendance_data` | Get current attendance payload. |
| `set_attendance_data` | Populate attendance fields. |
| `get_widget` | Return root widget. |

## `frontend/src/components/attendance_section_optimized.py`

### Class: `AttendanceSectionOptimized`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize optimized attendance UI. |
| `setup_styles` | Initialize style configuration. |
| `_get_theme_colors` | Resolve theme colors. |
| `_is_dark_theme` | Detect dark theme mode. |
| `_apply_styles` | Apply themed widget styles. |
| `apply_theme` | Apply theme to widgets. |
| `_get_rate_colors` | Choose colors based on rate. |
| `_get_overall_rate_color` | Choose overall rate color. |
| `setup_ui` | Build UI layout. |
| `setup_overtime_section` | Build overtime section. |
| `setup_staff_section` | Build staff sub-section. |
| `setup_statistics_section` | Build statistics section. |
| `update_language` | Refresh UI text for language. |
| `_widget_alive` | Check widget existence. |
| `on_data_change` | Mark data as modified. |
| `update_status_indicator` | Update save status indicator. |
| `calculate_rates` | Compute attendance rates. |
| `update_rate_display` | Update rate labels and indicators. |
| `update_totals` | Update totals and overall rate. |
| `_recalc_absent` | Recalculate absent from scheduled/present. |
| `format_number` | Format integers for display. |
| `validate_attendance_data` | Validate inputs and report errors. |
| `save_attendance_data` | Save attendance via app callbacks. |
| `get_attendance_data` | Collect attendance and overtime data. |
| `set_attendance_data` | Populate attendance and overtime data. |
| `get_widget` | Return root widget. |
| `clear_data` | Clear all input fields. |

| Function | Purpose |
| --- | --- |
| `test_optimized_attendance` | Standalone demo/test for optimized UI. |

## `frontend/src/components/equipment_log_section.py`

### Class: `EquipmentLogSection`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize equipment log UI. |
| `setup_ui` | Build equipment log widgets. |
| `update_ui_language` | Refresh UI text for language. |
| `browse_image` | Choose an image file. |
| `add_equipment_log` | Add equipment log entry. |
| `on_double_click` | Load selected row into input fields. |
| `reset_fields` | Clear input fields. |
| `get_widget` | Return root widget. |
| `load_data` | Populate table from data. |
| `get_data` | Extract table data. |

## `frontend/src/components/lot_log_section.py`

### Class: `LotLogSection`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize lot log UI. |
| `setup_ui` | Build lot log widgets. |
| `update_ui_language` | Refresh UI text for language. |
| `add_lot_log` | Add lot log entry. |
| `on_double_click` | Load selected row into input fields. |
| `reset_fields` | Clear input fields. |
| `get_widget` | Return root widget. |
| `load_data` | Populate table from data. |
| `get_data` | Extract table data. |

## `frontend/src/components/admin_section.py`

### Class: `UserManagementSection`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize user management UI. |
| `setup_ui` | Build user management widgets. |
| `set_current_user` | Update current user context. |
| `_is_admin` | Check admin role. |
| `_ui_ready` | Check UI readiness. |
| `_widget_alive` | Check widget existence. |
| `_apply_access_control` | Enable/disable admin controls. |
| `load_users` | Load users into table. |
| `update_ui_language` | Refresh UI strings. |
| `create_user` | Create a new user. |
| `update_user` | Update selected user. |
| `delete_user` | Delete selected user. |
| `on_tree_select` | Populate form on row selection. |
| `reset_password` | Reset selected user password. |
| `reset_fields` | Clear input fields. |
| `get_widget` | Return root widget. |

### Class: `MasterDataSection`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize master data UI. |
| `setup_ui` | Build master data widgets. |
| `_apply_access_control` | Enable/disable admin controls. |
| `get_widget` | Return root widget. |
| `load_data` | Load shift/area data. |
| `update_ui_language` | Refresh UI strings. |
| `on_shift_select` | Handle shift selection. |
| `on_area_select` | Handle area selection. |
| `add_shift` | Add a shift option. |
| `update_shift` | Update selected shift. |
| `delete_shift` | Remove selected shift. |
| `add_area` | Add an area option. |
| `update_area` | Update selected area. |
| `delete_area` | Remove selected area. |
| `_notify_change` | Notify parent of data changes. |

### Class: `TranslationManagementSection`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize translation management UI. |
| `setup_ui` | Build translation management widgets. |
| `update_ui_language` | Refresh UI strings. |
| `add_translation_resource` | Add a translation entry. |
| `update_translation_resource` | Update selected translation entry. |
| `delete_translation_resource` | Remove selected translation entry. |
| `import_translations` | Import translations from JSON. |
| `export_translations` | Export translations to JSON. |
| `load_translation_data_from_json` | Populate table from JSON data. |
| `on_resource_tree_select` | Populate form from row selection. |
| `reset_resource_fields` | Clear translation input fields. |
| `get_widget` | Return root widget. |

## `frontend/src/components/language_selector.py`

### Class: `LanguageSelector`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize language selector widget. |
| `on_language_changed` | Apply selected language. |
| `get_widget` | Return root widget. |
| `update_text` | Refresh label text. |
| `update_language_display` | Update displayed language name. |

### Class: `MultiLanguageLabel`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize label with translation key. |
| `get_widget` | Return label widget. |
| `update_text` | Refresh label text. |
| `pack` | Pack wrapper. |
| `grid` | Grid wrapper. |
| `config` | Config wrapper. |

### Class: `MultiLanguageButton`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize button with translation key. |
| `get_widget` | Return button widget. |
| `update_text` | Refresh button text. |
| `pack` | Pack wrapper. |
| `grid` | Grid wrapper. |
| `config` | Config wrapper. |

### Class: `ModernLanguageLabel`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize themed label widget. |

| Function | Purpose |
| --- | --- |
| `create_modern_label` | Build a themed label. |
| `create_modern_button` | Build a themed button. |

## `frontend/src/components/calendar_picker.py`

| Function | Purpose |
| --- | --- |
| `create_date_picker` | Build a simple date picker entry + button. |

## `frontend/src/components/password_change_dialog.py`

### Class: `LocalPasswordValidator`

| Method | Purpose |
| --- | --- |
| `validate_strength` | Validate password strength rules. |
| `get_strength_score` | Compute strength score and label. |
| `generate_suggestions` | Produce strength improvement tips. |

### Class: `PasswordChangeDialog`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize password change dialog. |
| `setup_ui` | Build dialog widgets. |
| `update_language` | Refresh UI strings. |
| `toggle_new_password_visibility` | Toggle new password visibility. |
| `toggle_confirm_password_visibility` | Toggle confirm password visibility. |
| `update_password_strength` | Update strength indicator and tips. |
| `change_password` | Validate and submit password change. |

| Function | Purpose |
| --- | --- |
| `test_password_dialog` | Standalone demo for password dialog. |

## `frontend/src/components/main_app_frame.py`

### Class: `MainApplicationFrame`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize main app frame. |
| `setup_ui` | Build top-level UI. |
| `create_content_area` | Build tab container. |
| `create_daily_report_tab` | Build daily report tab. |
| `create_attendance_tab` | Build attendance tab. |
| `create_equipment_tab` | Build equipment tab. |
| `create_lot_tab` | Build lot tab. |
| `create_summary_tab` | Build summary tab. |
| `create_admin_tab` | Build admin tab. |
| `browse_image` | Choose image file. |
| `on_language_changed` | Handle language change event. |
| `update_ui_language` | Refresh UI strings. |
| `show_users` | Placeholder user list action. |
| `add_user` | Placeholder add user action. |
| `edit_user` | Placeholder edit user action. |
| `delete_user` | Placeholder delete user action. |

## `frontend/src/components/modern_main_frame.py`

### Class: `ModernMainFrame`

| Method | Purpose |
| --- | --- |
| `__init__` | Initialize modern UI frame and state. |
| `_t` | Shortcut for translation lookup. |
| `_register_text` | Track widgets for i18n updates. |
| `_apply_i18n` | Apply i18n text to tracked widgets. |
| `_clear_page_i18n` | Clear page-scoped i18n tracking. |
| `_set_status` | Update status label text. |
| `_update_auth_ui` | Refresh auth UI state. |
| `_clear_tree` | Clear a treeview widget. |
| `_load_settings_data` | Load settings JSON. |
| `_save_settings_data` | Save settings JSON. |
| `_load_theme_mode` | Load persisted theme mode. |
| `_persist_theme_setting` | Save current theme mode. |
| `_register_text_widget` | Track text widgets for theme. |
| `_register_canvas_widget` | Track canvas widgets for theme. |
| `_apply_text_widget_colors` | Apply theme colors to text widgets. |
| `_apply_theme_to_fixed_widgets` | Apply theme colors to fixed widgets. |
| `_update_theme_toggle_label` | Update theme toggle text. |
| `toggle_theme` | Toggle light/dark theme. |
| `apply_theme` | Apply a specific theme. |
| `setup_modern_styles` | Configure ttk styles for theme. |
| `setup_login_ui` | Build login UI. |
| `setup_ui` | Build main UI layout. |
| `_show_login_screen` | Switch to login view. |
| `_show_main_ui` | Switch to main view. |
| `create_top_toolbar` | Build top toolbar. |
| `create_sidebar` | Build sidebar navigation. |
| `_set_admin_button_visible` | Show/hide admin nav entry. |
| `create_main_content` | Build main content container. |
| `create_status_bar` | Build status bar. |
| `_update_status_bar_info` | Update status bar info text. |
| `_notify_database_fallback` | Notify about DB fallback path. |
| `show_page` | Navigate to a page. |
| `update_nav_buttons` | Update nav button state. |
| `create_daily_report_page` | Build daily report page. |
| `_daily_scroll_setup` | Configure scrolling for daily page. |
| `create_card` | Create a card container. |
| `create_form_row` | Create a labeled form row. |
| `_load_shift_area_options` | Load shift/area options from DB. |
| `_build_shift_display_options` | Build shift display entries. |
| `_get_month_date_range` | Compute date range for a month. |
| `_format_shift_display` | Format shift display text. |
| `_update_abnormal_filter_options` | Refresh abnormal history filters. |
| `_update_summary_query_filter_options` | Refresh summary query filters. |
| `_create_date_picker` | Create date picker input. |
| `_open_calendar_popup` | Open calendar popup. |
| `create_attendance_page` | Build attendance page. |
| `create_equipment_page` | Build equipment page. |
| `create_lot_page` | Build lot page. |
| `create_summary_page` | Build summary page. |
| `create_summary_query_page` | Build summary query page. |
| `create_abnormal_history_page` | Build abnormal history page. |
| `_abnormal_scroll_setup` | Configure abnormal page scrolling. |
| `_summary_scroll_setup` | Configure summary page scrolling. |
| `_bind_canvas_mousewheel` | Bind mousewheel scrolling. |
| `_update_summary_dashboard_headers` | Refresh summary dashboard headers. |
| `_build_attendance_notes` | Build attendance notes text. |
| `_format_last_modified_display` | Format last-modified display text. |
| `_start_summary_dash_cell_edit` | Begin summary dashboard cell edit. |
| `_end_summary_dash_cell_edit` | End summary dashboard cell edit. |
| `_cancel_summary_dash_cell_edit` | Cancel summary dashboard cell edit. |
| `_commit_summary_dash_cell_edit` | Commit summary dashboard cell edit. |
| `_show_summary_dash_context_menu` | Show summary dashboard context menu. |
| `_delete_summary_dash_rows` | Delete selected summary dashboard rows. |
| `_update_abnormal_history_headers` | Refresh abnormal history headers. |
| `_parse_abnormal_item_id` | Parse abnormal history item id. |
| `_show_abnormal_context_menu` | Show abnormal history context menu. |
| `_delete_abnormal_records` | Delete abnormal history records. |
| `_edit_abnormal_record` | Edit an abnormal history record. |
| `_update_summary_dash_rows` | Refresh summary dashboard rows. |
| `_load_summary_dashboard` | Load summary dashboard data. |
| `_load_abnormal_history` | Load abnormal history data. |
| `_ensure_cjk_font` | Ensure CJK font availability. |
| `_get_chart_theme` | Resolve chart theme settings. |
| `_apply_chart_axes_theme` | Apply chart theme to axes. |
| `_clear_summary_charts` | Clear summary charts. |
| `_render_summary_charts` | Render summary charts. |
| `create_delay_list_page` | Build delay list page. |
| `create_summary_actual_page` | Build summary actual page. |
| `create_admin_page` | Build admin page. |
| `create_settings_page` | Build settings page. |
| `_settings_path` | Resolve settings file path. |
| `_get_display_database_path` | Resolve DB path for display. |
| `_load_system_settings` | Load system settings into UI. |
| `save_system_settings` | Save system settings from UI. |
| `_browse_database_path` | Browse and set DB path. |
| `toggle_sidebar` | Collapse/expand sidebar. |
| `_position_sidebar_toggle` | Position sidebar toggle button. |
| `update_nav_text` | Refresh navigation labels. |
| `_set_navigation_locked` | Lock/unlock navigation. |
| `_reset_report_state` | Reset report context/state. |
| `_flush_inline_edits` | Commit pending inline edits. |
| `_has_pending_imports` | Check pending import buffers. |
| `_has_daily_report_content` | Check for unsaved report content. |
| `_safe_text_value` | Read text widget safely. |
| `_attempt_save_daily_report` | Attempt to save report on exit. |
| `_attempt_save_attendance` | Attempt to save attendance on exit. |
| `_confirm_force_exit` | Prompt for force-exit. |
| `_can_close_app` | Determine if app can close. |
| `_on_app_close` | Handle window close event. |
| `_request_restart` | Request application restart. |
| `toggle_auth` | Toggle login/logout flow. |
| `attempt_login` | Perform login attempt. |
| `logout` | Log out current user. |
| `on_language_changed` | Apply language change across UI. |
| `add_tooltip` | Add tooltip to widget. |
| `_update_admin_tab_texts` | Refresh admin tab text. |
| `_update_shift_values` | Refresh shift value lists. |
| `_get_shift_code` | Map shift display to shift code. |
| `refresh_shift_area_options` | Reload shift/area options. |
| `add_equipment_record` | Add equipment record to report. |
| `view_equipment_history` | Show equipment history. |
| `add_lot_record` | Add lot record to report. |
| `view_lot_list` | Show lot history list. |
| `_open_history_dialog` | Open generic history dialog. |
| `_open_equipment_history_dialog` | Open equipment history dialog. |
| `_open_lot_history_dialog` | Open lot history dialog. |
| `browse_image` | Pick image file for report. |
| `save_basic_info` | Save basic report info. |
| `save_daily_report` | Save report contents. |
| `_save_report` | Persist report and related entries. |
| `reset_daily_report` | Clear daily report fields. |
| `_sync_report_context_from_form` | Sync report context from form fields. |
| `_update_report_context_label` | Update report context display. |
| `_apply_report_date_to_filters` | Apply report date to filters. |
| `get_report_context` | Return current report context. |
| `ensure_report_context` | Require valid report context before actions. |
| `_load_attendance_entries` | Load attendance entries for report. |
| `save_attendance_entries` | Save attendance entries for report. |
| Method | Purpose |
| --- | --- |
| `_update_delay_headers` | Refresh delay list headers. |
| `_update_summary_headers` | Refresh summary headers. |
| `_update_summary_query_headers` | Refresh summary query headers. |
| `_parse_summary_query_item_id` | Parse summary query item id. |
| `_show_summary_query_context_menu` | Show summary query context menu. |
| `_delete_summary_query_rows` | Delete selected summary query rows. |
| `_edit_summary_query_row` | Edit summary query row. |
| `_clear_delay_view` | Clear delay list view. |
| `_ensure_delay_pending_ids` | Ensure pending delay IDs. |
| `_find_delay_pending_record` | Find pending delay record. |
| `_delete_selected_delay_pending` | Delete selected pending delay rows. |
| `_clear_summary_view` | Clear summary view. |
| `_ensure_summary_pending_ids` | Ensure pending summary IDs. |
| `_find_summary_pending_record` | Find pending summary record. |
| `_delete_selected_summary_pending` | Delete selected pending summary rows. |
| `_configure_summary_tags` | Configure summary tag styles. |
| `_summary_row_tags` | Compute summary row tags. |
| `_start_delay_cell_edit` | Begin delay cell edit. |
| `_end_delay_cell_edit` | End delay cell edit. |
| `_cancel_delay_cell_edit` | Cancel delay cell edit. |
| `_commit_delay_cell_edit` | Commit delay cell edit. |
| `_show_delay_context_menu` | Show delay list context menu. |
| `_show_summary_context_menu` | Show summary list context menu. |
| `_delete_selected_summary_rows` | Delete selected summary rows. |
| `_delete_selected_delay_rows` | Delete selected delay rows. |
| `_render_delay_rows` | Render delay rows. |
| `_load_delay_entries` | Load delay entries from DB. |
| `_import_delay_excel` | Import delay list from Excel/CSV. |
| `_upload_delay_pending` | Upload pending delay records. |
| `_edit_delay_dialog` | Edit delay entry dialog. |
| `_load_summary_query_records` | Load summary query results. |
| `_load_summary_actual` | Load summary actual data. |
| `_import_summary_actual_excel` | Import summary actual data from file. |
| `_upload_summary_pending` | Upload pending summary data. |
| `_edit_summary_dialog` | Edit summary entry dialog. |

## `frontend/src/components/LanguageSelector.js`

| Function | Purpose |
| --- | --- |
| `LanguageSelector` | React language selector component. |
| `handleLanguageChange` | Switch i18n language and sync backend. |

## `frontend/src/components/LoadingIndicator.js`

| Function | Purpose |
| --- | --- |
| `LoadingIndicator` | Render a loading overlay. |
| `getDefaultMessage` | Compute default loading message. |
| `withLoading` | HOC to wrap components with loading state. |
| `useLoading` | Hook to manage loading state. |
| `executeWithLoading` | Execute async function with loading state. |

## `frontend/src/components/LoginForm.js`

| Function | Purpose |
| --- | --- |
| `LoginForm` | React login form component. |
| `handleChange` | Update form state from inputs. |
| `handleSubmit` | Submit login form (placeholder). |

## `frontend/src/components/TopNavbar.js`

| Function | Purpose |
| --- | --- |
| `TopNavbar` | Render top navigation bar. |

## `frontend/src/components/Trans.js`

| Function | Purpose |
| --- | --- |
| `Trans` | Simple translation wrapper component. |

## `frontend/src/components/admin/LanguageImport.js`

| Function | Purpose |
| --- | --- |
| `LanguageImport` | UI for bulk import of translation resources. |
| `handleFileChange` | Validate and store selected JSON file. |
| `handleImport` | Parse JSON and call bulk import API. |
| `isValidJsonStructure` | Validate JSON structure. |
| `flattenJsonToResources` | Flatten nested JSON to resource list. |

## `frontend/src/pages/admin/LanguagePackManager.js`

| Function | Purpose |
| --- | --- |
| `LanguagePackManager` | Manage language packs in admin UI. |
| `fetchLanguagePacks` | Load language packs from API. |
| `handleInputChange` | Update form state. |
| `handleCreatePack` | Create a language pack via API. |
| `handleUpdatePack` | Update a language pack via API. |
| `handleDeletePack` | Delete a language pack via API. |
| `startEditing` | Enter edit mode for a pack. |
| `cancelEditing` | Exit edit mode. |

## `frontend/src/pages/admin/LanguageResourceManager.js`

| Function | Purpose |
| --- | --- |
| `LanguageResourceManager` | Manage translation resources in admin UI. |
| `fetchResources` | Load resources from API. |
| `handleInputChange` | Update form state. |
| `handleCreateResource` | Create resource via API. |
| `handleUpdateResource` | Update resource via API. |
| `handleDeleteResource` | Delete resource via API. |
| `startEditing` | Enter edit mode for a resource. |
| `cancelEditing` | Exit edit mode. |

## `frontend/src/hooks/useLanguageSwitcher.js`

| Function | Purpose |
| --- | --- |
| `useLanguageSwitcher` | Hook to manage language switching. |
| `updateLanguageOnServer` | Sync language preference to backend. |
| `switchLanguage` | Change i18n language and persist preference. |
| `handleLanguageChange` | Sync local state on language change. |

## `frontend/src/contexts/LanguageContext.js`

| Function | Purpose |
| --- | --- |
| `useLanguage` | Hook to access language context. |
| `LanguageProvider` | Context provider for language state. |
| `changeLanguage` | Change language and persist preference. |
| `initializeLanguage` | Initialize language from storage. |
| `handleLanguageChange` | Sync local state on language change. |

## `frontend/src/utils/localization.js`

| Function | Purpose |
| --- | --- |
| `formatNumber` | Localize number formatting. |
| `formatPercent` | Localize percent formatting. |
| `formatDate` | Localize date formatting. |
| `formatTime` | Localize time formatting. |
| `formatDateTime` | Localize date-time formatting. |
| `formatCurrency` | Localize currency formatting. |
| `getDatePattern` | Return date format options per language. |
| `getTimePattern` | Return time format options per language. |
| `localizedCompare` | Locale-aware string comparison. |

## `frontend/src/utils/languageStorage.js`

| Function | Purpose |
| --- | --- |
| `storeLanguagePreference` | Store language preference in localStorage. |
| `getLanguagePreference` | Retrieve language preference from localStorage. |
| `clearLanguagePreference` | Clear stored language preference. |
| `isLanguagePreferenceValid` | Validate stored preference. |
| `updateLanguagePreference` | Update preference and optionally sync to API. |

## `frontend/src/i18n/config.js`

| Function | Purpose |
| --- | --- |
| `setDirection` | Set document text direction and lang. |

## `frontend/src/i18n/switcher.js`

| Function | Purpose |
| --- | --- |
| `switchLanguage` | Change language and persist preference. |
| `getCurrentLanguage` | Get current i18n language. |
| `getSupportedLanguages` | List supported languages. |
| `getLanguageName` | Resolve display name for language code. |
| `getLanguageFlag` | Resolve flag emoji for language code. |
| `isLanguageSupported` | Validate language code support. |

## `frontend/src/i18n/preload.js`

| Function | Purpose |
| --- | --- |
| `preloadCommonResources` | Preload common namespaces. |
| `preloadPageResources` | Preload namespaces for a page. |
| `smartPreload` | Predict and preload likely resources. |
| `predictNextPages` | Predict next pages from current page. |
| `preloadAllLanguagesCommonResources` | Preload common resources for all languages. |
| `checkResourcesAvailability` | Check cached/loaded resources. |
| `setupProgressiveLoading` | Attach progress callbacks to i18n loading. |
| `preloadRoleBasedResources` | Preload namespaces based on role. |
| `startupPreload` | Run app startup preloading flow. |

## `frontend/src/i18n/lazyLoad.js`

| Function | Purpose |
| --- | --- |
| `loadNamespaces` | Load i18n namespaces on demand. |
| `preloadCommonNamespaces` | Preload common namespaces. |
| `loadPageNamespaces` | Load page-specific namespaces. |
| `configureLazyLoading` | Configure i18n lazy load settings. |
| `cacheNamespaceResources` | Add resources to i18n cache. |
| `loadLanguage` | Load a language pack. |
| `isNamespaceLoaded` | Check if namespace is loaded. |
| `preloadLanguagesAndNamespaces` | Preload namespaces for languages. |

## `frontend/src/i18n/fallback.js`

| Function | Purpose |
| --- | --- |
| `setFallbackLanguages` | Configure fallback order for a language. |
| `hasTranslation` | Check if translation key exists. |
| `getTranslationWithFallback` | Get translation with fallback logic. |
| `setupMissingTranslationHandler` | Attach missing-key handler. |
| `configureFallback` | Configure i18n fallback options. |

## `frontend/src/i18n/detector.js`

| Function | Purpose |
| --- | --- |
| `getBrowserLanguage` | Detect browser language. |
| `mapToSupportedLanguage` | Map browser lang to supported codes. |
| `detectRecommendedLanguage` | Compute recommended language. |
| `autoSetLanguageFromBrowser` | Auto switch based on browser settings. |
| `initLanguageDetector` | Initialize language detection. |
| `getLanguageName` | Convert code to display name. |
| `getDetectedLanguages` | Report detection details. |

## `frontend/src/i18n/cache.js`

| Function | Purpose |
| --- | --- |
| `generateCacheKey` | Build cache key for language/namespace. |
| `generateTimestampKey` | Build timestamp key. |
| `generateSizeKey` | Build size key. |
| `isCacheValid` | Check cache expiry. |
| `isStorageAvailable` | Check localStorage space. |
| `getCachedResources` | Read cached resources. |
| `setCachedResources` | Write resources to cache. |
| `clearCache` | Clear a language/namespace cache. |
| `clearAllCache` | Clear all i18n caches. |
| `cleanupOldCaches` | Cleanup expired caches. |
| `getCacheStats` | Report cache usage statistics. |
| `preloadResources` | Preload resources into cache. |
| `implementLRUCache` | Enable LRU cache behavior. |
| `compressCacheData` | Compress cache data string. |
| `decompressCacheData` | Decompress cache data string. |

## `tests/unit_tests.py`

| Function | Purpose |
| --- | --- |
| `test_placeholder` | Placeholder unit test. |

## `tests/security_tests.py`

| Function | Purpose |
| --- | --- |
| `test_security_placeholder` | Placeholder security test. |

## `tests/usability_tests.py`

| Function | Purpose |
| --- | --- |
| `test_usability_placeholder` | Placeholder usability test. |

## `tests/integration_tests.py`

| Function | Purpose |
| --- | --- |
| `test_integration_placeholder` | Placeholder integration test. |

## `tests/performance_tests.py`

| Function | Purpose |
| --- | --- |
| `test_performance_placeholder` | Placeholder performance test. |

## `tests/test_modern_ui.py`

| Function | Purpose |
| --- | --- |
| `test_modern_ui_components` | Run smoke checks for modern UI. |
| `test_ui_features` | Print feature checklist for UI. |
| `generate_test_report` | Print a consolidated test report. |

## `tests/final_integration_test.py`

| Function | Purpose |
| --- | --- |
| `test_final_integration_placeholder` | Placeholder final integration test. |

