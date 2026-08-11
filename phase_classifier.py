"""月相羅針 classification module for technical PoC v0.1.

IMPORTANT:
The eight definitions below are NOT the official 月相羅針 specification.
They are temporary technical test definitions that simply divide 360 degrees
into eight equal 45-degree sectors.

When the official ID/name/range/boundary/description/characteristics/guidance
are approved, replace the definitions in this module rather than changing the
astronomical calculation module or the whole Web application.
"""

from __future__ import annotations

from typing import TypedDict


class PhaseDefinition(TypedDict):
    id: str
    name: str
    start: float
    end: float
    description: str
    characteristics: str
    guidance: str


# PoC-only provisional definitions: start angle INCLUDED, end angle EXCLUDED.
PHASES: list[PhaseDefinition] = [
    {
        "id": "P01",
        "name": "仮分類1",
        "start": 0.0,
        "end": 45.0,
        "description": "PoC用の仮定義です。正式説明文ではありません。",
        "characteristics": "PoC用未定義",
        "guidance": "PoC用未定義",
    },
    {
        "id": "P02",
        "name": "仮分類2",
        "start": 45.0,
        "end": 90.0,
        "description": "PoC用の仮定義です。正式説明文ではありません。",
        "characteristics": "PoC用未定義",
        "guidance": "PoC用未定義",
    },
    {
        "id": "P03",
        "name": "仮分類3",
        "start": 90.0,
        "end": 135.0,
        "description": "PoC用の仮定義です。正式説明文ではありません。",
        "characteristics": "PoC用未定義",
        "guidance": "PoC用未定義",
    },
    {
        "id": "P04",
        "name": "仮分類4",
        "start": 135.0,
        "end": 180.0,
        "description": "PoC用の仮定義です。正式説明文ではありません。",
        "characteristics": "PoC用未定義",
        "guidance": "PoC用未定義",
    },
    {
        "id": "P05",
        "name": "仮分類5",
        "start": 180.0,
        "end": 225.0,
        "description": "PoC用の仮定義です。正式説明文ではありません。",
        "characteristics": "PoC用未定義",
        "guidance": "PoC用未定義",
    },
    {
        "id": "P06",
        "name": "仮分類6",
        "start": 225.0,
        "end": 270.0,
        "description": "PoC用の仮定義です。正式説明文ではありません。",
        "characteristics": "PoC用未定義",
        "guidance": "PoC用未定義",
    },
    {
        "id": "P07",
        "name": "仮分類7",
        "start": 270.0,
        "end": 315.0,
        "description": "PoC用の仮定義です。正式説明文ではありません。",
        "characteristics": "PoC用未定義",
        "guidance": "PoC用未定義",
    },
    {
        "id": "P08",
        "name": "仮分類8",
        "start": 315.0,
        "end": 360.0,
        "description": "PoC用の仮定義です。正式説明文ではありません。",
        "characteristics": "PoC用未定義",
        "guidance": "PoC用未定義",
    },
]


def normalize_angle(angle: float) -> float:
    """Normalize an angle so 360.0 becomes 0.0, etc."""
    return float(angle) % 360.0


def classify_phase(angle_difference: float) -> dict[str, object]:
    """Classify an angle with the provisional PoC eight-sector definition."""
    angle = normalize_angle(angle_difference)

    for phase in PHASES:
        if phase["start"] <= angle < phase["end"]:
            return {
                **phase,
                "normalized_angle": angle,
                "range_text": f'{phase["start"]:.0f}°以上 ～ {phase["end"]:.0f}°未満',
                "is_provisional": True,
            }

    # Because angle is normalized to [0, 360), this should never be reached.
    raise ValueError("仮8分類を判定できませんでした。")
