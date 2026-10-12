import unittest

from tocaia.evaluation import evaluate


def row(key="F1", p=0.8, baseline=0.5, outcome=1):
    return dict(forecast_id=key, probability=p, baseline_probability=baseline, outcome=outcome)


class EvaluationTests(unittest.TestCase):
    def test_known_scores_and_abstention(self):
        result = evaluate([row(), row("F2", 0.2, outcome=0), row("F3", outcome=None)])
        self.assertAlmostEqual(result["brier"], 0.04)
        self.assertAlmostEqual(result["baseline_brier"], 0.25)
        self.assertAlmostEqual(result["brier_skill"], 0.84)
        self.assertEqual(result["resolved"], 2)
        self.assertEqual(result["unresolved"], 1)
        self.assertEqual(result["positive_outcomes"], 1)

    def test_all_unresolved_does_not_imply_success(self):
        result = evaluate([row(outcome=None)])
        self.assertIsNone(result["brier"])
        self.assertIsNone(result["brier_skill"])
        self.assertEqual(result["unresolved_rate"], 1)

    def test_perfect_baseline_has_undefined_skill(self):
        self.assertIsNone(evaluate([row(baseline=1)])["brier_skill"])

    def test_worse_than_baseline_has_negative_skill(self):
        self.assertLess(evaluate([row(p=0, baseline=0.8)])["brier_skill"], 0)

    def test_invalid_probabilities_including_unresolved_are_rejected(self):
        for invalid in (True, "0.5", float("nan"), float("inf"), -0.1, 1.1):
            for field in ("probability", "baseline_probability"):
                with self.subTest(value=invalid, field=field):
                    value = row(outcome=None)
                    value[field] = invalid
                    with self.assertRaises(ValueError):
                        evaluate([value])

    def test_invalid_outcomes_are_rejected(self):
        for invalid in (True, "1", 1.0, 2, -1):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                evaluate([row(outcome=invalid)])

    def test_duplicate_and_missing_fields_are_rejected(self):
        for invalid in ([row(), row()], [{}], [], {}, [row(key=" ")], [None]):
            with self.subTest(value=invalid), self.assertRaises(ValueError):
                evaluate(invalid)
