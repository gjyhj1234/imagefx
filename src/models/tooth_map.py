"""FDI tooth numbering constants and helper utilities.

The FDI (Fédération Dentaire Internationale) system uses a two-digit
number where the first digit indicates the quadrant and the second
indicates the tooth position within the quadrant.

Quadrants (permanent):
  1 = upper right   2 = upper left
  4 = lower right   3 = lower left

Quadrants (primary / deciduous):
  5 = upper right   6 = upper left
  8 = lower right   7 = lower left
"""

from __future__ import annotations

# Permanent teeth: FDI number -> (English name, Chinese name)
PERMANENT_TEETH: dict[int, tuple[str, str]] = {
    # Upper right (quadrant 1)
    18: ("upper right third molar (wisdom tooth)", "右上第三磨牙（智齿）"),
    17: ("upper right second molar", "右上第二磨牙"),
    16: ("upper right first molar", "右上第一磨牙"),
    15: ("upper right second premolar", "右上第二前磨牙"),
    14: ("upper right first premolar", "右上第一前磨牙"),
    13: ("upper right canine", "右上尖牙"),
    12: ("upper right lateral incisor", "右上侧切牙"),
    11: ("upper right central incisor", "右上中切牙"),
    # Upper left (quadrant 2)
    21: ("upper left central incisor", "左上中切牙"),
    22: ("upper left lateral incisor", "左上侧切牙"),
    23: ("upper left canine", "左上尖牙"),
    24: ("upper left first premolar", "左上第一前磨牙"),
    25: ("upper left second premolar", "左上第二前磨牙"),
    26: ("upper left first molar", "左上第一磨牙"),
    27: ("upper left second molar", "左上第二磨牙"),
    28: ("upper left third molar (wisdom tooth)", "左上第三磨牙（智齿）"),
    # Lower left (quadrant 3)
    38: ("lower left third molar (wisdom tooth)", "左下第三磨牙（智齿）"),
    37: ("lower left second molar", "左下第二磨牙"),
    36: ("lower left first molar", "左下第一磨牙"),
    35: ("lower left second premolar", "左下第二前磨牙"),
    34: ("lower left first premolar", "左下第一前磨牙"),
    33: ("lower left canine", "左下尖牙"),
    32: ("lower left lateral incisor", "左下侧切牙"),
    31: ("lower left central incisor", "左下中切牙"),
    # Lower right (quadrant 4)
    41: ("lower right central incisor", "右下中切牙"),
    42: ("lower right lateral incisor", "右下侧切牙"),
    43: ("lower right canine", "右下尖牙"),
    44: ("lower right first premolar", "右下第一前磨牙"),
    45: ("lower right second premolar", "右下第二前磨牙"),
    46: ("lower right first molar", "右下第一磨牙"),
    47: ("lower right second molar", "右下第二磨牙"),
    48: ("lower right third molar (wisdom tooth)", "右下第三磨牙（智齿）"),
}

# Primary (deciduous) teeth: FDI number -> (English name, Chinese name)
PRIMARY_TEETH: dict[int, tuple[str, str]] = {
    # Upper right (quadrant 5)
    55: ("upper right second primary molar", "右上第二乳磨牙"),
    54: ("upper right first primary molar", "右上第一乳磨牙"),
    53: ("upper right primary canine", "右上乳尖牙"),
    52: ("upper right primary lateral incisor", "右上乳侧切牙"),
    51: ("upper right primary central incisor", "右上乳中切牙"),
    # Upper left (quadrant 6)
    61: ("upper left primary central incisor", "左上乳中切牙"),
    62: ("upper left primary lateral incisor", "左上乳侧切牙"),
    63: ("upper left primary canine", "左上乳尖牙"),
    64: ("upper left first primary molar", "左上第一乳磨牙"),
    65: ("upper left second primary molar", "左上第二乳磨牙"),
    # Lower left (quadrant 7)
    75: ("lower left second primary molar", "左下第二乳磨牙"),
    74: ("lower left first primary molar", "左下第一乳磨牙"),
    73: ("lower left primary canine", "左下乳尖牙"),
    72: ("lower left primary lateral incisor", "左下乳侧切牙"),
    71: ("lower left primary central incisor", "左下乳中切牙"),
    # Lower right (quadrant 8)
    81: ("lower right primary central incisor", "右下乳中切牙"),
    82: ("lower right primary lateral incisor", "右下乳侧切牙"),
    83: ("lower right primary canine", "右下乳尖牙"),
    84: ("lower right first primary molar", "右下第一乳磨牙"),
    85: ("lower right second primary molar", "右下第二乳磨牙"),
}

ALL_TEETH = {**PERMANENT_TEETH, **PRIMARY_TEETH}


def get_tooth_name(fdi_number: int) -> tuple[str, str]:
    """Return (English, Chinese) name for an FDI tooth number."""
    return ALL_TEETH.get(fdi_number, (f"tooth {fdi_number}", f"牙齿 {fdi_number}"))


def is_primary(fdi_number: int) -> bool:
    """Return True if the FDI number belongs to the primary dentition."""
    return fdi_number in PRIMARY_TEETH


def quadrant(fdi_number: int) -> int:
    """Return the quadrant digit (1-8) for a given FDI number."""
    return fdi_number // 10
