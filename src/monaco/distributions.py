"""Probability distribution classes for task duration estimation."""

import math
import random
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Distribution(ABC):
    """Abstract base class for probability distributions used in task estimation."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the distribution name (for display and serialization)."""
        pass

    @abstractmethod
    def sample(self) -> float:
        """Draw a single sample from the distribution.

        Returns
        -------
        float
            A non-negative sample from the distribution.
        """
        pass

    @abstractmethod
    def validate(self) -> None:
        """Validate distribution parameters.

        Raises
        ------
        ValueError
            If parameters are invalid.
        """
        pass

    @abstractmethod
    def get_display_params(self) -> str:
        """Return a string representation of parameters for display.

        Returns
        -------
        str
            Human-readable parameter string, e.g., "(2-5-10)" for triangular.
        """
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize distribution to dictionary (for YAML/JSON export).

        Returns
        -------
        Dict[str, Any]
            Dictionary representation with 'type' and parameters.
        """
        pass


class TriangularDistribution(Distribution):
    """Triangular probability distribution for task estimation.

    Parameters
    ----------
    min_value : float
        Minimum possible duration (must be >= 0).
    mode_value : float
        Most likely duration (must satisfy min <= mode <= max).
    max_value : float
        Maximum possible duration.
    """

    def __init__(self, min_value: float, mode_value: float, max_value: float) -> None:
        self.min_value = min_value
        self.mode_value = mode_value
        self.max_value = max_value
        self.validate()

    @property
    def name(self) -> str:
        return "triangular"

    def sample(self) -> float:
        return random.triangular(
            low=self.min_value, mode=self.mode_value, high=self.max_value
        )

    def validate(self) -> None:
        if self.min_value < 0:
            raise ValueError(f"min_value must be non-negative, got {self.min_value}")
        if self.mode_value < 0:
            raise ValueError(f"mode_value must be non-negative, got {self.mode_value}")
        if self.max_value < 0:
            raise ValueError(f"max_value must be non-negative, got {self.max_value}")
        if not (self.min_value <= self.mode_value <= self.max_value):
            raise ValueError(
                f"Must have min <= mode <= max. "
                f"Got min={self.min_value}, mode={self.mode_value}, max={self.max_value}"
            )

    def get_display_params(self) -> str:
        return f"({self.min_value}-{self.mode_value}-{self.max_value})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "triangular",
            "min_duration": self.min_value,
            "mode_duration": self.mode_value,
            "max_duration": self.max_value,
        }


class UniformDistribution(Distribution):
    """Uniform probability distribution for task estimation.

    Parameters
    ----------
    min_value : float
        Minimum possible duration (must be >= 0).
    max_value : float
        Maximum possible duration (must be >= min_value).
    """

    def __init__(self, min_value: float, max_value: float) -> None:
        self.min_value = min_value
        self.max_value = max_value
        self.validate()

    @property
    def name(self) -> str:
        return "uniform"

    def sample(self) -> float:
        return random.uniform(self.min_value, self.max_value)

    def validate(self) -> None:
        if self.min_value < 0:
            raise ValueError(f"min_value must be non-negative, got {self.min_value}")
        if self.max_value < 0:
            raise ValueError(f"max_value must be non-negative, got {self.max_value}")
        if self.min_value > self.max_value:
            raise ValueError(
                f"Must have min <= max. Got min={self.min_value}, max={self.max_value}"
            )

    def get_display_params(self) -> str:
        return f"({self.min_value}-{self.max_value})"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "uniform",
            "min_duration": self.min_value,
            "max_duration": self.max_value,
        }


class NormalDistribution(Distribution):
    """Truncated Normal (Gaussian) distribution for task estimation.

    Uses truncated normal distribution to ensure non-negative durations.
    If a sampled value is outside bounds, it resamples until a valid value
    is obtained.

    Parameters
    ----------
    mean : float
        Mean of the distribution (must be > 0).
    std_dev : float
        Standard deviation (must be > 0).
    min_value : float, optional
        Minimum bound for truncation (default: 0).
    max_value : float, optional
        Maximum bound for truncation (default: None, unbounded above).

    Notes
    -----
    The implementation uses rejection sampling for simplicity. For mean values
    significantly greater than std_dev (e.g., mean > 3 * std_dev), the probability
    of rejection is negligible.
    """

    MAX_RESAMPLE_ATTEMPTS = 1000

    def __init__(
        self,
        mean: float,
        std_dev: float,
        min_value: float = 0.0,
        max_value: Optional[float] = None,
    ) -> None:
        self.mean = mean
        self.std_dev = std_dev
        self.min_value = min_value
        self.max_value = max_value
        self.validate()

    @property
    def name(self) -> str:
        return "normal"

    def sample(self) -> float:
        """Sample using rejection sampling for truncated normal."""
        for _ in range(self.MAX_RESAMPLE_ATTEMPTS):
            value = random.gauss(self.mean, self.std_dev)
            if value >= self.min_value:
                if self.max_value is None or value <= self.max_value:
                    return value
        # Fallback: clamp to bounds (should rarely happen with valid params)
        return max(self.min_value, min(value, self.max_value or value))

    def validate(self) -> None:
        if self.mean <= 0:
            raise ValueError(f"mean must be positive, got {self.mean}")
        if self.std_dev <= 0:
            raise ValueError(f"std_dev must be positive, got {self.std_dev}")
        if self.min_value < 0:
            raise ValueError(f"min_value must be non-negative, got {self.min_value}")
        if self.max_value is not None:
            if self.max_value < self.min_value:
                raise ValueError(
                    f"max_value must be >= min_value. "
                    f"Got min={self.min_value}, max={self.max_value}"
                )

    def get_display_params(self) -> str:
        if self.max_value is not None:
            return f"(mean={self.mean}, std={self.std_dev}, [{self.min_value}-{self.max_value}])"
        return f"(mean={self.mean}, std={self.std_dev})"

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "type": "normal",
            "mean": self.mean,
            "std_dev": self.std_dev,
        }
        if self.min_value != 0.0:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value
        return result


class PERTDistribution(Distribution):
    """PERT (Program Evaluation and Review Technique) distribution.

    The PERT distribution is a smooth version of the triangular distribution,
    using a Beta distribution scaled to [min, max]. It gives more weight to
    the mode (most likely value) compared to the triangular distribution.

    The mean is calculated as: (min + 4*mode + max) / 6

    Parameters
    ----------
    min_value : float
        Minimum possible duration (must be >= 0).
    mode_value : float
        Most likely duration (must satisfy min <= mode <= max).
    max_value : float
        Maximum possible duration.
    lamb : float, optional
        Shape parameter (default: 4). Higher values give more weight to mode.
        Traditional PERT uses lamb=4.

    Notes
    -----
    PERT is widely used in project management for schedule risk analysis.
    It produces more realistic estimates than triangular by reducing the
    impact of extreme values.
    """

    def __init__(
        self,
        min_value: float,
        mode_value: float,
        max_value: float,
        lamb: float = 4.0,
    ) -> None:
        self.min_value = min_value
        self.mode_value = mode_value
        self.max_value = max_value
        self.lamb = lamb
        self.validate()
        # Pre-calculate alpha and beta for the underlying Beta distribution
        self._calculate_beta_params()

    def _calculate_beta_params(self) -> None:
        """Calculate alpha and beta parameters for the Beta distribution."""
        range_val = self.max_value - self.min_value
        if range_val == 0:
            # Degenerate case: all values equal
            self._alpha = 1.0
            self._beta = 1.0
        else:
            # Mean of PERT
            mu = (self.min_value + self.lamb * self.mode_value + self.max_value) / (
                self.lamb + 2
            )
            # Calculate alpha based on mode position
            if self.mode_value == self.min_value:
                self._alpha = 1.0
                self._beta = self.lamb + 1
            elif self.mode_value == self.max_value:
                self._alpha = self.lamb + 1
                self._beta = 1.0
            else:
                # Standard PERT formula
                self._alpha = 1 + self.lamb * (mu - self.min_value) / range_val
                self._beta = 1 + self.lamb * (self.max_value - mu) / range_val

    @property
    def name(self) -> str:
        return "pert"

    def sample(self) -> float:
        """Sample from the PERT distribution using Beta distribution."""
        if self.max_value == self.min_value:
            return self.min_value
        # Sample from Beta(alpha, beta) and scale to [min, max]
        beta_sample = random.betavariate(self._alpha, self._beta)
        return self.min_value + beta_sample * (self.max_value - self.min_value)

    def validate(self) -> None:
        if self.min_value < 0:
            raise ValueError(f"min_value must be non-negative, got {self.min_value}")
        if self.mode_value < 0:
            raise ValueError(f"mode_value must be non-negative, got {self.mode_value}")
        if self.max_value < 0:
            raise ValueError(f"max_value must be non-negative, got {self.max_value}")
        if not (self.min_value <= self.mode_value <= self.max_value):
            raise ValueError(
                f"Must have min <= mode <= max. "
                f"Got min={self.min_value}, mode={self.mode_value}, max={self.max_value}"
            )
        if self.lamb <= 0:
            raise ValueError(f"lamb must be positive, got {self.lamb}")

    def get_display_params(self) -> str:
        return f"({self.min_value}-{self.mode_value}-{self.max_value})"

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "type": "pert",
            "min_duration": self.min_value,
            "mode_duration": self.mode_value,
            "max_duration": self.max_value,
        }
        if self.lamb != 4.0:
            result["lamb"] = self.lamb
        return result


class LogNormalDistribution(Distribution):
    """Log-Normal distribution for task estimation.

    The Log-Normal distribution is useful for tasks that have a long right
    tail (rare but significant delays). All sampled values are positive.

    Parameters
    ----------
    mean : float
        Mean of the distribution (must be > 0).
    std_dev : float
        Standard deviation of the distribution (must be > 0).
    min_value : float, optional
        Minimum bound (default: 0). Values below this are resampled.
    max_value : float, optional
        Maximum bound (default: None). Values above this are resampled.

    Notes
    -----
    The mean and std_dev parameters refer to the actual distribution
    (not the underlying normal). The implementation converts these to
    mu and sigma for the underlying normal distribution.

    Log-Normal is commonly used for:
    - Tasks with high uncertainty and potential for delays
    - When historical data shows right-skewed completion times
    - Modeling multiplicative effects of many small factors
    """

    MAX_RESAMPLE_ATTEMPTS = 1000

    def __init__(
        self,
        mean: float,
        std_dev: float,
        min_value: float = 0.0,
        max_value: Optional[float] = None,
    ) -> None:
        self.mean = mean
        self.std_dev = std_dev
        self.min_value = min_value
        self.max_value = max_value
        self.validate()
        # Calculate mu and sigma for the underlying normal distribution
        self._calculate_normal_params()

    def _calculate_normal_params(self) -> None:
        """Calculate mu and sigma for the underlying normal distribution."""
        # Given mean (m) and std_dev (s) of log-normal:
        # mu = ln(m^2 / sqrt(s^2 + m^2))
        # sigma = sqrt(ln(1 + s^2/m^2))
        variance = self.std_dev**2
        mean_sq = self.mean**2
        self._mu = math.log(mean_sq / math.sqrt(variance + mean_sq))
        self._sigma = math.sqrt(math.log(1 + variance / mean_sq))

    @property
    def name(self) -> str:
        return "lognormal"

    def sample(self) -> float:
        """Sample from the log-normal distribution."""
        for _ in range(self.MAX_RESAMPLE_ATTEMPTS):
            value = random.lognormvariate(self._mu, self._sigma)
            if value >= self.min_value:
                if self.max_value is None or value <= self.max_value:
                    return value
        # Fallback: clamp to bounds
        return max(self.min_value, min(value, self.max_value or value))

    def validate(self) -> None:
        if self.mean <= 0:
            raise ValueError(f"mean must be positive, got {self.mean}")
        if self.std_dev <= 0:
            raise ValueError(f"std_dev must be positive, got {self.std_dev}")
        if self.min_value < 0:
            raise ValueError(f"min_value must be non-negative, got {self.min_value}")
        if self.max_value is not None:
            if self.max_value < self.min_value:
                raise ValueError(
                    f"max_value must be >= min_value. "
                    f"Got min={self.min_value}, max={self.max_value}"
                )

    def get_display_params(self) -> str:
        if self.max_value is not None:
            return f"(mean={self.mean}, std={self.std_dev}, [{self.min_value}-{self.max_value}])"
        return f"(mean={self.mean}, std={self.std_dev})"

    def to_dict(self) -> Dict[str, Any]:
        result: Dict[str, Any] = {
            "type": "lognormal",
            "mean": self.mean,
            "std_dev": self.std_dev,
        }
        if self.min_value != 0.0:
            result["min_value"] = self.min_value
        if self.max_value is not None:
            result["max_value"] = self.max_value
        return result


class BetaDistribution(Distribution):
    """Beta distribution scaled to a [min, max] range.

    The Beta distribution is highly flexible and can model many different
    shapes depending on the alpha and beta parameters.

    Parameters
    ----------
    alpha : float
        First shape parameter (must be > 0).
    beta : float
        Second shape parameter (must be > 0).
    min_value : float, optional
        Minimum value (default: 0).
    max_value : float
        Maximum value (must be > min_value).

    Notes
    -----
    Common parameter combinations:
    - alpha=1, beta=1: Uniform distribution
    - alpha=2, beta=2: Symmetric, bell-shaped
    - alpha=2, beta=5: Right-skewed (more likely to be below mean)
    - alpha=5, beta=2: Left-skewed (more likely to be above mean)
    - alpha=0.5, beta=0.5: U-shaped (extremes more likely)

    The mean of the scaled distribution is:
        min + (max - min) * alpha / (alpha + beta)
    """

    def __init__(
        self,
        alpha: float,
        beta: float,
        min_value: float = 0.0,
        max_value: float = 1.0,
    ) -> None:
        self.alpha = alpha
        self.beta = beta
        self.min_value = min_value
        self.max_value = max_value
        self.validate()

    @property
    def name(self) -> str:
        return "beta"

    def sample(self) -> float:
        """Sample from the scaled Beta distribution."""
        beta_sample = random.betavariate(self.alpha, self.beta)
        return self.min_value + beta_sample * (self.max_value - self.min_value)

    def validate(self) -> None:
        if self.alpha <= 0:
            raise ValueError(f"alpha must be positive, got {self.alpha}")
        if self.beta <= 0:
            raise ValueError(f"beta must be positive, got {self.beta}")
        if self.min_value < 0:
            raise ValueError(f"min_value must be non-negative, got {self.min_value}")
        if self.max_value <= self.min_value:
            raise ValueError(
                f"max_value must be > min_value. "
                f"Got min={self.min_value}, max={self.max_value}"
            )

    def get_display_params(self) -> str:
        return f"(α={self.alpha}, β={self.beta}, [{self.min_value}-{self.max_value}])"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "beta",
            "alpha": self.alpha,
            "beta": self.beta,
            "min_value": self.min_value,
            "max_value": self.max_value,
        }


# Registry of distribution types
DISTRIBUTION_REGISTRY: Dict[str, type] = {
    "triangular": TriangularDistribution,
    "uniform": UniformDistribution,
    "normal": NormalDistribution,
    "pert": PERTDistribution,
    "lognormal": LogNormalDistribution,
    "beta": BetaDistribution,
}


def create_distribution(
    estimator: str,
    min_duration: Optional[float] = None,
    mode_duration: Optional[float] = None,
    max_duration: Optional[float] = None,
    mean: Optional[float] = None,
    std_dev: Optional[float] = None,
    min_value: Optional[float] = None,
    max_value: Optional[float] = None,
    alpha: Optional[float] = None,
    beta: Optional[float] = None,
    lamb: Optional[float] = None,
) -> Distribution:
    """Factory function to create Distribution instances from parameters.

    This function supports both the legacy parameter names (min_duration, etc.)
    for backward compatibility and new parameters for various distributions.

    Parameters
    ----------
    estimator : str
        Distribution type: "triangular", "uniform", "normal", "pert",
        "lognormal", or "beta".
    min_duration, mode_duration, max_duration : float, optional
        Parameters for Triangular, Uniform, and PERT distributions.
    mean, std_dev : float, optional
        Parameters for Normal and LogNormal distributions.
    min_value, max_value : float, optional
        Bounds for distributions (Normal, LogNormal, Beta).
    alpha, beta : float, optional
        Shape parameters for Beta distribution.
    lamb : float, optional
        Shape parameter for PERT distribution (default: 4).

    Returns
    -------
    Distribution
        Configured distribution instance.

    Raises
    ------
    ValueError
        If estimator is unknown or required parameters are missing.
    """
    if estimator not in DISTRIBUTION_REGISTRY:
        raise ValueError(
            f"Unknown estimator '{estimator}'. "
            f"Valid options: {list(DISTRIBUTION_REGISTRY.keys())}"
        )

    if estimator == "triangular":
        if min_duration is None or mode_duration is None or max_duration is None:
            raise ValueError(
                "Triangular distribution requires min_duration, mode_duration, "
                "and max_duration"
            )
        return TriangularDistribution(min_duration, mode_duration, max_duration)

    elif estimator == "uniform":
        if min_duration is None or max_duration is None:
            raise ValueError(
                "Uniform distribution requires min_duration and max_duration"
            )
        return UniformDistribution(min_duration, max_duration)

    elif estimator == "normal":
        if mean is None or std_dev is None:
            raise ValueError("Normal distribution requires mean and std_dev")
        return NormalDistribution(
            mean=mean,
            std_dev=std_dev,
            min_value=min_value if min_value is not None else 0.0,
            max_value=max_value,
        )

    elif estimator == "pert":
        if min_duration is None or mode_duration is None or max_duration is None:
            raise ValueError(
                "PERT distribution requires min_duration, mode_duration, "
                "and max_duration"
            )
        return PERTDistribution(
            min_value=min_duration,
            mode_value=mode_duration,
            max_value=max_duration,
            lamb=lamb if lamb is not None else 4.0,
        )

    elif estimator == "lognormal":
        if mean is None or std_dev is None:
            raise ValueError("LogNormal distribution requires mean and std_dev")
        return LogNormalDistribution(
            mean=mean,
            std_dev=std_dev,
            min_value=min_value if min_value is not None else 0.0,
            max_value=max_value,
        )

    elif estimator == "beta":
        if alpha is None or beta is None:
            raise ValueError("Beta distribution requires alpha and beta")
        if max_value is None:
            raise ValueError("Beta distribution requires max_value")
        return BetaDistribution(
            alpha=alpha,
            beta=beta,
            min_value=min_value if min_value is not None else 0.0,
            max_value=max_value,
        )

    # Should never reach here due to registry check
    raise ValueError(f"Unknown estimator: {estimator}")
