import numpy as np
from typing import Tuple, List


class BlackScholesSimulator:
    """
    Simulator for Black-Scholes price paths using Geometric Brownian Motion.

    The model follows: dS(t) = μS(t)dt + σS(t)dW(t)
    Discrete solution: S(t) = S₀ * exp((μ - σ²/2)t + σ√dt * Z)
    """

    def __init__(self, S0: float, mu: float, sigma: float, T: float, dt: float = 1/252):
        """
        Initialize the Black-Scholes simulator.

        Args:
            S0: Initial stock price
            mu: Expected return (drift)
            sigma: Volatility
            T: Time horizon in years
            dt: Time step (default: 1 trading day = 1/252 years)
        """
        self.S0 = S0
        self.mu = mu
        self.sigma = sigma
        self.T = T
        self.dt = dt
        self.n_steps = int(T / dt)
        self.time_grid = np.linspace(0, T, self.n_steps + 1)

    def simulate_path(self, random_seed: int = None) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate a single price path.

        Args:
            random_seed: Optional random seed for reproducibility

        Returns:
            Tuple of (time_grid, price_path)
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        # Generate random increments
        dW = np.random.normal(0, np.sqrt(self.dt), self.n_steps)

        # Calculate price path using vectorized operations
        drift = (self.mu - 0.5 * self.sigma**2) * self.dt
        diffusion = self.sigma * dW

        # Cumulative sum for the exponent
        log_returns = np.cumsum(drift + diffusion)

        # Price path starting from S0
        price_path = np.zeros(self.n_steps + 1)
        price_path[0] = self.S0
        price_path[1:] = self.S0 * np.exp(log_returns)

        return self.time_grid, price_path

    def simulate_multiple_paths(self, n_paths: int, parallel: bool = True) -> Tuple[np.ndarray, np.ndarray]:
        """
        Simulate multiple price paths efficiently.

        Args:
            n_paths: Number of paths to simulate
            parallel: Whether to use vectorized computation (recommended for large n_paths)

        Returns:
            Tuple of (time_grid, price_paths_matrix)
            price_paths_matrix shape: (n_paths, n_steps + 1)
        """
        if parallel and n_paths > 10:
            return self._simulate_paths_vectorized(n_paths)
        else:
            return self._simulate_paths_sequential(n_paths)

    def _simulate_paths_vectorized(self, n_paths: int) -> Tuple[np.ndarray, np.ndarray]:
        """Vectorized simulation for better performance with many paths."""
        # Generate all random numbers at once
        dW = np.random.normal(0, np.sqrt(self.dt), (n_paths, self.n_steps))

        # Calculate drift and diffusion components
        drift = (self.mu - 0.5 * self.sigma**2) * self.dt
        diffusion = self.sigma * dW

        # Cumulative sum along time axis
        log_returns = np.cumsum(drift + diffusion, axis=1)

        # Initialize price paths
        price_paths = np.zeros((n_paths, self.n_steps + 1))
        price_paths[:, 0] = self.S0
        price_paths[:, 1:] = self.S0 * np.exp(log_returns)

        return self.time_grid, price_paths

    def _simulate_paths_sequential(self, n_paths: int) -> Tuple[np.ndarray, np.ndarray]:
        """Sequential simulation for smaller number of paths."""
        price_paths = np.zeros((n_paths, self.n_steps + 1))

        for i in range(n_paths):
            _, path = self.simulate_path()
            price_paths[i] = path

        return self.time_grid, price_paths

    def get_statistics(self, price_paths: np.ndarray) -> dict:
        """
        Calculate statistics for the simulated paths.

        Args:
            price_paths: Array of shape (n_paths, n_steps + 1)

        Returns:
            Dictionary with various statistics
        """
        final_prices = price_paths[:, -1]
        returns = (final_prices / self.S0 - 1) * 100

        # Percentiles for the fan chart
        percentiles = [5, 10, 25, 50, 75, 90, 95]
        price_percentiles = {}

        for p in percentiles:
            price_percentiles[f'p{p}'] = np.percentile(price_paths, p, axis=0)

        # Basic statistics
        stats = {
            'final_price_mean': np.mean(final_prices),
            'final_price_std': np.std(final_prices),
            'final_price_min': np.min(final_prices),
            'final_price_max': np.max(final_prices),
            'returns_mean': np.mean(returns),
            'returns_std': np.std(returns),
            'probability_profit': np.mean(final_prices > self.S0) * 100,
            'percentiles': price_percentiles,
            'var_95': np.percentile(returns, 5),  # Value at Risk (95%)
            'var_99': np.percentile(returns, 1),  # Value at Risk (99%)
        }

        # Expected Shortfall (Conditional VaR)
        var_95_threshold = np.percentile(final_prices, 5)
        shortfall_prices = final_prices[final_prices <= var_95_threshold]
        if len(shortfall_prices) > 0:
            stats['expected_shortfall'] = (np.mean(shortfall_prices) / self.S0 - 1) * 100
        else:
            stats['expected_shortfall'] = stats['var_95']

        return stats

    def update_parameters(self, S0: float = None, mu: float = None,
                         sigma: float = None, T: float = None):
        """Update simulation parameters."""
        if S0 is not None:
            self.S0 = S0
        if mu is not None:
            self.mu = mu
        if sigma is not None:
            self.sigma = sigma
        if T is not None:
            self.T = T
            self.n_steps = int(T / self.dt)
            self.time_grid = np.linspace(0, T, self.n_steps + 1)


def create_scenario_presets() -> dict:
    """Create predefined scenarios for quick testing."""
    return {
        "stable_growth": {"mu": 0.08, "sigma": 0.15},
        "high_volatility": {"mu": 0.05, "sigma": 0.40},
        "bear_market": {"mu": -0.10, "sigma": 0.25},
        "bull_market": {"mu": 0.15, "sigma": 0.20},
        "crisis": {"mu": -0.20, "sigma": 0.60},
        "low_vol": {"mu": 0.06, "sigma": 0.08}
    }