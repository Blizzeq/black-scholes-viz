import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import pandas as pd
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QFileDialog, QMessageBox
from PySide6.QtCore import Qt, QTimer

from ..utils.config import COLORS, CHART_CONFIG, PERCENTILES, PATH_COLORS


class ChartWidget(QWidget):
    """Widget containing the matplotlib chart for price path visualization."""

    def __init__(self):
        super().__init__()
        self.current_data = None
        self.current_stats = None
        self.animation = None
        self.setup_ui()
        self.setup_chart()

    def setup_ui(self):
        """Setup the chart widget UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Matplotlib figure
        self.figure = Figure(figsize=CHART_CONFIG['figsize'], dpi=CHART_CONFIG['dpi'])
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.show_percentiles = True

    def setup_chart(self):
        """Setup the matplotlib chart."""
        self.figure.patch.set_facecolor(COLORS['chart_bg'])
        self.ax = self.figure.add_subplot(111)

        # Style the axes
        self.ax.set_facecolor(COLORS['chart_bg'])
        self.ax.grid(True, alpha=0.3, color=COLORS['grid'])
        self.ax.spines['bottom'].set_color(COLORS['text'])
        self.ax.spines['top'].set_color(COLORS['text'])
        self.ax.spines['right'].set_color(COLORS['text'])
        self.ax.spines['left'].set_color(COLORS['text'])
        self.ax.tick_params(colors=COLORS['text'])
        self.ax.xaxis.label.set_color(COLORS['text'])
        self.ax.yaxis.label.set_color(COLORS['text'])

        # Enable interactive navigation
        self.canvas.mpl_connect('scroll_event', self.on_scroll)
        self.canvas.mpl_connect('button_press_event', self.on_button_press)
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move)

        # Initial placeholder
        self.ax.text(0.5, 0.5, 'Run simulation to see price path chart',
                    transform=self.ax.transAxes, ha='center', va='center',
                    fontsize=14, color=COLORS['text_secondary'], style='italic')
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)

        self.figure.tight_layout(pad=3.0)
        # Ensure labels are not clipped
        self.figure.subplots_adjust(left=0.1, bottom=0.15, right=0.95, top=0.9)

    def update_chart(self, time_grid, price_paths, stats):
        """Update the chart with new simulation data."""
        self.current_data = (time_grid, price_paths)
        self.current_stats = stats

        # Clear previous plot
        self.ax.clear()
        self.setup_chart_style()

        # Plot price paths
        self.plot_price_paths(time_grid, price_paths, stats)

        # Plot percentiles if enabled
        if self.show_percentiles:
            self.plot_percentiles(time_grid, stats)

        # Update labels and title
        self.update_labels(stats)

        # Add color legend for paths
        self.add_color_legend()

        # If percentiles legend exists, ensure it's properly positioned
        if hasattr(self, 'percentiles_legend') and self.show_percentiles:
            # Add legend back to axes after color legend
            self.ax.add_artist(self.percentiles_legend)

        # Ensure proper layout without clipping
        self.figure.tight_layout(pad=3.0)
        self.figure.subplots_adjust(left=0.1, bottom=0.15, right=0.95, top=0.85)

        self.canvas.draw()

    def setup_chart_style(self):
        """Setup chart styling after clearing."""
        self.ax.set_facecolor(COLORS['chart_bg'])
        self.ax.grid(True, alpha=0.3, color=COLORS['grid'])
        self.ax.spines['bottom'].set_color(COLORS['text'])
        self.ax.spines['top'].set_color(COLORS['text'])
        self.ax.spines['right'].set_color(COLORS['text'])
        self.ax.spines['left'].set_color(COLORS['text'])
        self.ax.tick_params(colors=COLORS['text'])

    def plot_price_paths(self, time_grid, price_paths, stats):
        """Plot individual price paths with color coding."""
        n_paths = len(price_paths)
        S0 = price_paths[0, 0]  # Initial price

        # Color paths based on final performance
        final_prices = price_paths[:, -1]
        final_returns = (final_prices / S0 - 1)

        # Create color map based on returns
        colors = []
        for ret in final_returns:
            if ret > 0.1:  # > 10% gain
                colors.append(PATH_COLORS['profit'])
            elif ret < -0.1:  # > 10% loss
                colors.append(PATH_COLORS['loss'])
            else:  # Neutral
                colors.append(PATH_COLORS['neutral'])

        # Plot paths with reduced alpha for better visualization
        alpha = max(0.1, min(0.8, 200 / n_paths))  # Adaptive alpha based on number of paths

        for i, (path, color) in enumerate(zip(price_paths, colors)):
            self.ax.plot(time_grid, path, color=color, alpha=alpha,
                        linewidth=CHART_CONFIG['line_width'])

    def plot_percentiles(self, time_grid, stats):
        """Plot percentile lines."""
        percentiles = stats['percentiles']

        percentile_colors = {
            'p10': '#ff6b6b',   # Red
            'p25': '#ffa726',   # Orange
            'p50': '#66bb6a',   # Green (median)
            'p75': '#42a5f5',   # Blue
            'p90': '#ab47bc'    # Purple
        }

        for p in PERCENTILES:
            p_key = f'p{p}'
            if p_key in percentiles:
                color = percentile_colors.get(p_key, COLORS['accent'])
                linewidth = 3 if p == 50 else 2  # Thicker line for median
                linestyle = '-' if p == 50 else '--'

                self.ax.plot(time_grid, percentiles[p_key], color=color,
                           linewidth=linewidth, linestyle=linestyle,
                           alpha=CHART_CONFIG['percentile_alpha'],
                           label=f'{p}th percentile')

        # Add legend for percentiles
        if self.show_percentiles:
            percentiles_legend = self.ax.legend(loc='upper left', fancybox=True, shadow=True,
                                               facecolor=COLORS['surface'], edgecolor=COLORS['accent'])

            # Fix text color for percentiles legend
            for text in percentiles_legend.get_texts():
                text.set_color(COLORS['text'])

            # Store reference for later use
            self.percentiles_legend = percentiles_legend

    def update_labels(self, stats):
        """Update chart labels and title."""
        n_paths = len(stats['percentiles']['p50']) if 'percentiles' in stats else 0

        self.ax.set_xlabel('Time (years)', color=COLORS['text'], fontsize=12)
        self.ax.set_ylabel('Price', color=COLORS['text'], fontsize=12)

        title = f'Black-Scholes Simulation: {n_paths} price paths\n'
        title += f'Profit Probability: {stats["probability_profit"]:.1f}% | '
        title += f'VaR (95%): {stats["var_95"]:.1f}%'

        self.ax.set_title(title, color=COLORS['text'], fontsize=11, pad=20)

    def start_animation(self):
        """Start animated visualization of price paths."""
        if self.current_data is None:
            return

        time_grid, price_paths = self.current_data
        n_paths = min(len(price_paths), CHART_CONFIG['max_paths_for_animation'])

        # Clear and setup
        self.ax.clear()
        self.setup_chart_style()

        # Setup animation data
        self.animation_paths = price_paths[:n_paths]
        self.animation_lines = []

        # Create empty lines for animation
        for i in range(n_paths):
            line, = self.ax.plot([], [], alpha=0.6, linewidth=1)
            self.animation_lines.append(line)

        # Set up axes
        self.ax.set_xlim(time_grid[0], time_grid[-1])
        y_min = np.min(price_paths) * 0.95
        y_max = np.max(price_paths) * 1.05
        self.ax.set_ylim(y_min, y_max)

        # Animation function
        def animate(frame):
            if frame < len(time_grid):
                for i, line in enumerate(self.animation_lines):
                    if i < len(self.animation_paths):
                        x_data = time_grid[:frame+1]
                        y_data = self.animation_paths[i][:frame+1]
                        line.set_data(x_data, y_data)

                        # Color based on current performance
                        if frame > 0:
                            current_return = (y_data[-1] / y_data[0] - 1)
                            if current_return > 0.1:  # > 10% profit
                                line.set_color(PATH_COLORS['profit'])
                            elif current_return < -0.1:  # < -10% loss
                                line.set_color(PATH_COLORS['loss'])
                            else:  # Neutral (-10% to +10%)
                                line.set_color(PATH_COLORS['neutral'])

            return self.animation_lines

        # Start animation
        frames = len(time_grid)
        interval = max(10, min(100, 3000 // frames))  # Adaptive interval

        self.animation = FuncAnimation(self.figure, animate, frames=frames,
                                     interval=interval, blit=False, repeat=False)

        self.update_labels(self.current_stats)
        self.canvas.draw()

    def toggle_percentiles(self):
        """Toggle percentile lines visibility."""
        self.show_percentiles = not self.show_percentiles
        if self.current_data is not None:
            time_grid, price_paths = self.current_data
            self.update_chart(time_grid, price_paths, self.current_stats)

    def reset_zoom(self):
        """Reset chart zoom to show all data."""
        if self.current_data is not None:
            time_grid, price_paths = self.current_data
            self.ax.set_xlim(time_grid[0], time_grid[-1])
            y_min = np.min(price_paths) * 0.95
            y_max = np.max(price_paths) * 1.05
            self.ax.set_ylim(y_min, y_max)
            self.canvas.draw()

    def on_scroll(self, event):
        """Handle mouse scroll for zooming."""
        if event.inaxes != self.ax:
            return

        scale_factor = 1.1 if event.step < 0 else 0.9
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Zoom around mouse position
        x_center = event.xdata
        y_center = event.ydata

        if x_center is not None and y_center is not None:
            x_range = (xlim[1] - xlim[0]) * scale_factor
            y_range = (ylim[1] - ylim[0]) * scale_factor

            self.ax.set_xlim(x_center - x_range/2, x_center + x_range/2)
            self.ax.set_ylim(y_center - y_range/2, y_center + y_range/2)
            self.canvas.draw()

    def on_button_press(self, event):
        """Handle mouse button press for panning."""
        if event.inaxes != self.ax:
            return
        self.press_data = (event.xdata, event.ydata)

    def on_mouse_move(self, event):
        """Handle mouse movement for panning and tooltips."""
        if event.inaxes != self.ax:
            return

        # Panning with left mouse button
        if event.button == 1 and hasattr(self, 'press_data') and self.press_data:
            x_press, y_press = self.press_data
            if x_press is not None and y_press is not None:
                dx = event.xdata - x_press
                dy = event.ydata - y_press

                xlim = self.ax.get_xlim()
                ylim = self.ax.get_ylim()

                self.ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
                self.ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
                self.canvas.draw()

    def export_chart(self):
        """Export chart and/or data to files."""
        if self.current_data is None:
            QMessageBox.warning(self, "Export Warning", "No data to export. Please run a simulation first.")
            return

        # File dialog to choose export type
        dialog = QFileDialog()
        file_types = "PNG Image (*.png);;PDF Document (*.pdf);;CSV Data (*.csv);;All Files (*.*)"
        filename, selected_type = dialog.getSaveFileName(
            self, "Export Chart/Data", "black_scholes_simulation", file_types
        )

        if not filename:
            return

        try:
            if selected_type.startswith("PNG") or filename.endswith('.png'):
                # Export chart as PNG
                self.figure.savefig(filename, dpi=300, bbox_inches='tight',
                                  facecolor=COLORS['chart_bg'], edgecolor='none')
                QMessageBox.information(self, "Export Success", f"Chart exported to {filename}")

            elif selected_type.startswith("PDF") or filename.endswith('.pdf'):
                # Export chart as PDF
                self.figure.savefig(filename, format='pdf', bbox_inches='tight',
                                  facecolor=COLORS['chart_bg'], edgecolor='none')
                QMessageBox.information(self, "Export Success", f"Chart exported to {filename}")

            elif selected_type.startswith("CSV") or filename.endswith('.csv'):
                # Export simulation data as CSV
                time_grid, price_paths = self.current_data

                # Create DataFrame
                df_data = {'Time': time_grid}
                for i, path in enumerate(price_paths):
                    df_data[f'Path_{i+1}'] = path

                df = pd.DataFrame(df_data)
                df.to_csv(filename, index=False)
                QMessageBox.information(self, "Export Success", f"Data exported to {filename}")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    def add_color_legend(self):
        """Add legend explaining path colors."""
        if not self.current_data:
            return

        # Create custom legend elements
        from matplotlib.lines import Line2D
        legend_elements = [
            Line2D([0], [0], color=PATH_COLORS['profit'], lw=2, label='Profit (>10%)'),
            Line2D([0], [0], color=PATH_COLORS['neutral'], lw=2, label='Neutral (-10% to +10%)'),
            Line2D([0], [0], color=PATH_COLORS['loss'], lw=2, label='Loss (<-10%)')
        ]

        paths_legend = self.ax.legend(handles=legend_elements, loc='lower left',
                                     fancybox=True, shadow=True, fontsize=9,
                                     facecolor=COLORS['surface'], edgecolor=COLORS['accent'])

        # Fix text color - make it white/light
        for text in paths_legend.get_texts():
            text.set_color(COLORS['text'])

        # Store reference for later positioning
        self.paths_legend = paths_legend