"""Data models for dental panoramic image analysis.

Uses the FDI (Fédération Dentaire Internationale) two-digit tooth
numbering system and standard periodontal examination terminology.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ToothStatus(str, enum.Enum):
    """Overall status of a single tooth."""
    NORMAL = "normal"
    CARIES = "caries"
    MISSING = "missing"
    IMPACTED = "impacted"
    UNERUPTED = "unerupted"
    RETAINED_PRIMARY = "retained_primary"
    ROOT_REMNANT = "root_remnant"
    RESTORED = "restored"
    CROWN = "crown"
    ECTOPIC = "ectopic"


class GumCondition(str, enum.Enum):
    """Gingival / gum condition around a tooth."""
    HEALTHY = "healthy"
    GINGIVITIS = "gingivitis"
    PERIODONTITIS_MILD = "periodontitis_mild"
    PERIODONTITIS_MODERATE = "periodontitis_moderate"
    PERIODONTITIS_SEVERE = "periodontitis_severe"
    RECESSION = "recession"


class BoneLossLevel(str, enum.Enum):
    """Alveolar bone loss severity."""
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class DentitionType(str, enum.Enum):
    """Type of dentition the tooth belongs to."""
    PRIMARY = "primary"
    PERMANENT = "permanent"
    MIXED = "mixed"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ToothFinding:
    """Clinical finding for a single tooth."""
    tooth_number: int                     # FDI number (11-48 permanent, 51-85 primary)
    tooth_name: str                       # e.g. "upper right central incisor"
    tooth_name_cn: str                    # Chinese name
    dentition_type: DentitionType         # primary / permanent
    status: list[ToothStatus] = field(default_factory=list)
    gum_condition: GumCondition = GumCondition.HEALTHY
    bone_loss: BoneLossLevel = BoneLossLevel.NONE
    probing_depth_mm: Optional[float] = None
    mobility: int = 0                     # 0-3
    notes: str = ""
    notes_cn: str = ""

    def has_issues(self) -> bool:
        """Return True if there are any abnormal findings."""
        return (
            any(s != ToothStatus.NORMAL for s in self.status)
            or self.gum_condition != GumCondition.HEALTHY
            or self.bone_loss != BoneLossLevel.NONE
            or self.mobility > 0
        )


@dataclass
class PeriodontalExam:
    """Standard periodontal examination result for the whole mouth."""
    patient_id: str
    exam_date: str
    dentition_stage: DentitionType
    teeth: list[ToothFinding] = field(default_factory=list)
    overall_notes: str = ""
    overall_notes_cn: str = ""

    @property
    def teeth_with_issues(self) -> list[ToothFinding]:
        return [t for t in self.teeth if t.has_issues()]


@dataclass
class OralScore:
    """Comprehensive oral health score and reasoning."""
    score: int                   # 0-100
    level: str                   # e.g. "fair", "good", "poor"
    level_cn: str                # Chinese level
    reasons: list[str]           # English reasons
    reasons_cn: list[str]        # Chinese reasons
    recommendations: list[str]
    recommendations_cn: list[str]
