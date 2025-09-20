from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                               QLabel, QFrame, QProgressBar)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette

from ..utils.config import COLORS


class StatCard(QFrame):

    def __init__(self, title, value="", unit="", color=None):
        super().__init__()
        self.setup_ui(title, value, unit, color)

    def setup_ui(self, title, value, unit, color):
        """Setup the card UI."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['accent']};
                border-radius: 8px;
                padding: 8px;
                margin: 2px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(8, 6, 8, 6)

        # Title label
        self.title_label = QLabel(title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
        """)
        layout.addWidget(self.title_label)

        # Value label
        self.value_label = QLabel(value)
        self.value_label.setAlignment(Qt.AlignCenter)

        # Set color based on value type
        if color:
            text_color = color
        else:
            text_color = COLORS['text']

        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {text_color};
                font-size: 14px;
                font-weight: bold;
                margin: 1px 0px;
            }}
        """)
        layout.addWidget(self.value_label)

        # Unit label (if provided)
        if unit:
            self.unit_label = QLabel(unit)
            self.unit_label.setAlignment(Qt.AlignCenter)
            self.unit_label.setStyleSheet(f"""
                QLabel {{
                    color: {COLORS['text_secondary']};
                    font-size: 9px;
                }}
            """)
            layout.addWidget(self.unit_label)

    def update_value(self, value, color=None):
        """Update the card value and color."""
        self.value_label.setText(str(value))
        if color:
            self.value_label.setStyleSheet(f"""
                QLabel {{
                    color: {color};
                    font-size: 16px;
                    font-weight: bold;
                    margin: 2px 0px;
                }}
            """)


class ProgressCard(QFrame):

    def __init__(self, title, value=0, max_value=100):
        super().__init__()
        self.setup_ui(title, value, max_value)

    def setup_ui(self, title, value, max_value):
        """Setup the progress card UI."""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['surface']};
                border: 1px solid {COLORS['accent']};
                border-radius: 8px;
                padding: 8px;
                margin: 2px;
            }}
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(12, 8, 12, 8)

        # Title and value in one row
        header_layout = QHBoxLayout()

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text_secondary']};
                font-size: 10px;
                font-weight: bold;
                text-transform: uppercase;
            }}
        """)
        header_layout.addWidget(self.title_label)

        self.value_label = QLabel(f"{value:.1f}%")
        self.value_label.setAlignment(Qt.AlignRight)
        self.value_label.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 12px;
                font-weight: bold;
            }}
        """)
        header_layout.addWidget(self.value_label)

        layout.addLayout(header_layout)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(int(max_value))
        self.progress_bar.setValue(int(value))
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS['accent']};
                border-radius: 4px;
                text-align: center;
                background-color: {COLORS['background']};
                height: 8px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['accent']}, stop:1 {COLORS['success']});
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.progress_bar)

    def update_value(self, value):
        """Update progress value."""
        self.value_label.setText(f"{value:.1f}%")
        self.progress_bar.setValue(int(value))


class StatsPanel(QWidget):

    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """Setup the statistics panel UI."""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(8, 8, 8, 8)

        # Header
        header = QLabel("📊 SIMULATION STATISTICS")
        header.setAlignment(Qt.AlignCenter)
        header.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['accent']};
                font-size: 13px;
                font-weight: bold;
                padding: 6px;
                border-bottom: 1px solid {COLORS['accent']};
                margin-bottom: 8px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {COLORS['surface']}, stop:1 {COLORS['background']});
                border-radius: 6px;
            }}
        """)
        main_layout.addWidget(header)

        # Price Statistics Section
        price_frame = QFrame()
        price_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['background']};
                border-radius: 8px;
                padding: 5px;
            }}
        """)
        price_layout = QVBoxLayout(price_frame)

        price_title = QLabel("💰 FINAL PRICE")
        price_title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 12px;
                font-weight: bold;
                padding: 4px;
            }}
        """)
        price_layout.addWidget(price_title)

        # Price stats - vertical stack for narrow layout
        self.mean_card = StatCard("MEAN", "0.00")
        self.std_card = StatCard("STD DEV", "0.00")
        self.min_card = StatCard("MIN", "0.00")
        self.max_card = StatCard("MAX", "0.00")

        price_layout.addWidget(self.mean_card)
        price_layout.addWidget(self.std_card)
        price_layout.addWidget(self.min_card)
        price_layout.addWidget(self.max_card)
        main_layout.addWidget(price_frame)

        # Returns Section
        returns_frame = QFrame()
        returns_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['background']};
                border-radius: 8px;
                padding: 5px;
            }}
        """)
        returns_layout = QVBoxLayout(returns_frame)

        returns_title = QLabel("📈 RETURNS & RISK")
        returns_title.setStyleSheet(f"""
            QLabel {{
                color: {COLORS['text']};
                font-size: 12px;
                font-weight: bold;
                padding: 4px;
            }}
        """)
        returns_layout.addWidget(returns_title)

        # Returns stats - vertical stack for narrow layout
        self.profit_prob_card = ProgressCard("PROFIT PROBABILITY", 0, 100)
        returns_layout.addWidget(self.profit_prob_card)

        self.var_card = StatCard("VaR (95%)", "0.0%")
        self.es_card = StatCard("Expected Shortfall", "0.0%")

        returns_layout.addWidget(self.var_card)
        returns_layout.addWidget(self.es_card)
        main_layout.addWidget(returns_frame)

        # Add stretch to push content to top
        main_layout.addStretch()

    def update_statistics(self, stats):
        """Update all statistics with new data."""
        # Price statistics
        self.mean_card.update_value(f"{stats['final_price_mean']:.2f}")
        self.std_card.update_value(f"{stats['final_price_std']:.2f}")
        self.min_card.update_value(f"{stats['final_price_min']:.2f}")
        self.max_card.update_value(f"{stats['final_price_max']:.2f}")

        # Returns statistics with color coding
        profit_prob = stats['probability_profit']
        self.profit_prob_card.update_value(profit_prob)

        # VaR with color coding (negative is bad, so red for negative values)
        var_95 = stats['var_95']
        var_color = COLORS['error'] if var_95 < 0 else COLORS['success']
        self.var_card.update_value(f"{var_95:.1f}%", var_color)

        # Expected Shortfall
        es = stats['expected_shortfall']
        es_color = COLORS['error'] if es < 0 else COLORS['success']
        self.es_card.update_value(f"{es:.1f}%", es_color)

    def set_placeholder_text(self):
        """Set placeholder text when no simulation data is available."""
        self.mean_card.update_value("--")
        self.std_card.update_value("--")
        self.min_card.update_value("--")
        self.max_card.update_value("--")
        self.profit_prob_card.update_value(0)
        self.var_card.update_value("--")
        self.es_card.update_value("--")