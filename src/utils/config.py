"""
Configuration and constants for the Black-Scholes Visualizer
"""

# Application Settings
APP_NAME = "Black-Scholes Simulator"
APP_VERSION = "1.0.0"

# Default Parameters
DEFAULT_S0 = 100.0
DEFAULT_MU = 0.08  # 8% annual return
DEFAULT_SIGMA = 0.20  # 20% volatility
DEFAULT_T = 1.0  # 1 year
DEFAULT_N_PATHS = 500
DEFAULT_N_STEPS = 252  # Trading days in a year

# Parameter Ranges
RANGES = {
    'n_paths': (10, 1000),
    'time_horizon': (0.1, 5.0),  # 0.1 to 5 years
    'S0': (1.0, 1000.0),
    'mu': (-0.50, 0.50),  # -50% to +50% annual return
    'sigma': (0.05, 1.00)  # 5% to 100% volatility
}

# UI Colors (Dark + Green Theme)
COLORS = {
    'background': '#1a1a2e',
    'surface': '#16213e',
    'accent': '#388e3c',  # Darker, more subtle green
    'accent_dark': '#2e7d32',  # Even darker green
    'text': '#f5f5f5',
    'text_secondary': '#b0b0b0',
    'success': '#4caf50',
    'warning': '#ffe66d',
    'error': '#f44336',
    'chart_bg': '#0f0f23',
    'grid': '#2a2a3e'
}

# Chart Settings
CHART_CONFIG = {
    'dpi': 100,
    'figsize': (12, 8),
    'line_alpha': 0.3,
    'line_width': 0.8,
    'percentile_alpha': 0.7,
    'percentile_width': 2,
    'animation_interval': 50,  # milliseconds
    'max_paths_for_animation': 200
}

# Percentiles to highlight
PERCENTILES = [10, 25, 50, 75, 90]

# Color gradients for paths
PATH_COLORS = {
    'profit': '#4caf50',  # Green for positive returns
    'loss': '#f44336',    # Red for negative returns
    'neutral': '#9e9e9e'  # Gray for neutral
}

# Statistics panel configuration
STATS_PRECISION = {
    'price': 2,
    'percentage': 1,
    'volatility': 3
}