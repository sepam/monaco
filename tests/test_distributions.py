"""Tests for distribution classes."""

import random

import pytest

from monaco.distributions import (
    DISTRIBUTION_REGISTRY,
    BetaDistribution,
    LogNormalDistribution,
    NormalDistribution,
    PERTDistribution,
    TriangularDistribution,
    UniformDistribution,
    create_distribution,
)


class TestDistributionRegistry:
    """Tests for the distribution registry."""

    def test_registry_contains_all_distributions(self):
        assert "triangular" in DISTRIBUTION_REGISTRY
        assert "uniform" in DISTRIBUTION_REGISTRY
        assert "normal" in DISTRIBUTION_REGISTRY
        assert "pert" in DISTRIBUTION_REGISTRY
        assert "lognormal" in DISTRIBUTION_REGISTRY
        assert "beta" in DISTRIBUTION_REGISTRY

    def test_registry_maps_to_correct_classes(self):
        assert DISTRIBUTION_REGISTRY["triangular"] == TriangularDistribution
        assert DISTRIBUTION_REGISTRY["uniform"] == UniformDistribution
        assert DISTRIBUTION_REGISTRY["normal"] == NormalDistribution
        assert DISTRIBUTION_REGISTRY["pert"] == PERTDistribution
        assert DISTRIBUTION_REGISTRY["lognormal"] == LogNormalDistribution
        assert DISTRIBUTION_REGISTRY["beta"] == BetaDistribution


class TestTriangularDistribution:
    """Tests for TriangularDistribution."""

    def test_valid_creation(self):
        dist = TriangularDistribution(1.0, 2.0, 3.0)
        assert dist.min_value == 1.0
        assert dist.mode_value == 2.0
        assert dist.max_value == 3.0
        assert dist.name == "triangular"

    def test_sample_in_range(self):
        random.seed(42)
        dist = TriangularDistribution(1.0, 2.0, 3.0)
        for _ in range(100):
            sample = dist.sample()
            assert 1.0 <= sample <= 3.0

    def test_invalid_ordering_mode_too_low(self):
        with pytest.raises(ValueError) as excinfo:
            TriangularDistribution(2.0, 1.0, 3.0)
        assert "min <= mode <= max" in str(excinfo.value)

    def test_invalid_ordering_mode_too_high(self):
        with pytest.raises(ValueError) as excinfo:
            TriangularDistribution(1.0, 4.0, 3.0)
        assert "min <= mode <= max" in str(excinfo.value)

    def test_negative_min_value(self):
        with pytest.raises(ValueError) as excinfo:
            TriangularDistribution(-1.0, 2.0, 3.0)
        assert "non-negative" in str(excinfo.value)

    def test_negative_mode_value(self):
        with pytest.raises(ValueError) as excinfo:
            TriangularDistribution(0.0, -1.0, 3.0)
        assert "non-negative" in str(excinfo.value)

    def test_negative_max_value(self):
        with pytest.raises(ValueError) as excinfo:
            TriangularDistribution(0.0, 1.0, -1.0)
        assert "non-negative" in str(excinfo.value)

    def test_display_params(self):
        dist = TriangularDistribution(1.0, 2.0, 3.0)
        assert dist.get_display_params() == "(1.0-2.0-3.0)"

    def test_to_dict(self):
        dist = TriangularDistribution(1.0, 2.0, 3.0)
        d = dist.to_dict()
        assert d["type"] == "triangular"
        assert d["min_duration"] == 1.0
        assert d["mode_duration"] == 2.0
        assert d["max_duration"] == 3.0

    def test_equal_values_allowed(self):
        # Edge case: all values equal (degenerate distribution)
        dist = TriangularDistribution(5.0, 5.0, 5.0)
        assert dist.sample() == 5.0


class TestUniformDistribution:
    """Tests for UniformDistribution."""

    def test_valid_creation(self):
        dist = UniformDistribution(1.0, 5.0)
        assert dist.min_value == 1.0
        assert dist.max_value == 5.0
        assert dist.name == "uniform"

    def test_sample_in_range(self):
        random.seed(42)
        dist = UniformDistribution(1.0, 5.0)
        for _ in range(100):
            sample = dist.sample()
            assert 1.0 <= sample <= 5.0

    def test_invalid_ordering(self):
        with pytest.raises(ValueError) as excinfo:
            UniformDistribution(5.0, 1.0)
        assert "min <= max" in str(excinfo.value)

    def test_negative_min_value(self):
        with pytest.raises(ValueError) as excinfo:
            UniformDistribution(-1.0, 5.0)
        assert "non-negative" in str(excinfo.value)

    def test_negative_max_value(self):
        with pytest.raises(ValueError) as excinfo:
            UniformDistribution(0.0, -1.0)
        assert "non-negative" in str(excinfo.value)

    def test_display_params(self):
        dist = UniformDistribution(1.0, 5.0)
        assert dist.get_display_params() == "(1.0-5.0)"

    def test_to_dict(self):
        dist = UniformDistribution(1.0, 5.0)
        d = dist.to_dict()
        assert d["type"] == "uniform"
        assert d["min_duration"] == 1.0
        assert d["max_duration"] == 5.0

    def test_equal_values_allowed(self):
        # Edge case: min equals max
        dist = UniformDistribution(5.0, 5.0)
        assert dist.sample() == 5.0


class TestNormalDistribution:
    """Tests for NormalDistribution."""

    def test_valid_creation(self):
        dist = NormalDistribution(mean=5.0, std_dev=1.0)
        assert dist.mean == 5.0
        assert dist.std_dev == 1.0
        assert dist.min_value == 0.0
        assert dist.max_value is None
        assert dist.name == "normal"

    def test_valid_creation_with_bounds(self):
        dist = NormalDistribution(mean=5.0, std_dev=1.0, min_value=2.0, max_value=8.0)
        assert dist.min_value == 2.0
        assert dist.max_value == 8.0

    def test_sample_non_negative(self):
        random.seed(42)
        dist = NormalDistribution(mean=5.0, std_dev=1.0)
        for _ in range(100):
            sample = dist.sample()
            assert sample >= 0.0

    def test_sample_with_bounds(self):
        random.seed(42)
        dist = NormalDistribution(mean=5.0, std_dev=1.0, min_value=3.0, max_value=7.0)
        for _ in range(100):
            sample = dist.sample()
            assert 3.0 <= sample <= 7.0

    def test_invalid_mean_zero(self):
        with pytest.raises(ValueError) as excinfo:
            NormalDistribution(mean=0.0, std_dev=1.0)
        assert "positive" in str(excinfo.value)

    def test_invalid_mean_negative(self):
        with pytest.raises(ValueError) as excinfo:
            NormalDistribution(mean=-1.0, std_dev=1.0)
        assert "positive" in str(excinfo.value)

    def test_invalid_std_dev_zero(self):
        with pytest.raises(ValueError) as excinfo:
            NormalDistribution(mean=5.0, std_dev=0.0)
        assert "positive" in str(excinfo.value)

    def test_invalid_std_dev_negative(self):
        with pytest.raises(ValueError) as excinfo:
            NormalDistribution(mean=5.0, std_dev=-1.0)
        assert "positive" in str(excinfo.value)

    def test_invalid_min_value_negative(self):
        with pytest.raises(ValueError) as excinfo:
            NormalDistribution(mean=5.0, std_dev=1.0, min_value=-1.0)
        assert "non-negative" in str(excinfo.value)

    def test_invalid_max_less_than_min(self):
        with pytest.raises(ValueError) as excinfo:
            NormalDistribution(mean=5.0, std_dev=1.0, min_value=5.0, max_value=3.0)
        assert "max_value must be >= min_value" in str(excinfo.value)

    def test_display_params_no_bounds(self):
        dist = NormalDistribution(mean=5.0, std_dev=1.0)
        params = dist.get_display_params()
        assert "mean=5.0" in params
        assert "std=1.0" in params
        assert "[" not in params  # No bounds shown

    def test_display_params_with_bounds(self):
        dist = NormalDistribution(mean=5.0, std_dev=1.0, min_value=2.0, max_value=8.0)
        params = dist.get_display_params()
        assert "mean=5.0" in params
        assert "std=1.0" in params
        assert "[2.0-8.0]" in params

    def test_to_dict_minimal(self):
        dist = NormalDistribution(mean=5.0, std_dev=1.0)
        d = dist.to_dict()
        assert d["type"] == "normal"
        assert d["mean"] == 5.0
        assert d["std_dev"] == 1.0
        assert "min_value" not in d  # Default not serialized
        assert "max_value" not in d

    def test_to_dict_with_bounds(self):
        dist = NormalDistribution(mean=5.0, std_dev=1.0, min_value=2.0, max_value=8.0)
        d = dist.to_dict()
        assert d["min_value"] == 2.0
        assert d["max_value"] == 8.0


class TestCreateDistribution:
    """Tests for the create_distribution factory function."""

    def test_create_triangular(self):
        dist = create_distribution(
            estimator="triangular",
            min_duration=1.0,
            mode_duration=2.0,
            max_duration=3.0,
        )
        assert isinstance(dist, TriangularDistribution)
        assert dist.min_value == 1.0
        assert dist.mode_value == 2.0
        assert dist.max_value == 3.0

    def test_create_uniform(self):
        dist = create_distribution(
            estimator="uniform",
            min_duration=1.0,
            max_duration=3.0,
        )
        assert isinstance(dist, UniformDistribution)
        assert dist.min_value == 1.0
        assert dist.max_value == 3.0

    def test_create_normal(self):
        dist = create_distribution(
            estimator="normal",
            mean=5.0,
            std_dev=1.0,
        )
        assert isinstance(dist, NormalDistribution)
        assert dist.mean == 5.0
        assert dist.std_dev == 1.0

    def test_create_normal_with_bounds(self):
        dist = create_distribution(
            estimator="normal",
            mean=5.0,
            std_dev=1.0,
            min_value=2.0,
            max_value=8.0,
        )
        assert dist.min_value == 2.0
        assert dist.max_value == 8.0

    def test_unknown_estimator(self):
        with pytest.raises(ValueError) as excinfo:
            create_distribution(estimator="unknown")
        assert "Unknown estimator" in str(excinfo.value)
        assert "unknown" in str(excinfo.value)

    def test_missing_triangular_params(self):
        with pytest.raises(ValueError) as excinfo:
            create_distribution(estimator="triangular", min_duration=1.0)
        assert "requires" in str(excinfo.value)

    def test_missing_uniform_params(self):
        with pytest.raises(ValueError) as excinfo:
            create_distribution(estimator="uniform", min_duration=1.0)
        assert "requires" in str(excinfo.value)

    def test_missing_normal_mean(self):
        with pytest.raises(ValueError) as excinfo:
            create_distribution(estimator="normal", std_dev=1.0)
        assert "requires" in str(excinfo.value)

    def test_missing_normal_std_dev(self):
        with pytest.raises(ValueError) as excinfo:
            create_distribution(estimator="normal", mean=5.0)
        assert "requires" in str(excinfo.value)


class TestDistributionStatisticalProperties:
    """Statistical tests to verify distribution behavior."""

    def test_triangular_mean_approximation(self):
        """Verify triangular samples cluster around expected mean."""
        random.seed(42)
        dist = TriangularDistribution(0.0, 5.0, 10.0)
        samples = [dist.sample() for _ in range(10000)]
        mean_sample = sum(samples) / len(samples)
        # For triangular, mean = (min + mode + max) / 3 = 5.0
        assert 4.8 <= mean_sample <= 5.2

    def test_uniform_mean_is_midpoint(self):
        """Verify uniform samples have mean at midpoint."""
        random.seed(42)
        dist = UniformDistribution(0.0, 10.0)
        samples = [dist.sample() for _ in range(10000)]
        mean_sample = sum(samples) / len(samples)
        assert 4.8 <= mean_sample <= 5.2

    def test_normal_mean_matches(self):
        """Verify normal samples have expected mean."""
        random.seed(42)
        dist = NormalDistribution(mean=10.0, std_dev=1.0)
        samples = [dist.sample() for _ in range(10000)]
        mean_sample = sum(samples) / len(samples)
        # Should be close to 10.0 (slight bias possible due to truncation at 0)
        assert 9.8 <= mean_sample <= 10.2

    def test_normal_std_dev_approximation(self):
        """Verify normal samples have expected standard deviation."""
        random.seed(42)
        dist = NormalDistribution(mean=10.0, std_dev=2.0)
        samples = [dist.sample() for _ in range(10000)]
        mean_sample = sum(samples) / len(samples)
        variance = sum((s - mean_sample) ** 2 for s in samples) / len(samples)
        std_sample = variance**0.5
        # Should be close to 2.0
        assert 1.8 <= std_sample <= 2.2

    def test_pert_mean_approximation(self):
        """Verify PERT samples cluster around expected mean."""
        random.seed(42)
        dist = PERTDistribution(0.0, 5.0, 10.0)
        samples = [dist.sample() for _ in range(10000)]
        mean_sample = sum(samples) / len(samples)
        # For PERT, mean = (min + 4*mode + max) / 6 = (0 + 20 + 10) / 6 = 5.0
        assert 4.8 <= mean_sample <= 5.2

    def test_lognormal_mean_approximation(self):
        """Verify lognormal samples have expected mean."""
        random.seed(42)
        dist = LogNormalDistribution(mean=5.0, std_dev=1.0)
        samples = [dist.sample() for _ in range(10000)]
        mean_sample = sum(samples) / len(samples)
        assert 4.8 <= mean_sample <= 5.2

    def test_beta_mean_approximation(self):
        """Verify beta samples cluster around expected mean."""
        random.seed(42)
        dist = BetaDistribution(alpha=2.0, beta=2.0, min_value=0.0, max_value=10.0)
        samples = [dist.sample() for _ in range(10000)]
        mean_sample = sum(samples) / len(samples)
        # For symmetric beta(2,2) on [0,10], mean = 5.0
        assert 4.8 <= mean_sample <= 5.2


class TestPERTDistribution:
    """Tests for PERTDistribution."""

    def test_valid_creation(self):
        dist = PERTDistribution(1.0, 2.0, 3.0)
        assert dist.min_value == 1.0
        assert dist.mode_value == 2.0
        assert dist.max_value == 3.0
        assert dist.lamb == 4.0
        assert dist.name == "pert"

    def test_valid_creation_with_lamb(self):
        dist = PERTDistribution(1.0, 2.0, 3.0, lamb=6.0)
        assert dist.lamb == 6.0

    def test_sample_in_range(self):
        random.seed(42)
        dist = PERTDistribution(1.0, 2.0, 3.0)
        for _ in range(100):
            sample = dist.sample()
            assert 1.0 <= sample <= 3.0

    def test_invalid_ordering(self):
        with pytest.raises(ValueError) as excinfo:
            PERTDistribution(3.0, 2.0, 1.0)
        assert "min <= mode <= max" in str(excinfo.value)

    def test_negative_values(self):
        with pytest.raises(ValueError) as excinfo:
            PERTDistribution(-1.0, 2.0, 3.0)
        assert "non-negative" in str(excinfo.value)

    def test_invalid_lamb(self):
        with pytest.raises(ValueError) as excinfo:
            PERTDistribution(1.0, 2.0, 3.0, lamb=0.0)
        assert "positive" in str(excinfo.value)

    def test_display_params(self):
        dist = PERTDistribution(1.0, 2.0, 3.0)
        assert dist.get_display_params() == "(1.0-2.0-3.0)"

    def test_to_dict(self):
        dist = PERTDistribution(1.0, 2.0, 3.0)
        d = dist.to_dict()
        assert d["type"] == "pert"
        assert d["min_duration"] == 1.0
        assert d["mode_duration"] == 2.0
        assert d["max_duration"] == 3.0
        assert "lamb" not in d  # Default not serialized

    def test_to_dict_with_lamb(self):
        dist = PERTDistribution(1.0, 2.0, 3.0, lamb=6.0)
        d = dist.to_dict()
        assert d["lamb"] == 6.0

    def test_equal_values_allowed(self):
        dist = PERTDistribution(5.0, 5.0, 5.0)
        assert dist.sample() == 5.0


class TestLogNormalDistribution:
    """Tests for LogNormalDistribution."""

    def test_valid_creation(self):
        dist = LogNormalDistribution(mean=5.0, std_dev=1.0)
        assert dist.mean == 5.0
        assert dist.std_dev == 1.0
        assert dist.min_value == 0.0
        assert dist.max_value is None
        assert dist.name == "lognormal"

    def test_valid_creation_with_bounds(self):
        dist = LogNormalDistribution(
            mean=5.0, std_dev=1.0, min_value=2.0, max_value=10.0
        )
        assert dist.min_value == 2.0
        assert dist.max_value == 10.0

    def test_sample_positive(self):
        random.seed(42)
        dist = LogNormalDistribution(mean=5.0, std_dev=1.0)
        for _ in range(100):
            sample = dist.sample()
            assert sample > 0

    def test_sample_with_bounds(self):
        random.seed(42)
        dist = LogNormalDistribution(
            mean=5.0, std_dev=1.0, min_value=3.0, max_value=8.0
        )
        for _ in range(100):
            sample = dist.sample()
            assert 3.0 <= sample <= 8.0

    def test_invalid_mean(self):
        with pytest.raises(ValueError) as excinfo:
            LogNormalDistribution(mean=0.0, std_dev=1.0)
        assert "positive" in str(excinfo.value)

    def test_invalid_std_dev(self):
        with pytest.raises(ValueError) as excinfo:
            LogNormalDistribution(mean=5.0, std_dev=0.0)
        assert "positive" in str(excinfo.value)

    def test_invalid_min_value(self):
        with pytest.raises(ValueError) as excinfo:
            LogNormalDistribution(mean=5.0, std_dev=1.0, min_value=-1.0)
        assert "non-negative" in str(excinfo.value)

    def test_invalid_max_less_than_min(self):
        with pytest.raises(ValueError) as excinfo:
            LogNormalDistribution(mean=5.0, std_dev=1.0, min_value=5.0, max_value=3.0)
        assert "max_value must be >= min_value" in str(excinfo.value)

    def test_display_params_no_bounds(self):
        dist = LogNormalDistribution(mean=5.0, std_dev=1.0)
        params = dist.get_display_params()
        assert "mean=5.0" in params
        assert "std=1.0" in params

    def test_display_params_with_bounds(self):
        dist = LogNormalDistribution(
            mean=5.0, std_dev=1.0, min_value=2.0, max_value=8.0
        )
        params = dist.get_display_params()
        assert "[2.0-8.0]" in params

    def test_to_dict_minimal(self):
        dist = LogNormalDistribution(mean=5.0, std_dev=1.0)
        d = dist.to_dict()
        assert d["type"] == "lognormal"
        assert d["mean"] == 5.0
        assert d["std_dev"] == 1.0
        assert "min_value" not in d

    def test_to_dict_with_bounds(self):
        dist = LogNormalDistribution(
            mean=5.0, std_dev=1.0, min_value=2.0, max_value=8.0
        )
        d = dist.to_dict()
        assert d["min_value"] == 2.0
        assert d["max_value"] == 8.0


class TestBetaDistribution:
    """Tests for BetaDistribution."""

    def test_valid_creation(self):
        dist = BetaDistribution(alpha=2.0, beta=3.0, min_value=0.0, max_value=10.0)
        assert dist.alpha == 2.0
        assert dist.beta == 3.0
        assert dist.min_value == 0.0
        assert dist.max_value == 10.0
        assert dist.name == "beta"

    def test_sample_in_range(self):
        random.seed(42)
        dist = BetaDistribution(alpha=2.0, beta=3.0, min_value=0.0, max_value=10.0)
        for _ in range(100):
            sample = dist.sample()
            assert 0.0 <= sample <= 10.0

    def test_symmetric_distribution(self):
        """Test that beta(2,2) is symmetric around midpoint."""
        random.seed(42)
        dist = BetaDistribution(alpha=2.0, beta=2.0, min_value=0.0, max_value=10.0)
        samples = [dist.sample() for _ in range(10000)]
        mean_sample = sum(samples) / len(samples)
        # Should be centered around 5.0
        assert 4.8 <= mean_sample <= 5.2

    def test_right_skewed(self):
        """Test that beta(2,5) is right-skewed (mean below midpoint)."""
        random.seed(42)
        dist = BetaDistribution(alpha=2.0, beta=5.0, min_value=0.0, max_value=10.0)
        samples = [dist.sample() for _ in range(10000)]
        mean_sample = sum(samples) / len(samples)
        # Mean should be below midpoint: 10 * 2/(2+5) = 2.86
        assert mean_sample < 5.0

    def test_left_skewed(self):
        """Test that beta(5,2) is left-skewed (mean above midpoint)."""
        random.seed(42)
        dist = BetaDistribution(alpha=5.0, beta=2.0, min_value=0.0, max_value=10.0)
        samples = [dist.sample() for _ in range(10000)]
        mean_sample = sum(samples) / len(samples)
        # Mean should be above midpoint: 10 * 5/(5+2) = 7.14
        assert mean_sample > 5.0

    def test_invalid_alpha(self):
        with pytest.raises(ValueError) as excinfo:
            BetaDistribution(alpha=0.0, beta=2.0, max_value=10.0)
        assert "positive" in str(excinfo.value)

    def test_invalid_beta(self):
        with pytest.raises(ValueError) as excinfo:
            BetaDistribution(alpha=2.0, beta=0.0, max_value=10.0)
        assert "positive" in str(excinfo.value)

    def test_invalid_min_value(self):
        with pytest.raises(ValueError) as excinfo:
            BetaDistribution(alpha=2.0, beta=2.0, min_value=-1.0, max_value=10.0)
        assert "non-negative" in str(excinfo.value)

    def test_invalid_max_less_than_min(self):
        with pytest.raises(ValueError) as excinfo:
            BetaDistribution(alpha=2.0, beta=2.0, min_value=10.0, max_value=5.0)
        assert "max_value must be > min_value" in str(excinfo.value)

    def test_display_params(self):
        dist = BetaDistribution(alpha=2.0, beta=3.0, min_value=0.0, max_value=10.0)
        params = dist.get_display_params()
        assert "α=2.0" in params
        assert "β=3.0" in params
        assert "[0.0-10.0]" in params

    def test_to_dict(self):
        dist = BetaDistribution(alpha=2.0, beta=3.0, min_value=0.0, max_value=10.0)
        d = dist.to_dict()
        assert d["type"] == "beta"
        assert d["alpha"] == 2.0
        assert d["beta"] == 3.0
        assert d["min_value"] == 0.0
        assert d["max_value"] == 10.0


class TestCreateDistributionNewTypes:
    """Tests for create_distribution with new distribution types."""

    def test_create_pert(self):
        dist = create_distribution(
            estimator="pert",
            min_duration=1.0,
            mode_duration=2.0,
            max_duration=3.0,
        )
        assert isinstance(dist, PERTDistribution)
        assert dist.min_value == 1.0
        assert dist.mode_value == 2.0
        assert dist.max_value == 3.0

    def test_create_pert_with_lamb(self):
        dist = create_distribution(
            estimator="pert",
            min_duration=1.0,
            mode_duration=2.0,
            max_duration=3.0,
            lamb=6.0,
        )
        assert dist.lamb == 6.0

    def test_create_lognormal(self):
        dist = create_distribution(
            estimator="lognormal",
            mean=5.0,
            std_dev=1.0,
        )
        assert isinstance(dist, LogNormalDistribution)
        assert dist.mean == 5.0
        assert dist.std_dev == 1.0

    def test_create_lognormal_with_bounds(self):
        dist = create_distribution(
            estimator="lognormal",
            mean=5.0,
            std_dev=1.0,
            min_value=2.0,
            max_value=10.0,
        )
        assert dist.min_value == 2.0
        assert dist.max_value == 10.0

    def test_create_beta(self):
        dist = create_distribution(
            estimator="beta",
            alpha=2.0,
            beta=3.0,
            max_value=10.0,
        )
        assert isinstance(dist, BetaDistribution)
        assert dist.alpha == 2.0
        assert dist.beta == 3.0
        assert dist.max_value == 10.0

    def test_create_beta_with_min_value(self):
        dist = create_distribution(
            estimator="beta",
            alpha=2.0,
            beta=3.0,
            min_value=1.0,
            max_value=10.0,
        )
        assert dist.min_value == 1.0

    def test_missing_pert_params(self):
        with pytest.raises(ValueError) as excinfo:
            create_distribution(estimator="pert", min_duration=1.0)
        assert "requires" in str(excinfo.value)

    def test_missing_lognormal_params(self):
        with pytest.raises(ValueError) as excinfo:
            create_distribution(estimator="lognormal", mean=5.0)
        assert "requires" in str(excinfo.value)

    def test_missing_beta_alpha(self):
        with pytest.raises(ValueError) as excinfo:
            create_distribution(estimator="beta", beta=2.0, max_value=10.0)
        assert "requires" in str(excinfo.value)

    def test_missing_beta_max_value(self):
        with pytest.raises(ValueError) as excinfo:
            create_distribution(estimator="beta", alpha=2.0, beta=2.0)
        assert "requires" in str(excinfo.value)


class TestDistributionRoundTrip:
    """Tests that to_dict() -> create_distribution() produces equivalent distributions.

    This verifies the serialization/deserialization round-trip that underpins
    YAML config save and load.
    """

    def test_triangular_round_trip(self):
        original = TriangularDistribution(2.0, 5.0, 12.0)
        d = original.to_dict()
        restored = create_distribution(estimator=d.pop("type"), **d)
        assert isinstance(restored, TriangularDistribution)
        assert restored.min_value == original.min_value
        assert restored.mode_value == original.mode_value
        assert restored.max_value == original.max_value

    def test_uniform_round_trip(self):
        original = UniformDistribution(3.0, 9.0)
        d = original.to_dict()
        restored = create_distribution(estimator=d.pop("type"), **d)
        assert isinstance(restored, UniformDistribution)
        assert restored.min_value == original.min_value
        assert restored.max_value == original.max_value

    def test_normal_round_trip_minimal(self):
        """Normal distribution with default bounds (no min_value/max_value in dict)."""
        original = NormalDistribution(mean=7.0, std_dev=2.0)
        d = original.to_dict()
        restored = create_distribution(estimator=d.pop("type"), **d)
        assert isinstance(restored, NormalDistribution)
        assert restored.mean == original.mean
        assert restored.std_dev == original.std_dev
        assert restored.min_value == 0.0
        assert restored.max_value is None

    def test_normal_round_trip_with_bounds(self):
        """Normal distribution with explicit bounds survives round-trip."""
        original = NormalDistribution(mean=7.0, std_dev=2.0, min_value=3.0, max_value=11.0)
        d = original.to_dict()
        restored = create_distribution(estimator=d.pop("type"), **d)
        assert isinstance(restored, NormalDistribution)
        assert restored.mean == original.mean
        assert restored.std_dev == original.std_dev
        assert restored.min_value == original.min_value
        assert restored.max_value == original.max_value

    def test_pert_round_trip_default_lamb(self):
        """PERT with default lamb=4 (not serialized) round-trips correctly."""
        original = PERTDistribution(1.0, 4.0, 10.0)
        d = original.to_dict()
        assert "lamb" not in d  # default is omitted
        restored = create_distribution(estimator=d.pop("type"), **d)
        assert isinstance(restored, PERTDistribution)
        assert restored.min_value == original.min_value
        assert restored.mode_value == original.mode_value
        assert restored.max_value == original.max_value
        assert restored.lamb == 4.0

    def test_pert_round_trip_custom_lamb(self):
        """PERT with non-default lamb survives round-trip."""
        original = PERTDistribution(1.0, 4.0, 10.0, lamb=6.0)
        d = original.to_dict()
        assert d["lamb"] == 6.0
        restored = create_distribution(estimator=d.pop("type"), **d)
        assert isinstance(restored, PERTDistribution)
        assert restored.min_value == original.min_value
        assert restored.mode_value == original.mode_value
        assert restored.max_value == original.max_value
        assert restored.lamb == 6.0

    def test_lognormal_round_trip_minimal(self):
        """LogNormal with default bounds round-trips correctly."""
        original = LogNormalDistribution(mean=8.0, std_dev=3.0)
        d = original.to_dict()
        restored = create_distribution(estimator=d.pop("type"), **d)
        assert isinstance(restored, LogNormalDistribution)
        assert restored.mean == original.mean
        assert restored.std_dev == original.std_dev
        assert restored.min_value == 0.0
        assert restored.max_value is None

    def test_lognormal_round_trip_with_bounds(self):
        """LogNormal with explicit bounds survives round-trip."""
        original = LogNormalDistribution(mean=8.0, std_dev=3.0, min_value=2.0, max_value=20.0)
        d = original.to_dict()
        restored = create_distribution(estimator=d.pop("type"), **d)
        assert isinstance(restored, LogNormalDistribution)
        assert restored.mean == original.mean
        assert restored.std_dev == original.std_dev
        assert restored.min_value == original.min_value
        assert restored.max_value == original.max_value

    def test_beta_round_trip(self):
        original = BetaDistribution(alpha=2.0, beta=5.0, min_value=1.0, max_value=15.0)
        d = original.to_dict()
        restored = create_distribution(estimator=d.pop("type"), **d)
        assert isinstance(restored, BetaDistribution)
        assert restored.alpha == original.alpha
        assert restored.beta == original.beta
        assert restored.min_value == original.min_value
        assert restored.max_value == original.max_value

    def test_round_trip_samples_match(self):
        """Verify that a round-tripped distribution produces the same samples."""
        original = TriangularDistribution(1.0, 5.0, 10.0)
        d = original.to_dict()
        restored = create_distribution(estimator=d.pop("type"), **d)

        random.seed(99)
        original_samples = [original.sample() for _ in range(50)]
        random.seed(99)
        restored_samples = [restored.sample() for _ in range(50)]

        assert original_samples == restored_samples
