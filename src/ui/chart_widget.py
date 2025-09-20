import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.animation import FuncAnimation
import pandas as pd
import time
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

        # Interactive features
        self.path_lines = []  # Store references to all path lines
        self.highlighted_line = None
        self.hover_dot = None
        self.tooltip_annotation = None
        self.last_hover_time = 0
        self.hover_threshold = 0.03  # Time threshold for hover updates (30 FPS)

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
        self.canvas.mpl_connect('motion_notify_event', self.on_mouse_move_and_hover)
        self.canvas.mpl_connect('axes_enter_event', self.on_axes_enter)
        self.canvas.mpl_connect('axes_leave_event', self.on_axes_leave)

        # Initial placeholder
        self.ax.text(0.5, 0.5, 'Run simulation to see price path chart',
                    transform=self.ax.transAxes, ha='center', va='center',
                    fontsize=14, color=COLORS['text_secondary'], style='italic')
        self.ax.set_xlim(0, 1)
        self.ax.set_ylim(0, 1)

        self.figure.tight_layout(pad=3.0)
        # Ensure labels are not clipped
        self.figure.subplots_adjust(left=0.1, bottom=0.15, right=0.95, top=0.9)

    def cleanup_old_data(self):
        """Clean up old data to prevent memory leaks."""
        try:
            # Clear animation if running
            if self.animation:
                self.animation.event_source.stop()
                self.animation = None

            # Clear cached line data
            for line in self.path_lines:
                if hasattr(line, '_cached_data'):
                    delattr(line, '_cached_data')

            # Clear line references
            self.path_lines.clear()

            # Clear highlights
            self.highlighted_line = None
            self.hover_dot = None
            self.tooltip_annotation = None

            # Force garbage collection for large datasets
            if self.current_data and len(self.current_data[1]) > 1000:
                import gc
                gc.collect()

        except Exception as e:
            print(f"Cleanup error: {e}")

    def update_chart(self, time_grid, price_paths, stats):
        """Update the chart with new simulation data."""
        # Clean up old data to prevent memory leaks
        self.cleanup_old_data()

        self.current_data = (time_grid, price_paths)
        self.current_stats = stats

        # Clear any existing interactive elements
        self.clear_highlight()

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

        # Clear previous path lines
        self.path_lines = []

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
            line = self.ax.plot(time_grid, path, color=color, alpha=alpha,
                               linewidth=CHART_CONFIG['line_width'],
                               picker=True, pickradius=5)[0]  # Enable picking

            # Store line reference with metadata
            line.path_index = i
            line.path_data = path
            line.original_color = color
            line.original_alpha = alpha
            line.original_linewidth = CHART_CONFIG['line_width']
            self.path_lines.append(line)

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
        # Get number of paths from the stored price data
        n_paths = len(self.current_data[1]) if self.current_data is not None else 0

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

    def on_mouse_move_and_hover(self, event):
        """Handle mouse movement for both panning and hover interactions."""
        if event.inaxes != self.ax:
            return

        # Handle panning with left mouse button
        if event.button == 1 and hasattr(self, 'press_data') and self.press_data:
            x_press, y_press = self.press_data
            if x_press is not None and y_press is not None:
                dx = event.xdata - x_press
                dy = event.ydata - y_press

                xlim = self.ax.get_xlim()
                ylim = self.ax.get_ylim()

                self.ax.set_xlim(xlim[0] - dx, xlim[1] - dx)
                self.ax.set_ylim(ylim[0] - dy, ylim[1] - dy)
                self.canvas.draw_idle()
        else:
            # Handle hover interactions when not panning
            self.on_hover(event)

    def on_hover(self, event):
        """Handle mouse hover over the chart for interactive features."""
        try:
            if event.inaxes != self.ax or not self.path_lines:
                return

            # Throttle updates for performance
            current_time = time.time()
            if current_time - self.last_hover_time < self.hover_threshold:
                return
            self.last_hover_time = current_time
        except Exception as e:
            print(f"Hover error: {e}")
            return

        try:
            # Find closest line to mouse cursor - optimized with numpy
            mouse_x, mouse_y = event.xdata, event.ydata
            if mouse_x is None or mouse_y is None:
                return

            # Pre-filter lines to only check those near the mouse position
            hover_range_x = (self.ax.get_xlim()[1] - self.ax.get_xlim()[0]) * 0.05
            hover_range_y = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * 0.05

            closest_line = None
            min_distance = float('inf')

            # Vectorized distance calculation
            for line in self.path_lines:
                # Get cached line data if available
                if not hasattr(line, '_cached_data'):
                    xdata, ydata = line.get_data()
                    line._cached_data = (xdata, ydata)
                else:
                    xdata, ydata = line._cached_data

                # Quick bbox check for performance
                if (mouse_x < np.min(xdata) - hover_range_x or mouse_x > np.max(xdata) + hover_range_x or
                    mouse_y < np.min(ydata) - hover_range_y or mouse_y > np.max(ydata) + hover_range_y):
                    continue

                # Vectorized distance calculation
                distances_sq = (xdata - mouse_x) ** 2 + (ydata - mouse_y) ** 2
                min_dist_on_line = np.sqrt(np.min(distances_sq))

                if min_dist_on_line < min_distance:
                    min_distance = min_dist_on_line
                    closest_line = line

            # Only highlight if mouse is close enough to a line
            hover_threshold = 0.05 * (self.ax.get_ylim()[1] - self.ax.get_ylim()[0])
            if min_distance < hover_threshold:
                self.highlight_path(closest_line, mouse_x, mouse_y)
            else:
                self.clear_highlight()
        except Exception as e:
            print(f"Hover detection error: {e}")
            self.clear_highlight()

    def on_axes_enter(self, event):
        """Change cursor when entering chart area."""
        from PySide6.QtCore import Qt
        self.canvas.setCursor(Qt.CrossCursor)

    def on_axes_leave(self, event):
        """Clear highlighting when mouse leaves the chart area."""
        self.clear_highlight()
        from PySide6.QtCore import Qt
        self.canvas.setCursor(Qt.ArrowCursor)

    def highlight_path(self, line, mouse_x, mouse_y):
        """Highlight a specific path and show tooltip."""
        try:
            if self.highlighted_line == line:
                return  # Already highlighted

            # Reset previous highlighting
            self.clear_highlight()

            # Highlight the selected line
            line.set_linewidth(2.5)
            line.set_alpha(0.9)
            line.set_zorder(100)  # Bring to front

            # Dim other lines
            for other_line in self.path_lines:
                if other_line != line:
                    other_line.set_alpha(0.15)

            self.highlighted_line = line

            # Show hover dot
            self.show_hover_dot(line, mouse_x, mouse_y)

            # Show tooltip
            self.show_tooltip(line, mouse_x, mouse_y)

            self.canvas.draw_idle()
        except Exception as e:
            print(f"Highlight error: {e}")
            self.clear_highlight()

    def clear_highlight(self):
        """Clear all highlighting and tooltips."""
        if self.highlighted_line:
            # Reset highlighted line
            self.highlighted_line.set_linewidth(self.highlighted_line.original_linewidth)
            self.highlighted_line.set_alpha(self.highlighted_line.original_alpha)
            self.highlighted_line.set_zorder(1)

            # Reset all other lines
            for line in self.path_lines:
                line.set_alpha(line.original_alpha)

            self.highlighted_line = None

        # Remove hover dot
        if self.hover_dot:
            self.hover_dot.remove()
            self.hover_dot = None

        # Remove tooltip
        if self.tooltip_annotation:
            self.tooltip_annotation.remove()
            self.tooltip_annotation = None

        self.canvas.draw_idle()

    def show_hover_dot(self, line, mouse_x, mouse_y):
        """Show a dot indicating the hover position on the line."""
        # Find the closest point on the line to mouse position
        xdata, ydata = line.get_data()
        distances = np.abs(xdata - mouse_x)
        closest_idx = np.argmin(distances)

        dot_x = xdata[closest_idx]
        dot_y = ydata[closest_idx]

        # Create hover dot
        self.hover_dot = self.ax.plot(dot_x, dot_y, 'o', color='white',
                                     markersize=6, markeredgecolor=line.original_color,
                                     markeredgewidth=2, zorder=200)[0]

    def show_tooltip(self, line, mouse_x, mouse_y):
        """Show detailed information tooltip for the hovered path."""
        # Get path data
        path_index = line.path_index
        path_data = line.path_data
        time_grid = self.current_data[0]

        # Find closest point
        distances = np.abs(time_grid - mouse_x)
        closest_idx = np.argmin(distances)

        current_time = time_grid[closest_idx]
        current_price = path_data[closest_idx]
        initial_price = path_data[0]
        final_price = path_data[-1]

        # Calculate statistics
        current_return = (current_price / initial_price - 1) * 100
        total_return = (final_price / initial_price - 1) * 100
        path_min = np.min(path_data)
        path_max = np.max(path_data)

        # Determine category
        if total_return > 10:
            category = "[+] Profit"
        elif total_return < -10:
            category = "[-] Loss"
        else:
            category = "[=] Neutral"

        # Format tooltip text
        tooltip_text = f"""Path #{path_index + 1}
─────────────────
Current: ${current_price:.2f}
Time: {current_time:.2f} years
Return: {current_return:+.1f}%

Final: ${final_price:.2f}
Total: {total_return:+.1f}%
Range: ${path_min:.0f}-${path_max:.0f}
{category}"""

        # Smart tooltip positioning to avoid going off-screen
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()

        # Determine tooltip position based on mouse location
        if mouse_x > (xlim[0] + xlim[1]) / 2:  # Right half
            xytext = (-120, 20)  # Position to the left
            ha = 'right'
        else:  # Left half
            xytext = (20, 20)  # Position to the right
            ha = 'left'

        if current_price > (ylim[0] + ylim[1]) / 2:  # Upper half
            xytext = (xytext[0], -80)  # Position below
            va = 'top'
        else:  # Lower half
            va = 'bottom'

        # Create annotation
        self.tooltip_annotation = self.ax.annotate(
            tooltip_text,
            xy=(mouse_x, current_price),
            xytext=xytext,
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.8',
                     facecolor=COLORS['surface'],
                     edgecolor=COLORS['accent'],
                     alpha=0.95),
            fontsize=8,
            color=COLORS['text'],
            ha=ha,
            va=va,
            zorder=300
        )

    def export_chart(self):
        """Export chart and/or data to files."""
        try:
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

                # Limit data size for performance
                if len(price_paths) > 1000:
                    QMessageBox.warning(self, "Large Dataset", "Exporting first 1000 paths for performance.")
                    price_paths = price_paths[:1000]

                # Create DataFrame
                df_data = {'Time': time_grid}
                for i, path in enumerate(price_paths):
                    df_data[f'Path_{i+1}'] = path

                df = pd.DataFrame(df_data)
                df.to_csv(filename, index=False)
                QMessageBox.information(self, "Export Success", f"Data exported to {filename}")

        except PermissionError:
            QMessageBox.critical(self, "Export Error", "Permission denied. Please check file permissions.")
        except FileNotFoundError:
            QMessageBox.critical(self, "Export Error", "Invalid file path.")
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