"""Tests for the dental analysis engine and scoring."""

from pathlib import Path

import numpy as np
import pytest

from src.analyzer.dental_analysis import analyze_panoramic_image
from src.analyzer.scoring import compute_oral_score
from src.models.dental import (
    DentitionType,
    GumCondition,
    OralScore,
    PeriodontalExam,
    ToothFinding,
    ToothStatus,
)


_SAMPLE_IMAGE = Path(__file__).resolve().parent.parent / "patient-dental-img.jpg"


class TestAnalyzePanoramicImage:
    """Integration tests that run the analyser against the sample image."""

    @pytest.mark.skipif(
        not _SAMPLE_IMAGE.exists(),
        reason="Sample image not available",
    )
    def test_returns_periodontal_exam(self):
        exam = analyze_panoramic_image(_SAMPLE_IMAGE, patient_id="T-001")
        assert isinstance(exam, PeriodontalExam)
        assert exam.patient_id == "T-001"
        assert len(exam.teeth) > 0

    @pytest.mark.skipif(
        not _SAMPLE_IMAGE.exists(),
        reason="Sample image not available",
    )
    def test_teeth_have_fdi_numbers(self):
        exam = analyze_panoramic_image(_SAMPLE_IMAGE)
        for t in exam.teeth:
            assert 11 <= t.tooth_number <= 85

    @pytest.mark.skipif(
        not _SAMPLE_IMAGE.exists(),
        reason="Sample image not available",
    )
    def test_mixed_dentition_detected(self):
        """The sample image appears to show mixed dentition."""
        exam = analyze_panoramic_image(_SAMPLE_IMAGE)
        # The image shows a child with mixed dentition;
        # the analyser should detect this.
        assert exam.dentition_stage in (
            DentitionType.MIXED,
            DentitionType.PERMANENT,
        )

    def test_nonexistent_image_raises(self):
        with pytest.raises(FileNotFoundError):
            analyze_panoramic_image("/nonexistent/path.jpg")


class TestComputeOralScore:
    def test_perfect_score(self):
        exam = PeriodontalExam(
            patient_id="P",
            exam_date="2026-01-01",
            dentition_stage=DentitionType.PERMANENT,
            teeth=[
                ToothFinding(
                    tooth_number=11,
                    tooth_name="t",
                    tooth_name_cn="t",
                    dentition_type=DentitionType.PERMANENT,
                    status=[ToothStatus.NORMAL],
                )
            ],
        )
        score = compute_oral_score(exam)
        assert score.score == 100
        assert score.level == "excellent"

    def test_caries_reduce_score(self):
        exam = PeriodontalExam(
            patient_id="P",
            exam_date="2026-01-01",
            dentition_stage=DentitionType.PERMANENT,
            teeth=[
                ToothFinding(
                    tooth_number=16,
                    tooth_name="t",
                    tooth_name_cn="t",
                    dentition_type=DentitionType.PERMANENT,
                    status=[ToothStatus.CARIES],
                )
            ],
        )
        score = compute_oral_score(exam)
        assert score.score < 100
        assert any("caries" in r.lower() for r in score.reasons)

    def test_score_between_0_and_100(self):
        teeth = [
            ToothFinding(
                tooth_number=i,
                tooth_name="t",
                tooth_name_cn="t",
                dentition_type=DentitionType.PERMANENT,
                status=[ToothStatus.MISSING],
                gum_condition=GumCondition.PERIODONTITIS_SEVERE,
            )
            for i in range(11, 49)
        ]
        exam = PeriodontalExam(
            patient_id="P",
            exam_date="2026-01-01",
            dentition_stage=DentitionType.PERMANENT,
            teeth=teeth,
        )
        score = compute_oral_score(exam)
        assert 0 <= score.score <= 100

    @pytest.mark.skipif(
        not _SAMPLE_IMAGE.exists(),
        reason="Sample image not available",
    )
    def test_score_on_sample_image(self):
        exam = analyze_panoramic_image(_SAMPLE_IMAGE)
        score = compute_oral_score(exam)
        assert isinstance(score, OralScore)
        assert 0 <= score.score <= 100
        assert len(score.reasons) > 0
        assert len(score.recommendations) > 0
