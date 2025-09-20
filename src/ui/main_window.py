import sys
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
                               QSplitter, QLabel, QStatusBar, QProgressBar)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont, QPalette, QColor

from ..utils.config import APP_NAME, COLORS
from .control_panel import ControlPanel
from .chart_widget import ChartWidget
from ..models.black_scholes import BlackScholesSimulator


class SimulationWorker(QThread):
    """Worker thread for running simulations without blocking the UI."""

    finished = Signal(object, object)  # time_grid, price_paths
    progress = Signal(int)
    error = Signal(str)

    def __init__(self, simulator, n_paths):
        super().__init__()
        self.simulator = simulator
        self.n_paths = n_paths

    def run(self):
        try:
            self.progress.emit(10)
            time_grid, price_paths = self.simulator.simulate_multiple_paths(self.n_paths)
            self.progress.emit(80)

            # Calculate statistics
            stats = self.simulator.get_statistics(price_paths)
            self.progress.emit(100)

            self.finished.emit((time_grid, price_paths), stats)
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.simulator = None
        self.simulation_worker = None
        self.setup_ui()
        self.apply_dark_theme()
        self.setup_simulator()

    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle(APP_NAME)
        self.setGeometry(100, 100, 1400, 900)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # Create main splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel (controls)
        self.control_panel = ControlPanel()
        self.control_panel.setMaximumWidth(300)
        self.control_panel.setMinimumWidth(250)
        splitter.addWidget(self.control_panel)

        # Right side layout for chart and stats
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)

        # Chart widget
        self.chart_widget = ChartWidget()
        right_layout.addWidget(self.chart_widget, stretch=3)

        # Statistics panel (placeholder for now)
        self.stats_panel = QLabel("Statistics will appear here after running simulation")
        self.stats_panel.setAlignment(Qt.AlignTop)
        self.stats_panel.setStyleSheet(f"""
            QLabel {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                padding: 15px;
                border-radius: 8px;
                font-size: 12px;
            }}
        """)
        self.stats_panel.setMaximumHeight(200)
        right_layout.addWidget(self.stats_panel, stretch=1)

        splitter.addWidget(right_widget)

        # Set splitter proportions
        splitter.setSizes([300, 1100])

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Progress bar for simulations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addPermanentWidget(self.progress_bar)

        # Connect signals
        self.connect_signals()

    def connect_signals(self):
        """Connect control panel signals to handlers."""
        self.control_panel.simulate_clicked.connect(self.run_simulation)
        self.control_panel.parameters_changed.connect(self.update_simulator_parameters)
        self.control_panel.animation_requested.connect(self.chart_widget.start_animation)
        self.control_panel.reset_zoom_requested.connect(self.chart_widget.reset_zoom)
        self.control_panel.toggle_percentiles_requested.connect(self.chart_widget.toggle_percentiles)
        self.control_panel.export_requested.connect(self.chart_widget.export_chart)

    def setup_simulator(self):
        """Initialize the Black-Scholes simulator with default parameters."""
        self.simulator = BlackScholesSimulator(
            S0=100.0,
            mu=0.08,
            sigma=0.20,
            T=1.0
        )

    def update_simulator_parameters(self, params):
        """Update simulator parameters when controls change."""
        if self.simulator:
            self.simulator.update_parameters(
                S0=params.get('S0'),
                mu=params.get('mu'),
                sigma=params.get('sigma'),
                T=params.get('T')
            )

    def run_simulation(self, params):
        """Run the Monte Carlo simulation."""
        if self.simulation_worker and self.simulation_worker.isRunning():
            return

        # Update simulator parameters
        self.update_simulator_parameters(params)

        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.status_bar.showMessage("Running simulation...")

        # Disable controls
        self.control_panel.setEnabled(False)

        # Start simulation in worker thread
        self.simulation_worker = SimulationWorker(self.simulator, params['n_paths'])
        self.simulation_worker.finished.connect(self.on_simulation_finished)
        self.simulation_worker.progress.connect(self.progress_bar.setValue)
        self.simulation_worker.error.connect(self.on_simulation_error)
        self.simulation_worker.start()

    def on_simulation_finished(self, simulation_data, stats):
        """Handle completed simulation."""
        time_grid, price_paths = simulation_data

        # Update chart
        self.chart_widget.update_chart(time_grid, price_paths, stats)

        # Update statistics panel
        self.update_stats_panel(stats)

        # Reset UI
        self.progress_bar.setVisible(False)
        self.control_panel.setEnabled(True)
        self.status_bar.showMessage(f"Simulation completed: {len(price_paths)} paths", 3000)

    def on_simulation_error(self, error_msg):
        """Handle simulation errors."""
        self.progress_bar.setVisible(False)
        self.control_panel.setEnabled(True)
        self.status_bar.showMessage(f"Simulation error: {error_msg}", 5000)

    def update_stats_panel(self, stats):
        """Update the statistics panel with simulation results."""
        stats_text = f"""
        <h3>Simulation Statistics</h3>
        <p><b>Final Price:</b></p>
        <p>• Mean: {stats['final_price_mean']:.2f}</p>
        <p>• Std Dev: {stats['final_price_std']:.2f}</p>
        <p>• Min: {stats['final_price_min']:.2f}</p>
        <p>• Max: {stats['final_price_max']:.2f}</p>

        <p><b>Returns:</b></p>
        <p>• Profit Probability: {stats['probability_profit']:.1f}%</p>
        <p>• VaR (95%): {stats['var_95']:.1f}%</p>
        <p>• Expected Shortfall: {stats['expected_shortfall']:.1f}%</p>
        """
        self.stats_panel.setText(stats_text)

    def apply_dark_theme(self):
        """Apply dark theme to the application."""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}

            QWidget {{
                background-color: {COLORS['background']};
                color: {COLORS['text']};
            }}

            QSplitter::handle {{
                background-color: {COLORS['accent']};
                width: 2px;
            }}

            QStatusBar {{
                background-color: {COLORS['surface']};
                color: {COLORS['text']};
                border-top: 1px solid {COLORS['accent']};
            }}
        """)

    def closeEvent(self, event):
        """Handle application close event."""
        if self.simulation_worker and self.simulation_worker.isRunning():
            self.simulation_worker.terminate()
            self.simulation_worker.wait()
        event.accept()