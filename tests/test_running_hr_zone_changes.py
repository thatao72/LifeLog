import datetime as dt
import io
import unittest

from running_hr_zone_changes import (
    ZoneSnapshot,
    changed_snapshots,
    extract_thresholds,
    is_running_activity,
    write_csv,
)


class ExtractThresholdsTest(unittest.TestCase):
    def test_extracts_list_payload(self):
        payload = [
            {"zoneNumber": 1, "zoneLowBoundary": 100, "secsInZone": 20},
            {"zoneNumber": 2, "zoneLowBoundary": 120, "secsInZone": 30},
            {"zoneNumber": 3, "zoneLowBoundary": 140, "secsInZone": 40},
            {"zoneNumber": 4, "zoneLowBoundary": 160, "secsInZone": 50},
            {"zoneNumber": 5, "zoneLowBoundary": 180, "secsInZone": 60},
        ]
        self.assertEqual(extract_thresholds(payload), (100, 120, 140, 160, 180))

    def test_accepts_wrapped_payload_and_key_variants(self):
        payload = {
            "zones": [
                {"zone": 1, "lowerBoundary": 98},
                {"zone": 2, "lowerBoundary": 118},
                {"zone": 3, "lowerBoundary": 138},
                {"zone": 4, "lowerBoundary": 158},
                {"zone": 5, "lowerBoundary": 178},
            ]
        }
        self.assertEqual(extract_thresholds(payload), (98, 118, 138, 158, 178))

    def test_rejects_incomplete_payload(self):
        with self.assertRaises(ValueError):
            extract_thresholds([{"zoneNumber": 1, "zoneLowBoundary": 100}])


class ActivityFilterTest(unittest.TestCase):
    def test_running_variants_are_included(self):
        self.assertTrue(is_running_activity({"activityType": {"typeKey": "running"}}))
        self.assertTrue(is_running_activity({"activityType": {"typeKey": "trail_running"}}))

    def test_non_running_activity_is_excluded(self):
        self.assertFalse(is_running_activity({"activityType": {"typeKey": "cycling"}}))


class ChangeDetectionTest(unittest.TestCase):
    def snapshot(self, day, thresholds, activity_id):
        return ZoneSnapshot(activity_id, dt.date.fromisoformat(day), "Run", thresholds)

    def test_keeps_initial_snapshot_and_changes_only(self):
        snapshots = [
            self.snapshot("2022-05-02", (100, 120, 140, 160, 180), 1),
            self.snapshot("2022-05-05", (100, 120, 140, 160, 180), 2),
            self.snapshot("2022-05-08", (101, 121, 141, 161, 181), 3),
        ]
        result = changed_snapshots(snapshots)
        self.assertEqual([item.activity_id for item in result], [1, 3])

    def test_same_day_uses_final_changed_snapshot(self):
        snapshots = [
            self.snapshot("2022-05-02", (100, 120, 140, 160, 180), 1),
            self.snapshot("2022-05-08", (101, 121, 141, 161, 181), 2),
            self.snapshot("2022-05-08", (102, 122, 142, 162, 182), 3),
        ]
        result = changed_snapshots(snapshots)
        self.assertEqual([item.activity_id for item in result], [1, 3])

    def test_csv_columns(self):
        stream = io.StringIO()
        write_csv([self.snapshot("2022-05-02", (100, 120, 140, 160, 180), 1)], stream)
        self.assertIn("zone1_min,zone2_min,zone3_min,zone4_min,zone5_min", stream.getvalue())
        self.assertIn("2022-05-02,1,Run,100,120,140,160,180", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
