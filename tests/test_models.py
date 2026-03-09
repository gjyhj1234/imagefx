"""Tests for dental data models."""

import pytest

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
    quadrant,
)


class TestToothMap:
    def test_permanent_teeth_count(self):
        assert len(PERMANENT_TEETH) == 32

    def test_primary_teeth_count(self):
        assert len(PRIMARY_TEETH) == 20

    def test_get_tooth_name_permanent(self):
        en, cn = get_tooth_name(11)
        assert "central incisor" in en
        assert "中切牙" in cn

    def test_get_tooth_name_primary(self):
        en, cn = get_tooth_name(51)
        assert "primary" in en
        assert "乳" in cn

    def test_get_tooth_name_unknown(self):
        en, cn = get_tooth_name(99)
        assert "99" in en
        assert "99" in cn

    def test_is_primary(self):
        assert is_primary(51) is True
        assert is_primary(11) is False

    def test_quadrant(self):
        assert quadrant(11) == 1
        assert quadrant(28) == 2
        assert quadrant(38) == 3
        assert quadrant(48) == 4
        assert quadrant(55) == 5


class TestToothFinding:
    def test_normal_tooth_no_issues(self):
        finding = ToothFinding(
            tooth_number=11,
            tooth_name="upper right central incisor",
            tooth_name_cn="右上中切牙",
            dentition_type=DentitionType.PERMANENT,
            status=[ToothStatus.NORMAL],
        )
        assert finding.has_issues() is False

    def test_caries_has_issues(self):
        finding = ToothFinding(
            tooth_number=16,
            tooth_name="upper right first molar",
            tooth_name_cn="右上第一磨牙",
            dentition_type=DentitionType.PERMANENT,
            status=[ToothStatus.CARIES],
        )
        assert finding.has_issues() is True

    def test_bone_loss_has_issues(self):
        finding = ToothFinding(
            tooth_number=36,
            tooth_name="lower left first molar",
            tooth_name_cn="左下第一磨牙",
            dentition_type=DentitionType.PERMANENT,
            status=[ToothStatus.NORMAL],
            bone_loss=BoneLossLevel.MODERATE,
        )
        assert finding.has_issues() is True

    def test_mobility_has_issues(self):
        finding = ToothFinding(
            tooth_number=31,
            tooth_name="lower left central incisor",
            tooth_name_cn="左下中切牙",
            dentition_type=DentitionType.PERMANENT,
            status=[ToothStatus.NORMAL],
            mobility=2,
        )
        assert finding.has_issues() is True


class TestPeriodontalExam:
    def test_teeth_with_issues(self):
        normal = ToothFinding(
            tooth_number=11,
            tooth_name="t1",
            tooth_name_cn="t1cn",
            dentition_type=DentitionType.PERMANENT,
            status=[ToothStatus.NORMAL],
        )
        abnormal = ToothFinding(
            tooth_number=16,
            tooth_name="t2",
            tooth_name_cn="t2cn",
            dentition_type=DentitionType.PERMANENT,
            status=[ToothStatus.CARIES],
        )
        exam = PeriodontalExam(
            patient_id="P-TEST",
            exam_date="2026-01-01",
            dentition_stage=DentitionType.PERMANENT,
            teeth=[normal, abnormal],
        )
        assert len(exam.teeth_with_issues) == 1
        assert exam.teeth_with_issues[0].tooth_number == 16


class TestOralScore:
    def test_score_creation(self):
        score = OralScore(
            score=72,
            level="good",
            level_cn="良好",
            reasons=["2 teeth with caries"],
            reasons_cn=["2颗牙齿龋坏"],
            recommendations=["Visit dentist"],
            recommendations_cn=["建议就诊"],
        )
        assert score.score == 72
        assert score.level == "good"
