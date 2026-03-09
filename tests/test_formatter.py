"""Tests for output formatters."""

import json

import pytest

from src.models.dental import (
    DentitionType,
    GumCondition,
    OralScore,
    PeriodontalExam,
    ToothFinding,
    ToothStatus,
)
from src.output.formatter import (
    exam_to_json,
    generate_patient_report,
    generate_score_summary,
)


@pytest.fixture
def sample_exam():
    return PeriodontalExam(
        patient_id="P-TEST",
        exam_date="2026-01-01",
        dentition_stage=DentitionType.MIXED,
        teeth=[
            ToothFinding(
                tooth_number=11,
                tooth_name="upper right central incisor",
                tooth_name_cn="右上中切牙",
                dentition_type=DentitionType.PERMANENT,
                status=[ToothStatus.NORMAL],
            ),
            ToothFinding(
                tooth_number=16,
                tooth_name="upper right first molar",
                tooth_name_cn="右上第一磨牙",
                dentition_type=DentitionType.PERMANENT,
                status=[ToothStatus.CARIES],
                gum_condition=GumCondition.PERIODONTITIS_MILD,
                notes="Suspected carious lesion.",
                notes_cn="疑似龋坏。",
            ),
        ],
    )


@pytest.fixture
def sample_score():
    return OralScore(
        score=72,
        level="good",
        level_cn="良好",
        reasons=["1 tooth with caries."],
        reasons_cn=["1颗牙齿龋坏。"],
        recommendations=["Visit dentist."],
        recommendations_cn=["建议就诊。"],
    )


class TestExamToJson:
    def test_valid_json(self, sample_exam, sample_score):
        result = exam_to_json(sample_exam, sample_score)
        data = json.loads(result)
        assert data["patient_id"] == "P-TEST"
        assert isinstance(data["teeth"], list)
        assert isinstance(data["oral_score"], dict)

    def test_teeth_with_issues_in_json(self, sample_exam, sample_score):
        result = exam_to_json(sample_exam, sample_score)
        data = json.loads(result)
        assert len(data["teeth_with_issues"]) == 1
        assert data["teeth_with_issues"][0]["tooth_number"] == 16


class TestGeneratePatientReport:
    def test_contains_patient_id(self, sample_exam, sample_score):
        report = generate_patient_report(sample_exam, sample_score)
        assert "P-TEST" in report

    def test_contains_chinese_text(self, sample_exam, sample_score):
        report = generate_patient_report(sample_exam, sample_score)
        assert "口腔全景片分析报告" in report
        assert "评分原因" in report

    def test_contains_tooth_details(self, sample_exam, sample_score):
        report = generate_patient_report(sample_exam, sample_score)
        assert "16" in report
        assert "caries" in report


class TestGenerateScoreSummary:
    def test_contains_score(self, sample_score):
        summary = generate_score_summary(sample_score)
        assert "72" in summary
        assert "良好" in summary

    def test_contains_recommendations(self, sample_score):
        summary = generate_score_summary(sample_score)
        assert "建议" in summary
