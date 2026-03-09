"""Image preprocessing utilities for dental panoramic X-ray analysis."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np


def load_image(path: str | Path) -> np.ndarray:
    """Load a dental panoramic image in grayscale.

    Returns the image as a 2-D numpy array (uint8).
    Raises FileNotFoundError when *path* does not exist.
    """
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Image not found: {path}")
    img = cv2.imread(str(path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to decode image: {path}")
    return img


def enhance_contrast(img: np.ndarray) -> np.ndarray:
    """Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)."""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(img)


def denoise(img: np.ndarray, strength: int = 10) -> np.ndarray:
    """Remove noise while preserving edges."""
    return cv2.fastNlMeansDenoising(img, h=strength)


def detect_edges(img: np.ndarray) -> np.ndarray:
    """Detect edges using Canny with auto-thresholding."""
    median_val = int(np.median(img))
    lower = max(0, int(median_val * 0.5))
    upper = min(255, int(median_val * 1.5))
    return cv2.Canny(img, lower, upper)


def split_upper_lower(img: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Split a panoramic image into upper jaw and lower jaw halves.

    Uses horizontal intensity projection to find the gap between the
    upper and lower teeth (the dark line between arches).
    """
    h, w = img.shape[:2]
    mid_band = img[h // 3 : 2 * h // 3, w // 4 : 3 * w // 4]
    row_means = np.mean(mid_band, axis=1)
    # The darkest row in the middle third is the inter-arch gap.
    gap_row = h // 3 + int(np.argmin(row_means))
    upper = img[:gap_row, :]
    lower = img[gap_row:, :]
    return upper, lower


def split_quadrants(img: np.ndarray) -> dict[str, np.ndarray]:
    """Split the panoramic image into four dental quadrants.

    Returns a dict with keys "upper_right", "upper_left",
    "lower_left", "lower_right" (from patient perspective).
    Note: in a panoramic X-ray the image is mirrored, so the
    patient's right appears on the left side of the image.
    """
    upper, lower = split_upper_lower(img)
    _, uw = upper.shape[:2]
    _, lw = lower.shape[:2]
    return {
        "upper_right": upper[:, : uw // 2],     # patient right = image left
        "upper_left": upper[:, uw // 2 :],      # patient left  = image right
        "lower_left": lower[:, lw // 2 :],
        "lower_right": lower[:, : lw // 2],
    }


def compute_region_stats(region: np.ndarray) -> dict:
    """Compute basic intensity statistics for a region.

    Returns dict with mean, std, min, max and histogram counts for
    dark / mid / bright intensity bands.
    """
    mean_val = float(np.mean(region))
    std_val = float(np.std(region))
    dark_ratio = float(np.sum(region < 80) / region.size)
    bright_ratio = float(np.sum(region > 180) / region.size)
    return {
        "mean": round(mean_val, 2),
        "std": round(std_val, 2),
        "min": int(np.min(region)),
        "max": int(np.max(region)),
        "dark_ratio": round(dark_ratio, 4),
        "bright_ratio": round(bright_ratio, 4),
    }
