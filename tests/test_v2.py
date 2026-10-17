import json
import random
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from tocaia import bench, journal, watch
from tocaia.absence import GapKind
from tocaia.detect import Window, count_cdf, detect


def series(counts, cov=1.0):
    return [Window(f"W{i}", c, cov if isinstance(cov, float) else cov[i]) for i, c in enumerate(counts)]


class DetectTests(unittest.TestCase):
    def test_cdf_matches_poisson_zero(self):
        self.assertAlmostEqual(count_cdf(0, 3.0), 2.718281828 ** -3, places=6)

    def test_silence_after_stable_baseline_is_behavioral_gap(self):
        r = detect(series([12, 10, 13, 11, 12, 11, 0, 0]))
        self.assertEqual([d.kind for d in r[-2:]], [GapKind.BEHAVIORAL_GAP] * 2)
        self.assertEqual(r[-1].silent_run, 2)

    def test_low_coverage_zero_is_data_gap(self):
        r = detect(series([12, 10, 13, 11, 12, 0], cov=[1.0] * 5 + [0.2]))
        self.assertEqual(r[-1].kind, GapKind.DATA_GAP)

    def test_low_volume_source_is_undetectable_not_silent(self):
        r = detect(series([1, 0, 1, 0, 1, 0, 0]))
        self.assertEqual(r[-1].kind, GapKind.UNDETECTABLE)

    def test_baseline_is_frozen_during_gaps(self):
        r = detect(series([12, 10, 13, 11, 12, 11] + [0] * 6))
        self.assertTrue(all(d.kind == GapKind.BEHAVIORAL_GAP for d in r[6:]))

    def test_deficit(self):
        r = detect(series([40, 42, 38, 41, 40, 39, 8]))
        self.assertEqual(r[-1].kind, GapKind.DEFICIT)

    def test_no_baseline_fails_closed(self):
        self.assertEqual(detect(series([0, 0]))[-1].kind, GapKind.UNDETECTABLE)


class JournalTests(unittest.TestCase):
    def test_chain_and_tamper_detection(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "j.jsonl"
            for i in range(3):
                journal.append(p, "probe", {"n": i}, ts=f"2026-01-0{i + 1}T00:00:00+00:00")
            self.assertTrue(journal.verify(p)[0])
            lines = p.read_text().splitlines()
            rec = json.loads(lines[1])
            rec["payload"] = {"n": 99}
            lines[1] = json.dumps(rec, sort_keys=True)
            p.write_text("\n".join(lines) + "\n")
            ok, n, msg = journal.verify(p)
            self.assertFalse(ok)
            self.assertEqual(n, 1)


FEED = b"""<rss><channel>%s</channel></rss>"""


def item(i):
    return f"<item><title>t{i}</title><link>http://x/{i}</link><guid>g{i}</guid></item>".encode()


class WatchTests(unittest.TestCase):
    def test_pipeline_separates_collector_failure_from_source_silence(self):
        state = {"items": 3, "fail": False}

        def fetcher(url):
            if state["fail"]:
                raise OSError("down")
            return FEED % b"".join(item(i) for i in range(state["items"]))

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "j.jsonl"
            base = datetime(2026, 3, 2, tzinfo=timezone.utc)  # a Monday: weeks align with windows
            # 10 weekly windows, 1 probe each; the source adds 10 items/week for 7 weeks, goes quiet, then the collector fails
            for week in range(10):
                state["fail"] = week == 9
                if week < 7:
                    state["items"] += 10
                watch.poll(["http://x/feed"], p, fetcher=fetcher, ts=(base + timedelta(weeks=week)).isoformat())
            rep = watch.report(p, window_days=7, probes_per_window=1, min_history=3)
            kinds = [d.kind for d in rep["http://x/feed"]]
            self.assertIn(GapKind.BEHAVIORAL_GAP, kinds[:-1])
            self.assertEqual(kinds[-1], GapKind.DATA_GAP)
            self.assertTrue(journal.verify(p)[0])


class BenchTests(unittest.TestCase):
    def test_deterministic(self):
        self.assertEqual(bench.run(series=20, seed=3), bench.run(series=20, seed=3))

    def test_v2_never_mistakes_outage_for_behavior_more_than_naive(self):
        r = bench.run(series=60, seed=5)
        self.assertLess(r["tocaia_v0.2"]["false_certainty"], r["naive_zero"]["false_certainty"])
        self.assertGreater(r["tocaia_v0.2"]["recall"], 0.5)


if __name__ == "__main__":
    unittest.main()
