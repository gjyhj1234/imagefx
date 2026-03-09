"""Core dental panoramic X-ray analysis engine.

This module examines a panoramic dental X-ray image using classical
image-processing heuristics (intensity analysis, edge density, region
statistics) to produce a :class:`PeriodontalExam` describing every
tooth that can be assessed from the radiograph.

**Important** – the analysis is heuristic-based and is intended as a
demonstrative prototype.  Clinical decision-making should always
involve a qualified dental professional.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import cv2
import numpy as np

from src.analyzer.image_preprocessing import (
    compute_region_stats,
    detect_edges,
    enhance_contrast,
    load_image,
    split_quadrants,
    split_upper_lower,
)
from src.models.dental import (
    BoneLossLevel,
    DentitionType,
    GumCondition,
    OralScore,
    PeriodontalExam,
    ToothFinding,
    ToothStatus,
)
from src.models.tooth_map import (
    PERMANENT_TEETH,
    PRIMARY_TEETH,
    get_tooth_name,
    is_primary,
)


# ---------------------------------------------------------------------------
# Quadrant ↔ FDI mapping
# ---------------------------------------------------------------------------
_QUADRANT_PERMANENT = {
    "upper_right": [18, 17, 16, 15, 14, 13, 12, 11],
    "upper_left":  [21, 22, 23, 24, 25, 26, 27, 28],
    "lower_left":  [38, 37, 36, 35, 34, 33, 32, 31],
    "lower_right": [41, 42, 43, 44, 45, 46, 47, 48],
}

_QUADRANT_PRIMARY = {
    "upper_right": [55, 54, 53, 52, 51],
    "upper_left":  [61, 62, 63, 64, 65],
    "lower_left":  [75, 74, 73, 72, 71],
    "lower_right": [81, 82, 83, 84, 85],
}


# ---------------------------------------------------------------------------
# Helper – extract a tooth-sized horizontal strip from a quadrant image
# ---------------------------------------------------------------------------

def _tooth_strip(quadrant_img: np.ndarray, index: int, total: int) -> np.ndarray:
    """Return the vertical strip for tooth *index* (0-based) out of *total*."""
    h, w = quadrant_img.shape[:2]
    strip_w = w // total
    x_start = index * strip_w
    x_end = min(x_start + strip_w, w)
    return quadrant_img[:, x_start:x_end]


# ---------------------------------------------------------------------------
# Per-tooth heuristic analysis
# ---------------------------------------------------------------------------

def _analyze_tooth_strip(
    strip: np.ndarray,
    fdi: int,
    is_mixed_dentition: bool,
) -> ToothFinding:
    """Analyze the image strip corresponding to one tooth position.

    Heuristics used
    ---------------
    * **Dark-ratio** – unusually high dark-pixel percentage may indicate
      caries or missing tooth.
    * **Bright-ratio** – unusually bright regions may indicate restorations
      or crowns (metallic density).
    * **Edge density** – low edge density in a strip suggests the tooth
      may be missing; very high density might indicate fracture lines.
    * **Upper-vs-lower intensity** – comparing the coronal half to the
      apical half can indicate bone loss.
    """
    en_name, cn_name = get_tooth_name(fdi)
    dtype = DentitionType.PRIMARY if is_primary(fdi) else DentitionType.PERMANENT
    stats = compute_region_stats(strip)
    edges = detect_edges(strip)
    edge_density = float(np.sum(edges > 0) / edges.size)

    statuses: list[ToothStatus] = []
    gum = GumCondition.HEALTHY
    bone = BoneLossLevel.NONE
    mobility = 0
    probing: Optional[float] = None
    notes_parts: list[str] = []
    notes_cn_parts: list[str] = []

    # --- Missing / unerupted ---
    if stats["dark_ratio"] > 0.80 and edge_density < 0.03:
        if is_mixed_dentition and dtype == DentitionType.PERMANENT:
            statuses.append(ToothStatus.UNERUPTED)
            notes_parts.append("Permanent tooth has not yet erupted.")
            notes_cn_parts.append("恒牙尚未萌出。")
        else:
            statuses.append(ToothStatus.MISSING)
            notes_parts.append("Tooth appears to be missing.")
            notes_cn_parts.append("该牙齿缺失。")
    # --- Restoration / crown ---
    elif stats["bright_ratio"] > 0.30:
        statuses.append(ToothStatus.RESTORED)
        notes_parts.append("High-density restoration or crown detected.")
        notes_cn_parts.append("检测到高密度修复体或牙冠。")
    # --- Caries suspicion ---
    elif stats["dark_ratio"] > 0.55 and stats["std"] > 45:
        statuses.append(ToothStatus.CARIES)
        notes_parts.append("Suspected carious lesion (dark area with irregular density).")
        notes_cn_parts.append("疑似龋坏病变（不规则低密度区域）。")
    # --- Impacted ---
    elif edge_density > 0.18 and stats["mean"] > 140:
        statuses.append(ToothStatus.IMPACTED)
        notes_parts.append("Tooth appears impacted or ectopically positioned.")
        notes_cn_parts.append("牙齿疑似阻生或异位。")

    # --- Bone loss (compare coronal vs apical halves) ---
    # In mixed dentition, developing tooth buds below erupted teeth
    # create naturally high contrast, so we raise thresholds.
    h = strip.shape[0]
    coronal = strip[: h // 2, :]
    apical = strip[h // 2 :, :]
    coronal_mean = float(np.mean(coronal))
    apical_mean = float(np.mean(apical))
    bone_diff = coronal_mean - apical_mean

    # Higher thresholds for mixed dentition to avoid false positives
    if is_mixed_dentition:
        t_severe, t_moderate, t_mild = 70, 55, 40
    else:
        t_severe, t_moderate, t_mild = 40, 25, 15

    if bone_diff > t_severe:
        bone = BoneLossLevel.SEVERE
        gum = GumCondition.PERIODONTITIS_SEVERE
        probing = 7.0
        mobility = 2
        notes_parts.append("Significant alveolar bone loss detected.")
        notes_cn_parts.append("检测到明显牙槽骨吸收。")
    elif bone_diff > t_moderate:
        bone = BoneLossLevel.MODERATE
        gum = GumCondition.PERIODONTITIS_MODERATE
        probing = 5.0
        mobility = 1
        notes_parts.append("Moderate alveolar bone loss detected.")
        notes_cn_parts.append("检测到中度牙槽骨吸收。")
    elif bone_diff > t_mild:
        bone = BoneLossLevel.MILD
        gum = GumCondition.PERIODONTITIS_MILD
        probing = 4.0
        notes_parts.append("Mild alveolar bone loss detected.")
        notes_cn_parts.append("检测到轻度牙槽骨吸收。")

    # Retained primary tooth heuristic (for mixed dentition)
    if is_mixed_dentition and dtype == DentitionType.PRIMARY:
        if stats["mean"] > 100 and edge_density > 0.06:
            statuses.append(ToothStatus.RETAINED_PRIMARY)
            notes_parts.append("Primary tooth is retained (successor may be developing).")
            notes_cn_parts.append("乳牙滞留（继承恒牙可能正在发育中）。")

    if not statuses:
        statuses.append(ToothStatus.NORMAL)

    return ToothFinding(
        tooth_number=fdi,
        tooth_name=en_name,
        tooth_name_cn=cn_name,
        dentition_type=dtype,
        status=statuses,
        gum_condition=gum,
        bone_loss=bone,
        probing_depth_mm=probing,
        mobility=mobility,
        notes=" ".join(notes_parts),
        notes_cn="".join(notes_cn_parts),
    )


# ---------------------------------------------------------------------------
# Mixed-dentition detection
# ---------------------------------------------------------------------------

def _detect_mixed_dentition(img: np.ndarray) -> bool:
    """Heuristic to decide whether the patient has mixed dentition.

    Mixed dentition is common in children aged 6-12.  The panoramic
    image typically shows developing permanent tooth germs below
    (lower jaw) or above (upper jaw) the erupted primary teeth.

    We look at the apical third of each jaw half for high-contrast
    rounded structures (tooth buds).
    """
    upper, lower = split_upper_lower(img)

    # Check apical region of lower jaw (bottom third) for tooth germs
    lh, _ = lower.shape[:2]
    apical_lower = lower[2 * lh // 3 :, :]
    enhanced = enhance_contrast(apical_lower)
    edges = detect_edges(enhanced)
    edge_density = float(np.sum(edges > 0) / edges.size)

    # Also check the upper jaw apical region
    uh, _ = upper.shape[:2]
    apical_upper = upper[: uh // 3, :]
    enhanced_u = enhance_contrast(apical_upper)
    edges_u = detect_edges(enhanced_u)
    edge_density_u = float(np.sum(edges_u > 0) / edges_u.size)

    avg_edge = (edge_density + edge_density_u) / 2
    # High edge density in apical regions suggests developing tooth buds
    return avg_edge > 0.06


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_panoramic_image(
    image_path: str | Path,
    patient_id: str = "UNKNOWN",
    exam_date: str = "",
) -> PeriodontalExam:
    """Analyze a dental panoramic X-ray and return a PeriodontalExam.

    Parameters
    ----------
    image_path:
        Path to the panoramic radiograph (JPEG / PNG).
    patient_id:
        Optional patient identifier.
    exam_date:
        ISO-format date string; defaults to today.

    Returns
    -------
    PeriodontalExam
        Structured findings for every assessable tooth.
    """
    import datetime

    if not exam_date:
        exam_date = datetime.date.today().isoformat()

    img = load_image(image_path)
    img = enhance_contrast(img)

    is_mixed = _detect_mixed_dentition(img)
    dentition_stage = DentitionType.MIXED if is_mixed else DentitionType.PERMANENT

    quadrants = split_quadrants(img)

    findings: list[ToothFinding] = []

    for quad_name, quad_img in quadrants.items():
        permanent_fdis = _QUADRANT_PERMANENT[quad_name]
        for idx, fdi in enumerate(permanent_fdis):
            strip = _tooth_strip(quad_img, idx, len(permanent_fdis))
            finding = _analyze_tooth_strip(strip, fdi, is_mixed)
            findings.append(finding)

        if is_mixed:
            primary_fdis = _QUADRANT_PRIMARY[quad_name]
            for idx, fdi in enumerate(primary_fdis):
                strip = _tooth_strip(quad_img, idx, len(primary_fdis))
                finding = _analyze_tooth_strip(strip, fdi, is_mixed)
                findings.append(finding)

    findings.sort(key=lambda f: f.tooth_number)

    overall_en = (
        "Panoramic radiograph analysis complete. "
        "Mixed dentition observed – patient appears to be in the transitional "
        "dentition phase." if is_mixed else
        "Panoramic radiograph analysis complete."
    )
    overall_cn = (
        "全景片分析完成。观察到混合牙列——患者处于替牙期。"
        if is_mixed else "全景片分析完成。"
    )

    return PeriodontalExam(
        patient_id=patient_id,
        exam_date=exam_date,
        dentition_stage=dentition_stage,
        teeth=findings,
        overall_notes=overall_en,
        overall_notes_cn=overall_cn,
    )
