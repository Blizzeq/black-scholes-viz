from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                               QSlider, QDoubleSpinBox, QSpinBox, QPushButton,
                               QGroupBox, QComboBox, QFrame)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

from ..utils.config import COLORS, DEFAULT_S0, DEFAULT_MU, DEFAULT_SIGMA, DEFAULT_T, DEFAULT_N_PATHS
from ..models.black_scholes import create_scenario_presets


class ControlPanel(QWidget):
    """Control panel widget with simulation parameters."""

    simulate_clicked = Signal(dict)
    parameters_changed = Signal(dict)
    animation_requested = Signal()
    reset_zoom_requested = Signal()
    toggle_percentiles_requested = Signal()
    export_requested = Signal()

    def __init__(self):
        super().__init__()
        self.scenario_presets = create_scenario_presets()
        self.setup_ui()
        self.connect_signals()

    def setup_ui(self):
        """Setup the control panel UI."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 15, 15, 15)

        # Title
        title = QLabel("Simulation Parameters")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Scenario presets
        layout.addWidget(self.create_scenario_group())

        # Simulation parameters
        layout.addWidget(self.create_simulation_group())

        # Market parameters
        layout.addWidget(self.create_market_group())

        # Action buttons
        layout.addWidget(self.create_buttons_group())

        # Stretch at the bottom
        layout.addStretch()

        self.apply_styling()

    def create_scenario_group(self):
        """Create scenario selection group."""
        group = QGroupBox("Scenarios")
        layout = QVBoxLayout(group)

        self.scenario_combo = QComboBox()
        self.scenario_combo.addItem("Choose scenario...", None)
        for name, params in self.scenario_presets.items():
            display_name = name.replace("_", " ").title()
            self.scenario_combo.addItem(display_name, params)

        layout.addWidget(self.scenario_combo)
        return group

    def create_simulation_group(self):
        """Create simulation parameters group."""
        group = QGroupBox("Simulation Parameters")
        layout = QVBoxLayout(group)

        # Number of paths
        layout.addWidget(QLabel("Number of paths:"))
        self.n_paths_slider = QSlider(Qt.Horizontal)
        self.n_paths_slider.setRange(10, 1000)
        self.n_paths_slider.setValue(DEFAULT_N_PATHS)
        self.n_paths_label = QLabel(str(DEFAULT_N_PATHS))

        paths_layout = QHBoxLayout()
        paths_layout.addWidget(self.n_paths_slider)
        paths_layout.addWidget(self.n_paths_label)
        layout.addLayout(paths_layout)

        # Time horizon
        layout.addWidget(QLabel("Time horizon (years):"))
        self.time_slider = QSlider(Qt.Horizontal)
        self.time_slider.setRange(1, 50)  # 0.1 to 5.0 years (in 0.1 increments)
        self.time_slider.setValue(int(DEFAULT_T * 10))
        self.time_label = QLabel(f"{DEFAULT_T:.1f}")

        time_layout = QHBoxLayout()
        time_layout.addWidget(self.time_slider)
        time_layout.addWidget(self.time_label)
        layout.addLayout(time_layout)

        return group

    def create_market_group(self):
        """Create market parameters group."""
        group = QGroupBox("Market Parameters")
        layout = QVBoxLayout(group)

        # Initial price
        layout.addWidget(QLabel("Initial price:"))
        self.s0_spinbox = QDoubleSpinBox()
        self.s0_spinbox.setRange(1.0, 1000.0)
        self.s0_spinbox.setValue(DEFAULT_S0)
        self.s0_spinbox.setDecimals(2)
        layout.addWidget(self.s0_spinbox)

        # Expected return (mu)
        layout.addWidget(QLabel("Expected return (μ):"))
        self.mu_slider = QSlider(Qt.Horizontal)
        self.mu_slider.setRange(-50, 50)  # -50% to +50%
        self.mu_slider.setValue(int(DEFAULT_MU * 100))
        self.mu_label = QLabel(f"{DEFAULT_MU:.1%}")

        mu_layout = QHBoxLayout()
        mu_layout.addWidget(self.mu_slider)
        mu_layout.addWidget(self.mu_label)
        layout.addLayout(mu_layout)

        # Volatility (sigma)
        layout.addWidget(QLabel("Volatility (σ):"))
        self.sigma_slider = QSlider(Qt.Horizontal)
        self.sigma_slider.setRange(5, 100)  # 5% to 100%
        self.sigma_slider.setValue(int(DEFAULT_SIGMA * 100))
        self.sigma_label = QLabel(f"{DEFAULT_SIGMA:.1%}")

        sigma_layout = QHBoxLayout()
        sigma_layout.addWidget(self.sigma_slider)
        sigma_layout.addWidget(self.sigma_label)
        layout.addLayout(sigma_layout)

        return group

    def create_buttons_group(self):
        """Create action buttons group."""
        group = QGroupBox("Actions")
        layout = QVBoxLayout(group)

        self.simulate_button = QPushButton("🚀 Run Simulation")
        self.simulate_button.setMinimumHeight(40)

        self.animate_button = QPushButton("🎬 Animation")
        self.animate_button.setEnabled(False)  # Enable after first simulation

        self.reset_zoom_button = QPushButton("🔍 Reset Zoom")
        self.reset_zoom_button.setEnabled(False)  # Enable after first simulation

        self.toggle_percentiles_button = QPushButton("📊 Toggle Percentiles")
        self.toggle_percentiles_button.setEnabled(False)  # Enable after first simulation

        self.export_button = QPushButton("💾 Export")
        self.export_button.setEnabled(False)  # Enable after first simulation

        layout.addWidget(self.simulate_button)
        layout.addWidget(self.animate_button)
        layout.addWidget(self.reset_zoom_button)
        layout.addWidget(self.toggle_percentiles_button)
        layout.addWidget(self.export_button)

        return group

    def connect_signals(self):
        """Connect widget signals."""
        # Sliders
        self.n_paths_slider.valueChanged.connect(self.update_n_paths_label)
        self.time_slider.valueChanged.connect(self.update_time_label)
        self.mu_slider.valueChanged.connect(self.update_mu_label)
        self.sigma_slider.valueChanged.connect(self.update_sigma_label)

        # Parameter changes
        self.time_slider.valueChanged.connect(self.emit_parameters_changed)
        self.s0_spinbox.valueChanged.connect(self.emit_parameters_changed)
        self.mu_slider.valueChanged.connect(self.emit_parameters_changed)
        self.sigma_slider.valueChanged.connect(self.emit_parameters_changed)

        # Buttons
        self.simulate_button.clicked.connect(self.emit_simulate_clicked)
        self.animate_button.clicked.connect(self.animation_requested.emit)
        self.reset_zoom_button.clicked.connect(self.reset_zoom_requested.emit)
        self.toggle_percentiles_button.clicked.connect(self.toggle_percentiles_requested.emit)
        self.export_button.clicked.connect(self.export_requested.emit)

        # Scenario selection
        self.scenario_combo.currentIndexChanged.connect(self.apply_scenario)

    def update_n_paths_label(self, value):
        """Update number of paths label."""
        self.n_paths_label.setText(str(value))

    def update_time_label(self, value):
        """Update time horizon label."""
        time_value = value / 10.0
        self.time_label.setText(f"{time_value:.1f}")

    def update_mu_label(self, value):
        """Update mu label."""
        mu_value = value / 100.0
        self.mu_label.setText(f"{mu_value:.1%}")

    def update_sigma_label(self, value):
        """Update sigma label."""
        sigma_value = value / 100.0
        self.sigma_label.setText(f"{sigma_value:.1%}")

    def apply_scenario(self, index):
        """Apply selected scenario parameters."""
        if index == 0:  # "Choose scenario..." option
            return

        scenario_data = self.scenario_combo.itemData(index)
        if scenario_data:
            # Update UI controls
            self.mu_slider.setValue(int(scenario_data['mu'] * 100))
            self.sigma_slider.setValue(int(scenario_data['sigma'] * 100))

            # Emit parameter change
            self.emit_parameters_changed()

    def get_current_parameters(self):
        """Get current parameter values."""
        return {
            'n_paths': self.n_paths_slider.value(),
            'T': self.time_slider.value() / 10.0,
            'S0': self.s0_spinbox.value(),
            'mu': self.mu_slider.value() / 100.0,
            'sigma': self.sigma_slider.value() / 100.0
        }

    def emit_parameters_changed(self):
        """Emit parameters changed signal."""
        self.parameters_changed.emit(self.get_current_parameters())

    def emit_simulate_clicked(self):
        """Emit simulate clicked signal."""
        params = self.get_current_parameters()
        self.simulate_clicked.emit(params)

        # Enable post-simulation buttons
        self.animate_button.setEnabled(True)
        self.reset_zoom_button.setEnabled(True)
        self.toggle_percentiles_button.setEnabled(True)
        self.export_button.setEnabled(True)

    def apply_styling(self):
        """Apply custom styling to the control panel."""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-weight: bold;
                border: 2px solid {COLORS['accent']};
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
                background-color: {COLORS['surface']};
            }}

            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: {COLORS['accent']};
            }}

            QLabel {{
                color: {COLORS['text']};
                font-size: 11px;
            }}

            QSlider::groove:horizontal {{
                border: 1px solid {COLORS['text_secondary']};
                height: 6px;
                background: {COLORS['background']};
                border-radius: 3px;
            }}

            QSlider::handle:horizontal {{
                background: {COLORS['accent']};
                border: 1px solid {COLORS['accent']};
                width: 18px;
                height: 18px;
                border-radius: 9px;
                margin: -6px 0;
            }}

            QSlider::sub-page:horizontal {{
                background: {COLORS['accent']};
                border-radius: 3px;
            }}

            QPushButton {{
                background-color: {COLORS['accent']};
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 12px;
            }}

            QPushButton:hover {{
                background-color: #ff6b7a;
            }}

            QPushButton:pressed {{
                background-color: #d73654;
            }}

            QPushButton:disabled {{
                background-color: {COLORS['text_secondary']};
                color: #666;
            }}

            QDoubleSpinBox, QSpinBox {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['text_secondary']};
                border-radius: 4px;
                padding: 4px;
                color: {COLORS['text']};
            }}

            QComboBox {{
                background-color: {COLORS['background']};
                border: 1px solid {COLORS['text_secondary']};
                border-radius: 4px;
                padding: 4px;
                color: {COLORS['text']};
            }}

            QComboBox::drop-down {{
                border: none;
            }}

            QComboBox::down-arrow {{
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid {COLORS['text']};
            }}
        """)