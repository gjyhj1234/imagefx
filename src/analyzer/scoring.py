"""Oral health scoring based on periodontal exam findings."""

from __future__ import annotations

from src.models.dental import (
    BoneLossLevel,
    GumCondition,
    OralScore,
    PeriodontalExam,
    ToothStatus,
)


_SCORE_LEVELS = [
    (90, "excellent", "优秀"),
    (75, "good", "良好"),
    (60, "fair", "一般"),
    (40, "poor", "较差"),
    (0,  "very poor", "很差"),
]


def compute_oral_score(exam: PeriodontalExam) -> OralScore:
    """Compute a 0-100 oral health score from examination findings.

    Scoring rules
    -------------
    * Start at 100.
    * Deduct per tooth with issues:
      - caries: −3
      - missing: −4
      - impacted: −3
      - bone loss mild: −2, moderate: −4, severe: −6
      - periodontitis mild: −2, moderate: −4, severe: −6
      - retained primary (mixed dentition): −1
      - unerupted: −0 (normal in mixed dentition)
      - restored: −1 (treatment present but not fully intact)
    * Mixed-dentition bonus: +5 (normal developmental stage)
    * Floor at 0.
    """
    score = 100
    reasons_en: list[str] = []
    reasons_cn: list[str] = []
    recs_en: list[str] = []
    recs_cn: list[str] = []

    caries_count = 0
    missing_count = 0
    impacted_count = 0
    bone_loss_count = 0
    perio_count = 0
    retained_count = 0
    restored_count = 0

    for tooth in exam.teeth:
        for s in tooth.status:
            if s == ToothStatus.CARIES:
                score -= 3
                caries_count += 1
            elif s == ToothStatus.MISSING:
                score -= 4
                missing_count += 1
            elif s == ToothStatus.IMPACTED:
                score -= 3
                impacted_count += 1
            elif s == ToothStatus.RETAINED_PRIMARY:
                score -= 1
                retained_count += 1
            elif s == ToothStatus.RESTORED:
                score -= 1
                restored_count += 1

        # Bone loss and periodontal disease are related; count the
        # worse of the two to avoid double-penalising the same tooth.
        perio_penalty = 0
        if tooth.bone_loss == BoneLossLevel.MILD:
            perio_penalty = max(perio_penalty, 2)
            bone_loss_count += 1
        elif tooth.bone_loss == BoneLossLevel.MODERATE:
            perio_penalty = max(perio_penalty, 3)
            bone_loss_count += 1
        elif tooth.bone_loss == BoneLossLevel.SEVERE:
            perio_penalty = max(perio_penalty, 5)
            bone_loss_count += 1

        if tooth.gum_condition == GumCondition.PERIODONTITIS_MILD:
            perio_penalty = max(perio_penalty, 2)
            perio_count += 1
        elif tooth.gum_condition == GumCondition.PERIODONTITIS_MODERATE:
            perio_penalty = max(perio_penalty, 3)
            perio_count += 1
        elif tooth.gum_condition == GumCondition.PERIODONTITIS_SEVERE:
            perio_penalty = max(perio_penalty, 5)
            perio_count += 1

        score -= perio_penalty

    from src.models.dental import DentitionType
    if exam.dentition_stage == DentitionType.MIXED:
        score += 5
        reasons_en.append(
            "Patient is in the mixed-dentition stage (normal developmental phase)."
        )
        reasons_cn.append("患者处于替牙期（正常发育阶段）。")

    if caries_count:
        reasons_en.append(f"{caries_count} tooth/teeth with suspected caries.")
        reasons_cn.append(f"{caries_count}颗牙齿疑似龋坏。")
        recs_en.append("Visit a dentist for caries evaluation and possible restoration.")
        recs_cn.append("建议就诊牙科医生进行龋坏评估和可能的修复治疗。")

    if missing_count:
        reasons_en.append(f"{missing_count} missing tooth/teeth.")
        reasons_cn.append(f"{missing_count}颗牙齿缺失。")
        recs_en.append("Consult about prosthetic options (implant, bridge, or denture).")
        recs_cn.append("建议咨询修复方案（种植牙、牙桥或义齿）。")

    if impacted_count:
        reasons_en.append(f"{impacted_count} impacted tooth/teeth.")
        reasons_cn.append(f"{impacted_count}颗牙齿阻生。")
        recs_en.append("Surgical evaluation recommended for impacted teeth.")
        recs_cn.append("建议对阻生牙进行外科评估。")

    if bone_loss_count:
        reasons_en.append(
            f"Alveolar bone loss detected around {bone_loss_count} tooth/teeth."
        )
        reasons_cn.append(f"{bone_loss_count}颗牙齿周围检测到牙槽骨吸收。")
        recs_en.append("Periodontal treatment and regular follow-up recommended.")
        recs_cn.append("建议进行牙周治疗并定期复查。")

    if perio_count:
        reasons_en.append(f"Periodontal disease signs around {perio_count} tooth/teeth.")
        reasons_cn.append(f"{perio_count}颗牙齿周围有牙周病迹象。")
        recs_en.append("Professional dental cleaning and periodontal therapy advised.")
        recs_cn.append("建议进行专业洁牙和牙周治疗。")

    if retained_count:
        reasons_en.append(f"{retained_count} retained primary tooth/teeth.")
        reasons_cn.append(f"{retained_count}颗乳牙滞留。")
        recs_en.append("Monitor eruption of permanent successors; extraction may be needed.")
        recs_cn.append("监测继承恒牙的萌出情况，可能需要拔除乳牙。")

    if restored_count:
        reasons_en.append(f"{restored_count} tooth/teeth with existing restorations.")
        reasons_cn.append(f"{restored_count}颗牙齿有既有修复体。")
        recs_en.append("Regular check-ups to monitor restoration integrity.")
        recs_cn.append("定期复查以监测修复体完整性。")

    if not reasons_en:
        reasons_en.append("No significant dental issues detected.")
        reasons_cn.append("未检测到明显的口腔问题。")
        recs_en.append("Maintain regular dental check-ups every 6 months.")
        recs_cn.append("建议每6个月进行一次常规口腔检查。")

    score = max(0, min(100, score))
    level_en, level_cn = "", ""
    for threshold, lbl_en, lbl_cn in _SCORE_LEVELS:
        if score >= threshold:
            level_en = lbl_en
            level_cn = lbl_cn
            break

    return OralScore(
        score=score,
        level=level_en,
        level_cn=level_cn,
        reasons=reasons_en,
        reasons_cn=reasons_cn,
        recommendations=recs_en,
        recommendations_cn=recs_cn,
    )
