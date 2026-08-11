"""Core tests for 月相羅針 計算PoC v0.1."""

from __future__ import annotations

import os
import sys
import unittest

# Allow tests to import modules from the project root.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from astronomy import calculate_birth_astronomy
from phase_classifier import classify_phase


class TestAstronomy(unittest.TestCase):
    def test_reference_birth_data(self) -> None:
        result = calculate_birth_astronomy(
            birth_date="1964-09-03",
            birth_time="11:23",
            timezone_name="Asia/Tokyo",
        )

        self.assertEqual(
            result["utc_datetime"].strftime("%Y-%m-%d %H:%M:%S UTC"),
            "1964-09-03 02:23:00 UTC",
        )

        # The instruction gives approximate expected values.  A tolerance of
        # 0.0001 degree (= 0.36 arcsec) is used to avoid brittle float tests.
        tolerance = 0.0001
        self.assertAlmostEqual(
            float(result["sun_longitude"]), 160.60945188, delta=tolerance
        )
        self.assertAlmostEqual(
            float(result["moon_longitude"]), 119.86709682, delta=tolerance
        )
        self.assertAlmostEqual(
            float(result["angle_difference"]), 319.25764494, delta=tolerance
        )

        phase = classify_phase(float(result["angle_difference"]))
        self.assertEqual(phase["id"], "P08")
        self.assertEqual(phase["name"], "仮分類8")


class TestProvisionalPhaseBoundaries(unittest.TestCase):
    def test_boundaries(self) -> None:
        cases = [
            (0.0, "P01"),
            (44.9999, "P01"),
            (45.0, "P02"),
            (314.9999, "P07"),
            (315.0, "P08"),
            (359.9999, "P08"),
            (360.0, "P01"),
        ]
        for angle, expected_id in cases:
            with self.subTest(angle=angle):
                self.assertEqual(classify_phase(angle)["id"], expected_id)


if __name__ == "__main__":
    unittest.main()
