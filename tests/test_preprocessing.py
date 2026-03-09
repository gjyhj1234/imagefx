"""Tests for image preprocessing utilities."""

import numpy as np
import pytest

from src.analyzer.image_preprocessing import (
    compute_region_stats,
    detect_edges,
    enhance_contrast,
    split_upper_lower,
    split_quadrants,
)


@pytest.fixture
def synthetic_panoramic():
    """Create a synthetic panoramic-like grayscale image.

    Upper half is brighter (teeth), lower half darker, with a dark
    band in the middle simulating the inter-arch gap.
    """
    h, w = 400, 800
    img = np.zeros((h, w), dtype=np.uint8)
    # Upper teeth region (bright)
    img[20:170, 50:750] = 160
    # Dark gap between arches
    img[170:220, :] = 20
    # Lower teeth region (bright)
    img[220:380, 50:750] = 150
    return img


class TestEnhanceContrast:
    def test_output_shape(self, synthetic_panoramic):
        result = enhance_contrast(synthetic_panoramic)
        assert result.shape == synthetic_panoramic.shape
        assert result.dtype == np.uint8


class TestDetectEdges:
    def test_output_shape(self, synthetic_panoramic):
        result = detect_edges(synthetic_panoramic)
        assert result.shape == synthetic_panoramic.shape


class TestSplitUpperLower:
    def test_split(self, synthetic_panoramic):
        upper, lower = split_upper_lower(synthetic_panoramic)
        assert upper.shape[1] == synthetic_panoramic.shape[1]
        assert lower.shape[1] == synthetic_panoramic.shape[1]
        assert upper.shape[0] + lower.shape[0] == synthetic_panoramic.shape[0]


class TestSplitQuadrants:
    def test_four_quadrants(self, synthetic_panoramic):
        quads = split_quadrants(synthetic_panoramic)
        assert set(quads.keys()) == {
            "upper_right", "upper_left", "lower_left", "lower_right"
        }
        for name, q in quads.items():
            assert q.ndim == 2
            assert q.shape[0] > 0
            assert q.shape[1] > 0


class TestComputeRegionStats:
    def test_keys(self):
        region = np.full((100, 100), 128, dtype=np.uint8)
        stats = compute_region_stats(region)
        assert "mean" in stats
        assert "std" in stats
        assert "dark_ratio" in stats
        assert "bright_ratio" in stats

    def test_dark_region(self):
        region = np.full((100, 100), 30, dtype=np.uint8)
        stats = compute_region_stats(region)
        assert stats["dark_ratio"] > 0.9

    def test_bright_region(self):
        region = np.full((100, 100), 220, dtype=np.uint8)
        stats = compute_region_stats(region)
        assert stats["bright_ratio"] > 0.9
