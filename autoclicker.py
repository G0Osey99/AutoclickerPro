import sys
import time
import random
import json
import os
from collections import deque
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QCheckBox, QRadioButton, QComboBox, QFrame,
                              QButtonGroup, QTabWidget, QGridLayout)
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QIntValidator, QDoubleValidator
import pyautogui
import keyboard
import threading

pyautogui.PAUSE = 0

class AutoClickerSignals(QObject):
    update_stats = pyqtSignal(str, int, int, int)
    status_changed = pyqtSignal(str, str)

class ModernAutoClicker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Auto Clicker Pro")
        self.setFixedSize(420, 540)
        
        # State
        self.running = False
        self.paused = False
        self.click_count = 0
        self.cycles_count = 0
        self.start_time = None
        self.click_times = deque()
        self.config_file = "autoclicker_config.json"
        
        # Signals
        self.signals = AutoClickerSignals()
        self.signals.update_stats.connect(self.update_ui_stats)
        self.signals.status_changed.connect(self.update_status)
        
        self.setup_ui()
        self.load_config()
        self.setup_hotkey()
        
    def setup_ui(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #0f172a;
            }
            QLabel {
                color: #e2e8f0;
                font-size: 12px;
            }
            QLabel#title {
                color: #fff;
                font-size: 18px;
                font-weight: bold;
            }
            QLabel#statLabel {
                color: #94a3b8;
                font-size: 10px;
            }
            QLabel#statValue {
                color: #3b82f6;
                font-size: 20px;
                font-weight: bold;
            }
            QLabel#timerLabel {
                color: #f8fafc;
                font-size: 16px;
                font-weight: bold;
                font-family: 'Consolas', 'Courier New', monospace;
            }
            QLabel#fieldLabel {
                color: #cbd5e1;
                font-size: 11px;
            }
            QLabel#hotkeyBadge {
                background-color: #334155;
                color: #f1f5f9;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
                border: 2px solid #334155;
            }
            QPushButton#hotkeyBadge {
                background-color: #334155;
                color: #f1f5f9;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 10px;
                border: 2px solid #334155;
                min-height: 16px;
            }
            QPushButton#hotkeyBadge:hover {
                background-color: #475569;
                border-color: #3b82f6;
            }
            QPushButton#hotkeyBadge:pressed {
                background-color: #1e293b;
            }
            QFrame#statsCard {
                background-color: #1e293b;
                border-radius: 8px;
                border: 1px solid #334155;
            }
            QLineEdit {
                background-color: #0f172a;
                color: #f8fafc;
                border: 2px solid #334155;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
            }
            QComboBox {
                background-color: #0f172a;
                color: #f8fafc;
                border: 2px solid #334155;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 12px;
                min-height: 18px;
            }
            QComboBox:hover {
                border-color: #475569;
            }
            QComboBox::drop-down {
                border: none;
                width: 18px;
            }
            QComboBox::down-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 5px solid #94a3b8;
                margin-right: 6px;
            }
            QComboBox QAbstractItemView {
                background-color: #1e293b;
                color: #f8fafc;
                border: 1px solid #334155;
                selection-background-color: #3b82f6;
            }
            QCheckBox {
                color: #e2e8f0;
                font-size: 12px;
                spacing: 6px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border-radius: 3px;
                border: 2px solid #475569;
                background-color: #0f172a;
            }
            QCheckBox::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
            }
            QCheckBox::indicator:hover {
                border-color: #3b82f6;
            }
            QRadioButton {
                color: #e2e8f0;
                font-size: 12px;
                spacing: 6px;
            }
            QRadioButton::indicator {
                width: 14px;
                height: 14px;
                border-radius: 7px;
                border: 2px solid #475569;
                background-color: #0f172a;
            }
            QRadioButton::indicator:checked {
                background-color: #3b82f6;
                border-color: #3b82f6;
            }
            QRadioButton::indicator:hover {
                border-color: #3b82f6;
            }
            QPushButton {
                background-color: #3b82f6;
                color: #ffffff;
                border: none;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                font-weight: bold;
                min-height: 24px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
            QPushButton:pressed {
                background-color: #1d4ed8;
            }
            QPushButton:disabled {
                background-color: #334155;
                color: #64748b;
            }
            QPushButton#startBtn {
                background-color: #22c55e;
            }
            QPushButton#startBtn:hover {
                background-color: #16a34a;
            }
            QPushButton#pauseBtn {
                background-color: #eab308;
            }
            QPushButton#pauseBtn:hover {
                background-color: #ca8a04;
            }
            QPushButton#stopBtn {
                background-color: #ef4444;
            }
            QPushButton#stopBtn:hover {
                background-color: #dc2626;
            }
            QTabWidget::pane {
                border: 1px solid #334155;
                background-color: #1e293b;
                border-radius: 6px;
            }
            QTabWidget::tab-bar {
                left: 5px;
            }
            QTabBar::tab {
                background-color: #0f172a;
                color: #94a3b8;
                border: 1px solid #334155;
                padding: 6px 12px;
                margin-right: 2px;
                font-size: 12px;
            }
            QTabBar::tab:selected {
                background-color: #1e293b;
                color: #3b82f6;
                border-bottom-color: #1e293b;
            }
            QTabBar::tab:hover {
                color: #e2e8f0;
            }
            QTabBar::tab:first {
                border-top-left-radius: 4px;
            }
            QTabBar::tab:last {
                border-top-right-radius: 4px;
            }
        """)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Auto Clicker Pro")
        title.setObjectName("title")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        self.hotkey_label = QPushButton("F6")
        self.hotkey_label.setObjectName("hotkeyBadge")
        self.hotkey_label.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hotkey_label.clicked.connect(self.change_hotkey)
        self.hotkey_label.setMaximumWidth(60)
        header_layout.addWidget(self.hotkey_label)
        
        self.current_hotkey = "f6"
        self.listening_for_hotkey = False
        self.last_toggle_time = 0
        
        main_layout.addLayout(header_layout)
        
        # Statistics Card
        stats_card = QFrame()
        stats_card.setObjectName("statsCard")
        stats_layout = QVBoxLayout(stats_card)
        stats_layout.setContentsMargins(10, 8, 10, 8)
        stats_layout.setSpacing(6)
        
        # Stats grid
        stats_grid = QHBoxLayout()
        stats_grid.setSpacing(10)
        
        # Clicks
        clicks_col = QVBoxLayout()
        clicks_label = QLabel("Clicks")
        clicks_label.setObjectName("statLabel")
        clicks_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.clicks_value = QLabel("0")
        self.clicks_value.setObjectName("statValue")
        self.clicks_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        clicks_col.addWidget(clicks_label)
        clicks_col.addWidget(self.clicks_value)
        stats_grid.addLayout(clicks_col)
        
        # Cycles/Bursts (only shown in burst mode)
        self.cycles_col = QWidget()
        cycles_layout = QVBoxLayout(self.cycles_col)
        cycles_layout.setContentsMargins(0, 0, 0, 0)
        self.cycles_label = QLabel("Bursts")
        self.cycles_label.setObjectName("statLabel")
        self.cycles_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cycles_value = QLabel("0")
        self.cycles_value.setObjectName("statValue")
        self.cycles_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cycles_layout.addWidget(self.cycles_label)
        cycles_layout.addWidget(self.cycles_value)
        stats_grid.addWidget(self.cycles_col)
        self.cycles_col.hide()
        
        # CPS
        cps_col = QVBoxLayout()
        cps_label = QLabel("CPS")
        cps_label.setObjectName("statLabel")
        cps_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.cps_value = QLabel("0")
        self.cps_value.setObjectName("statValue")
        self.cps_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        cps_col.addWidget(cps_label)
        cps_col.addWidget(self.cps_value)
        stats_grid.addLayout(cps_col)
        
        stats_layout.addLayout(stats_grid)
        
        # Timer and Status
        timer_status = QHBoxLayout()
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setObjectName("timerLabel")
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        timer_status.addWidget(self.timer_label)
        
        timer_status.addStretch()
        
        self.status_dot = QLabel("●")
        self.status_dot.setStyleSheet("color: #64748b; font-size: 14px;")
        timer_status.addWidget(self.status_dot)
        
        self.status_text = QLabel("Idle")
        self.status_text.setStyleSheet("color: #e2e8f0; font-size: 12px; font-weight: bold;")
        timer_status.addWidget(self.status_text)
        
        stats_layout.addLayout(timer_status)
        main_layout.addWidget(stats_card)
        
        # Tabs
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)
        
        # TAB 1: Timing
        timing_tab = QWidget()
        timing_layout = QVBoxLayout(timing_tab)
        timing_layout.setContentsMargins(10, 10, 10, 10)
        timing_layout.setSpacing(10)
        
        # Timing mode selector
        timing_mode_label = QLabel("Timing Mode")
        timing_mode_label.setObjectName("fieldLabel")
        timing_layout.addWidget(timing_mode_label)
        
        self.timing_mode_group = QButtonGroup()
        self.interval_mode_radio = QRadioButton("Interval Mode")
        self.interval_mode_radio.setChecked(True)
        self.interval_mode_radio.toggled.connect(self.update_timing_mode)
        self.timing_mode_group.addButton(self.interval_mode_radio)
        timing_layout.addWidget(self.interval_mode_radio)
        
        self.cps_mode_radio = QRadioButton("CPS Mode")
        self.cps_mode_radio.toggled.connect(self.update_timing_mode)
        self.timing_mode_group.addButton(self.cps_mode_radio)
        timing_layout.addWidget(self.cps_mode_radio)
        
        # Interval Mode Configuration
        self.interval_config = QWidget()
        interval_config_layout = QVBoxLayout(self.interval_config)
        interval_config_layout.setContentsMargins(0, 5, 0, 0)
        interval_config_layout.setSpacing(8)
        
        interval_label = QLabel("Click Interval")
        interval_label.setObjectName("fieldLabel")
        interval_config_layout.addWidget(interval_label)
        
        time_grid = QGridLayout()
        time_grid.setSpacing(6)
        
        self.time_inputs = {}
        for i, (label, default) in enumerate([("Hours", "0"), ("Mins", "0"), ("Secs", "0"), ("MS", "100")]):
            lbl = QLabel(label)
            lbl.setObjectName("fieldLabel")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            time_grid.addWidget(lbl, 0, i)
            
            entry = QLineEdit(default)
            entry.setValidator(QIntValidator(0, 999999))
            entry.setAlignment(Qt.AlignmentFlag.AlignCenter)
            time_grid.addWidget(entry, 1, i)
            
            self.time_inputs[label.lower()] = entry
        
        interval_config_layout.addLayout(time_grid)
        
        self.random_check = QCheckBox("Random Offset ±")
        interval_config_layout.addWidget(self.random_check)
        
        offset_layout = QHBoxLayout()
        self.offset_entry = QLineEdit("10")
        self.offset_entry.setValidator(QIntValidator(0, 999999))
        offset_layout.addWidget(self.offset_entry)
        offset_layout.addWidget(QLabel("ms"))
        interval_config_layout.addLayout(offset_layout)
        
        timing_layout.addWidget(self.interval_config)
        
        # CPS Mode Configuration
        self.cps_config = QWidget()
        cps_config_layout = QVBoxLayout(self.cps_config)
        cps_config_layout.setContentsMargins(0, 5, 0, 0)
        cps_config_layout.setSpacing(8)
        
        cps_target_layout = QHBoxLayout()
        cps_target_layout.addWidget(QLabel("Target CPS:"))
        self.cps_target_entry = QLineEdit("10")
        validator = QDoubleValidator(0.1, 1000.0, 2)
        validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.cps_target_entry.setValidator(validator)
        self.cps_target_entry.setMaximumWidth(80)
        cps_target_layout.addWidget(self.cps_target_entry)
        cps_target_layout.addStretch()
        cps_config_layout.addLayout(cps_target_layout)
        
        self.cps_random_check = QCheckBox("Random CPS Variance ±")
        cps_config_layout.addWidget(self.cps_random_check)
        
        cps_variance_layout = QHBoxLayout()
        self.cps_variance_entry = QLineEdit("1.0")
        variance_validator = QDoubleValidator(0.0, 100.0, 2)
        variance_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        self.cps_variance_entry.setValidator(variance_validator)
        self.cps_variance_entry.setMaximumWidth(80)
        cps_variance_layout.addWidget(self.cps_variance_entry)
        cps_variance_layout.addWidget(QLabel("CPS"))
        cps_variance_layout.addStretch()
        cps_config_layout.addLayout(cps_variance_layout)
        
        timing_layout.addWidget(self.cps_config)
        self.cps_config.hide()
        
        timing_layout.addStretch()
        self.tabs.addTab(timing_tab, "Timing")
        
        # TAB 2: Pattern
        pattern_tab = QWidget()
        pattern_layout = QVBoxLayout(pattern_tab)
        pattern_layout.setContentsMargins(10, 10, 10, 10)
        pattern_layout.setSpacing(10)
        
        # Pattern type
        pattern_label = QLabel("Pattern Type")
        pattern_label.setObjectName("fieldLabel")
        pattern_layout.addWidget(pattern_label)
        
        self.pattern_group = QButtonGroup()
        self.continuous_radio = QRadioButton("Continuous")
        self.continuous_radio.setChecked(True)
        self.continuous_radio.toggled.connect(self.update_pattern_ui)
        self.pattern_group.addButton(self.continuous_radio)
        pattern_layout.addWidget(self.continuous_radio)
        
        self.burst_radio = QRadioButton("Burst Mode")
        self.burst_radio.toggled.connect(self.update_pattern_ui)
        self.pattern_group.addButton(self.burst_radio)
        pattern_layout.addWidget(self.burst_radio)
        
        # Burst configuration
        self.burst_config = QWidget()
        burst_config_layout = QVBoxLayout(self.burst_config)
        burst_config_layout.setContentsMargins(20, 5, 0, 0)
        burst_config_layout.setSpacing(8)
        
        burst_clicks_layout = QHBoxLayout()
        burst_clicks_layout.addWidget(QLabel("Clicks per burst:"))
        self.burst_clicks_entry = QLineEdit("5")
        self.burst_clicks_entry.setValidator(QIntValidator(1, 999))
        self.burst_clicks_entry.setMaximumWidth(60)
        burst_clicks_layout.addWidget(self.burst_clicks_entry)
        burst_clicks_layout.addStretch()
        burst_config_layout.addLayout(burst_clicks_layout)
        
        burst_delay_layout = QHBoxLayout()
        burst_delay_layout.addWidget(QLabel("Delay between bursts:"))
        self.burst_delay_entry = QLineEdit("1000")
        self.burst_delay_entry.setValidator(QIntValidator(1, 999999))
        self.burst_delay_entry.setMaximumWidth(60)
        burst_delay_layout.addWidget(self.burst_delay_entry)
        burst_delay_layout.addWidget(QLabel("ms"))
        burst_delay_layout.addStretch()
        burst_config_layout.addLayout(burst_delay_layout)
        
        pattern_layout.addWidget(self.burst_config)
        self.burst_config.hide()
        
        # Repeat mode
        repeat_label = QLabel("Repeat Mode")
        repeat_label.setObjectName("fieldLabel")
        pattern_layout.addWidget(repeat_label)
        
        self.repeat_group = QButtonGroup()
        self.infinite_radio = QRadioButton("Infinite")
        self.infinite_radio.setChecked(True)
        self.repeat_group.addButton(self.infinite_radio)
        pattern_layout.addWidget(self.infinite_radio)
        
        repeat_row = QHBoxLayout()
        self.repeat_radio = QRadioButton("Repeat")
        self.repeat_group.addButton(self.repeat_radio)
        repeat_row.addWidget(self.repeat_radio)
        
        self.repeat_entry = QLineEdit("100")
        self.repeat_entry.setValidator(QIntValidator(1, 999999))
        self.repeat_entry.setMaximumWidth(60)
        repeat_row.addWidget(self.repeat_entry)
        repeat_row.addWidget(QLabel("times"))
        repeat_row.addStretch()
        pattern_layout.addLayout(repeat_row)
        
        pattern_layout.addStretch()
        self.tabs.addTab(pattern_tab, "Pattern")
        
        # TAB 3: Options
        options_tab = QWidget()
        options_layout = QVBoxLayout(options_tab)
        options_layout.setContentsMargins(10, 10, 10, 10)
        options_layout.setSpacing(10)
        
        # Mouse button
        btn_label = QLabel("Mouse Button")
        btn_label.setObjectName("fieldLabel")
        options_layout.addWidget(btn_label)
        self.button_combo = QComboBox()
        self.button_combo.addItems(["Left", "Right", "Middle"])
        options_layout.addWidget(self.button_combo)
        
        # Click type
        type_label = QLabel("Click Type")
        type_label.setObjectName("fieldLabel")
        options_layout.addWidget(type_label)
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Single", "Double", "Triple"])
        options_layout.addWidget(self.type_combo)
        
        # Cursor position
        cursor_label = QLabel("Cursor Position")
        cursor_label.setObjectName("fieldLabel")
        options_layout.addWidget(cursor_label)
        
        self.cursor_group = QButtonGroup()
        self.current_radio = QRadioButton("Current Position")
        self.current_radio.setChecked(True)
        self.cursor_group.addButton(self.current_radio)
        options_layout.addWidget(self.current_radio)
        
        self.pick_radio = QRadioButton("Pick Location")
        self.cursor_group.addButton(self.pick_radio)
        options_layout.addWidget(self.pick_radio)
        
        self.pick_btn = QPushButton("Pick Location (Space)")
        self.pick_btn.clicked.connect(self.pick_location)
        options_layout.addWidget(self.pick_btn)
        
        options_layout.addStretch()
        self.tabs.addTab(options_tab, "Options")
        
        # Control buttons
        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(6)
        
        self.start_btn = QPushButton("START")
        self.start_btn.setObjectName("startBtn")
        self.start_btn.clicked.connect(self.start)
        controls_layout.addWidget(self.start_btn)
        
        self.pause_btn = QPushButton("PAUSE")
        self.pause_btn.setObjectName("pauseBtn")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pause)
        controls_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("STOP")
        self.stop_btn.setObjectName("stopBtn")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop)
        controls_layout.addWidget(self.stop_btn)
        
        main_layout.addLayout(controls_layout)
        
        # Store picked location
        self.pick_x = 0
        self.pick_y = 0
        
    def update_timing_mode(self):
        is_cps_mode = self.cps_mode_radio.isChecked()
        self.interval_config.setVisible(not is_cps_mode)
        self.cps_config.setVisible(is_cps_mode)
    
    def update_pattern_ui(self):
        is_burst = self.burst_radio.isChecked()
        self.burst_config.setVisible(is_burst)
        self.cycles_col.setVisible(is_burst)
    
    def get_interval(self):
        # Check which mode is active
        is_cps_mode = self.cps_mode_radio.isChecked()
        
        if is_cps_mode:
            # CPS mode - calculate interval from target CPS
            try:
                target_cps = float(self.cps_target_entry.text() or 10)
                if target_cps <= 0:
                    target_cps = 10
                
                # Adjust for click type - each multi-click counts as multiple clicks
                clicks_per_action = {"Single": 1, "Double": 2, "Triple": 3}[self.type_combo.currentText()]
                
                # Calculate interval based on clicks per action
                # If we want 10 CPS and double-clicking, we need 5 actions per second
                actions_per_second = target_cps / clicks_per_action
                base_interval = 1.0 / actions_per_second
                
                if self.cps_random_check.isChecked():
                    variance = float(self.cps_variance_entry.text() or 1.0)
                    # Calculate variance in CPS, then convert to interval
                    min_cps = max(0.1, target_cps - variance)
                    max_cps = target_cps + variance
                    random_cps = random.uniform(min_cps, max_cps)
                    random_actions_per_second = random_cps / clicks_per_action
                    base_interval = 1.0 / random_actions_per_second
                
                return max(0.001, base_interval)
            except Exception as e:
                return 0.1
        else:
            # Interval mode - use time inputs
            try:
                base = (int(self.time_inputs['hours'].text() or 0) * 3600 +
                        int(self.time_inputs['mins'].text() or 0) * 60 +
                        int(self.time_inputs['secs'].text() or 0) +
                        int(self.time_inputs['ms'].text() or 0) / 1000)
                
                if self.random_check.isChecked():
                    offset = int(self.offset_entry.text() or 0) / 1000
                    base += random.uniform(-offset, offset)
                
                return max(0.001, base)
            except Exception as e:
                return 0.1
    
    def click(self):
        if self.pick_radio.isChecked():
            pyautogui.moveTo(self.pick_x, self.pick_y)
        
        clicks = {"Single": 1, "Double": 2, "Triple": 3}[self.type_combo.currentText()]
        button = self.button_combo.currentText().lower()
        pyautogui.click(button=button, clicks=clicks)
        
        now = time.time()
        for _ in range(clicks):
            self.click_times.append(now)
        
        self.click_count += clicks
    
    def loop(self):
        self.start_time = time.time()
        is_burst = self.burst_radio.isChecked()
        is_cps_mode = self.cps_mode_radio.isChecked()
        
        while self.running:
            if self.paused:
                time.sleep(0.05)
                continue
            
            # Check repeat limit
            if self.repeat_radio.isChecked():
                try:
                    max_repeats = int(self.repeat_entry.text() or 100)
                    if self.cycles_count >= max_repeats:
                        break
                except:
                    pass
            
            if is_burst:
                # Burst mode: rapid clicks with delay between bursts
                try:
                    burst_clicks = int(self.burst_clicks_entry.text() or 5)
                    burst_delay = int(self.burst_delay_entry.text() or 1000) / 1000
                except:
                    burst_clicks = 5
                    burst_delay = 1.0
                
                for _ in range(burst_clicks):
                    if not self.running or self.paused:
                        break
                    self.click()
                    time.sleep(0.01)  # Small delay between clicks in burst
                
                self.cycles_count += 1
                time.sleep(burst_delay)
            else:
                # Continuous mode - use calculated interval
                self.click()
                self.cycles_count += 1
                
                # Get interval based on current mode
                interval = self.get_interval()
                time.sleep(interval)
        
        if self.running:
            self.stop()
    
    def update_ui_loop(self):
        while self.running:
            if not self.paused:
                elapsed = int(time.time() - self.start_time)
                h, r = divmod(elapsed, 3600)
                m, s = divmod(r, 60)
                timer_text = f"{h:02}:{m:02}:{s:02}"
                
                now = time.time()
                while self.click_times and now - self.click_times[0] > 1:
                    self.click_times.popleft()
                cps = len(self.click_times)
                
                self.signals.update_stats.emit(timer_text, self.click_count, 
                                               self.cycles_count, cps)
            
            time.sleep(0.1)
    
    def update_ui_stats(self, timer_text, clicks, cycles, cps):
        if self.running:
            self.timer_label.setText(timer_text)
            self.clicks_value.setText(str(clicks))
            self.cycles_value.setText(str(cycles))
            self.cps_value.setText(str(cps))
    
    def update_status(self, text, color):
        self.status_dot.setStyleSheet(f"color: {color}; font-size: 14px;")
        self.status_text.setText(text)
    
    def toggle_controls(self, enabled):
        for widget in [self.random_check, self.button_combo, self.type_combo,
                      self.continuous_radio, self.burst_radio, self.infinite_radio,
                      self.repeat_radio, self.current_radio, self.pick_radio, 
                      self.pick_btn, self.offset_entry, self.repeat_entry,
                      self.burst_clicks_entry, self.burst_delay_entry,
                      self.interval_mode_radio, self.cps_mode_radio,
                      self.cps_target_entry, self.cps_random_check, self.cps_variance_entry]:
            widget.setEnabled(enabled)
        
        for entry in self.time_inputs.values():
            entry.setEnabled(enabled)
    
    def start(self):
        if self.running:
            return
        
        self.running = True
        self.paused = False
        self.click_count = 0
        self.cycles_count = 0
        self.click_times.clear()
        
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        self.toggle_controls(False)
        
        self.signals.status_changed.emit("Running", "#22c55e")
        
        threading.Thread(target=self.loop, daemon=True).start()
        threading.Thread(target=self.update_ui_loop, daemon=True).start()
    
    def pause(self):
        self.paused = not self.paused
        self.pause_btn.setText("RESUME" if self.paused else "PAUSE")
        color = "#eab308" if self.paused else "#22c55e"
        text = "Paused" if self.paused else "Running"
        self.signals.status_changed.emit(text, color)
    
    def stop(self):
        self.running = False
        self.paused = False
        self.click_times.clear()
        
        self.timer_label.setText("00:00:00")
        self.clicks_value.setText(str(self.click_count))
        self.cycles_value.setText(str(self.cycles_count))
        self.cps_value.setText("0")
        
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.pause_btn.setText("PAUSE")
        self.stop_btn.setEnabled(False)
        self.toggle_controls(True)
        
        self.signals.status_changed.emit("Idle", "#64748b")
    
    def change_hotkey(self):
        if self.running or self.listening_for_hotkey:
            return
        
        self.listening_for_hotkey = True
        self.hotkey_label.setText("Press key...")
        self.hotkey_label.setStyleSheet("""
            background-color: #3b82f6;
            color: #ffffff;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 10px;
            border: 2px solid #2563eb;
            min-height: 16px;
        """)
        
        def wait_for_key():
            event = keyboard.read_event(suppress=True)
            if event.event_type == "down":
                new_key = event.name.lower()
                
                # Don't allow certain keys
                if new_key in ['esc', 'escape', 'tab', 'enter', 'return']:
                    self.listening_for_hotkey = False
                    self.hotkey_label.setText(self.current_hotkey.upper())
                    self.hotkey_label.setStyleSheet("")
                    return
                
                # Update hotkey
                self.current_hotkey = new_key
                self.setup_hotkey()  # Re-setup with new key
                
                # Update label
                display_name = new_key.upper()
                self.hotkey_label.setText(display_name)
                self.hotkey_label.setStyleSheet("")
                self.listening_for_hotkey = False
        
        threading.Thread(target=wait_for_key, daemon=True).start()
    
    def pick_location(self):
        def wait():
            keyboard.wait("space")
            x, y = pyautogui.position()
            self.pick_x = x
            self.pick_y = y
            self.pick_radio.setChecked(True)
        threading.Thread(target=wait, daemon=True).start()
    
    def setup_hotkey(self):
        keyboard.unhook_all()
        
        def on_key_event(event):
            if event.event_type == "down" and event.name.lower() == self.current_hotkey:
                # Debounce: prevent multiple triggers within 0.3 seconds
                current_time = time.time()
                if current_time - self.last_toggle_time >= 0.3:
                    self.last_toggle_time = current_time
                    self.toggle()
        
        keyboard.hook(on_key_event)
    
    def toggle(self):
        if not self.running:
            self.start()
        elif self.paused:
            self.pause()
        else:
            self.stop()
    
    def save_config(self):
        config = {
            'hotkey': self.current_hotkey,
            'timing_mode': 'cps' if self.cps_mode_radio.isChecked() else 'interval',
            'hours': self.time_inputs['hours'].text(),
            'mins': self.time_inputs['mins'].text(),
            'secs': self.time_inputs['secs'].text(),
            'ms': self.time_inputs['ms'].text(),
            'offset_val': self.offset_entry.text(),
            'random_offset': self.random_check.isChecked(),
            'cps_target': self.cps_target_entry.text(),
            'cps_variance': self.cps_variance_entry.text(),
            'cps_random': self.cps_random_check.isChecked(),
            'button': self.button_combo.currentText(),
            'click_type': self.type_combo.currentText(),
            'pattern': 'burst' if self.burst_radio.isChecked() else 'continuous',
            'burst_clicks': self.burst_clicks_entry.text(),
            'burst_delay': self.burst_delay_entry.text(),
            'repeat_mode': 'repeat' if self.repeat_radio.isChecked() else 'infinite',
            'repeat_times': self.repeat_entry.text(),
            'cursor_mode': 'pick' if self.pick_radio.isChecked() else 'current',
            'pick_x': self.pick_x,
            'pick_y': self.pick_y
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def load_config(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file) as f:
                    config = json.load(f)
                
                # Load hotkey
                self.current_hotkey = config.get('hotkey', 'f6')
                self.hotkey_label.setText(self.current_hotkey.upper())
                
                if config.get('timing_mode') == 'cps':
                    self.cps_mode_radio.setChecked(True)
                
                self.time_inputs['hours'].setText(config.get('hours', '0'))
                self.time_inputs['mins'].setText(config.get('mins', '0'))
                self.time_inputs['secs'].setText(config.get('secs', '0'))
                self.time_inputs['ms'].setText(config.get('ms', '100'))
                self.offset_entry.setText(config.get('offset_val', '10'))
                self.random_check.setChecked(config.get('random_offset', False))
                
                self.cps_target_entry.setText(config.get('cps_target', '10'))
                self.cps_variance_entry.setText(config.get('cps_variance', '1.0'))
                self.cps_random_check.setChecked(config.get('cps_random', False))
                
                self.button_combo.setCurrentText(config.get('button', 'Left'))
                self.type_combo.setCurrentText(config.get('click_type', 'Single'))
                
                if config.get('pattern') == 'burst':
                    self.burst_radio.setChecked(True)
                
                self.burst_clicks_entry.setText(config.get('burst_clicks', '5'))
                self.burst_delay_entry.setText(config.get('burst_delay', '1000'))
                
                if config.get('repeat_mode') == 'repeat':
                    self.repeat_radio.setChecked(True)
                
                self.repeat_entry.setText(config.get('repeat_times', '100'))
                
                if config.get('cursor_mode') == 'pick':
                    self.pick_radio.setChecked(True)
                    self.pick_x = config.get('pick_x', 0)
                    self.pick_y = config.get('pick_y', 0)
            except:
                pass
    
    def closeEvent(self, event):
        self.running = False
        self.save_config()
        keyboard.unhook_all()
        event.accept()

def main():
    app = QApplication(sys.argv)
    window = ModernAutoClicker()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
