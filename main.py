#!/usr/bin/env python3
"""Dental panoramic X-ray analysis – command-line entry point.

Usage
-----
    python main.py [image_path] [--patient-id ID] [--output-dir DIR]

If *image_path* is omitted the bundled sample image is used.

Outputs
-------
Three files are written to *output_dir* (default ``./output``):

1. ``analysis_result.json``  – structured JSON
2. ``patient_report.txt``    – patient-friendly report (CN + EN)
3. ``score_summary.txt``     – oral health score + reasons
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.analyzer.dental_analysis import analyze_panoramic_image
from src.analyzer.scoring import compute_oral_score
from src.output.formatter import (
    exam_to_json,
    generate_patient_report,
    generate_score_summary,
)

_DEFAULT_IMAGE = Path(__file__).resolve().parent / "patient-dental-img.jpg"
_DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "output"


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Analyze a dental panoramic X-ray image."
    )
    parser.add_argument(
        "image",
        nargs="?",
        default=str(_DEFAULT_IMAGE),
        help="Path to the panoramic image (default: bundled sample)",
    )
    parser.add_argument(
        "--patient-id",
        default="P-001",
        help="Patient identifier (default: P-001)",
    )
    parser.add_argument(
        "--output-dir",
        default=str(_DEFAULT_OUTPUT_DIR),
        help="Directory for output files (default: ./output)",
    )
    args = parser.parse_args(argv)

    image_path = Path(args.image)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Analyzing image: {image_path}")
    exam = analyze_panoramic_image(
        image_path=image_path,
        patient_id=args.patient_id,
    )
    score = compute_oral_score(exam)

    # 1. JSON
    json_str = exam_to_json(exam, score)
    json_path = output_dir / "analysis_result.json"
    json_path.write_text(json_str, encoding="utf-8")
    print(f"  ✓ JSON result    → {json_path}")

    # 2. Patient report
    report = generate_patient_report(exam, score)
    report_path = output_dir / "patient_report.txt"
    report_path.write_text(report, encoding="utf-8")
    print(f"  ✓ Patient report → {report_path}")

    # 3. Score summary
    summary = generate_score_summary(score)
    summary_path = output_dir / "score_summary.txt"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"  ✓ Score summary  → {summary_path}")

    # Also print the report to stdout
    print()
    print(report)


if __name__ == "__main__":
    main()
