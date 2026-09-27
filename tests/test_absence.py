import unittest

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

    def test_invalid_coverage_fails_closed(self):
        with self.assertRaises(ValueError):
            classify_window(window="S01", expected=1, observed=0, coverage=1.5)


if __name__ == "__main__":
    unittest.main()
