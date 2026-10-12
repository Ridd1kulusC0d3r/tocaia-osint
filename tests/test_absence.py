import unittest

from math import inf, nan

from tocaia.absence import GapKind, classify_window


class AbsenceTests(unittest.TestCase):
    def test_incomplete_collection_is_data_gap(self):
        record = classify_window(window="S06", expected=34, observed=0, coverage=0.30)
        self.assertEqual(record.kind, GapKind.DATA_GAP)

    def test_zero_with_adequate_coverage_is_behavioral_gap(self):
        record = classify_window(window="S13", expected=34, observed=0, coverage=1.0)
        self.assertEqual(record.kind, GapKind.BEHAVIORAL_GAP)
        self.assertEqual(record.delta, 34)

    def test_activity_is_not_forced_into_gap(self):
        record = classify_window(window="S12", expected=34, observed=31, coverage=1.0)
        self.assertEqual(record.kind, GapKind.NO_GAP)

    def test_serialization_and_string_enum_are_backward_compatible(self):
        record = classify_window(window="S13", expected=34, observed=0, coverage=1.0)
        self.assertIsInstance(record.kind, str)
        self.assertEqual(record.to_dict()["kind"], "behavioral_gap")

    def test_zero_baseline_does_not_imply_absence(self):
        record = classify_window(window="S13", expected=0, observed=0, coverage=1.0)
        self.assertEqual(record.kind, GapKind.NO_GAP)

    def test_non_finite_numbers_fail_closed(self):
        for invalid in (nan, inf, -inf):
            with self.subTest(field="expected", value=invalid):
                with self.assertRaises(ValueError):
                    classify_window(window="S01", expected=invalid, observed=0, coverage=1.0)
            with self.subTest(field="coverage", value=invalid):
                with self.assertRaises(ValueError):
                    classify_window(window="S01", expected=1, observed=0, coverage=invalid)
            with self.subTest(field="min_coverage", value=invalid):
                with self.assertRaises(ValueError):
                    classify_window(window="S01", expected=1, observed=0, coverage=1.0, min_coverage=invalid)

    def test_invalid_coverage_fails_closed(self):
        with self.assertRaises(ValueError):
            classify_window(window="S01", expected=1, observed=0, coverage=1.5)


if __name__ == "__main__":
    unittest.main()
