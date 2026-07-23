#!/usr/bin/env python3
"""Export dates on which Garmin running HR-zone thresholds changed.

Garmin Connect stores the heart-rate time-in-zone breakdown on each activity.
The lower boundary of each zone is therefore a historical snapshot of the
thresholds used for that activity, rather than the user's current profile.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, TextIO

from garminconnect import Garmin

DEFAULT_START_DATE = dt.date(2022, 5, 2)
RUNNING_TYPE_KEYS = {"running", "trail_running", "treadmill_running", "indoor_running"}


@dataclass(frozen=True)
class ZoneSnapshot:
    activity_id: int
    activity_date: dt.date
    activity_name: str
    thresholds: tuple[int, ...]


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"Invalid date {value!r}; use YYYY-MM-DD") from exc


def activity_date(activity: Mapping[str, Any]) -> dt.date:
    """Return the activity's local calendar date."""
    for key in ("startTimeLocal", "startTimeGMT", "calendarDate"):
        value = activity.get(key)
        if not value:
            continue
        text = str(value)
        try:
            return dt.datetime.fromisoformat(text.replace("Z", "+00:00")).date()
        except ValueError:
            try:
                return dt.date.fromisoformat(text[:10])
            except ValueError:
                pass
    raise ValueError(f"Activity {activity.get('activityId')} has no parseable date")


def is_running_activity(activity: Mapping[str, Any]) -> bool:
    activity_type = activity.get("activityType") or {}
    type_key = str(activity_type.get("typeKey", "")).lower()
    parent_key = str(activity_type.get("parentTypeId", "")).lower()
    return type_key in RUNNING_TYPE_KEYS or parent_key == "running"


def _zone_rows(payload: Any) -> Sequence[Mapping[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, Mapping)]
    if isinstance(payload, Mapping):
        for key in ("hrTimeInZones", "zones", "zoneData", "data"):
            rows = payload.get(key)
            if isinstance(rows, list):
                return [row for row in rows if isinstance(row, Mapping)]
    return []


def extract_thresholds(payload: Any) -> tuple[int, ...]:
    """Extract ordered zone lower boundaries from Garmin's response.

    Garmin's undocumented endpoint has used several key spellings over time,
    so this parser accepts the known variants while requiring five distinct
    numbered zones.
    """
    boundaries: dict[int, int] = {}
    for index, row in enumerate(_zone_rows(payload), start=1):
        zone_raw = row.get("zoneNumber", row.get("zone", row.get("zoneIndex", index)))
        boundary_raw = row.get(
            "zoneLowBoundary",
            row.get("lowBoundary", row.get("lowerBoundary", row.get("minHeartRate"))),
        )
        if boundary_raw is None:
            continue
        try:
            zone = int(zone_raw)
            boundary = int(round(float(boundary_raw)))
        except (TypeError, ValueError):
            continue
        if 1 <= zone <= 5:
            boundaries[zone] = boundary

    if sorted(boundaries) != [1, 2, 3, 4, 5]:
        raise ValueError(f"Expected zone boundaries 1-5, got {sorted(boundaries)}")
    thresholds = tuple(boundaries[zone] for zone in range(1, 6))
    if list(thresholds) != sorted(thresholds):
        raise ValueError(f"Zone boundaries are not ascending: {thresholds}")
    return thresholds


def get_running_activities(client: Garmin, start: dt.date, end: dt.date) -> list[Mapping[str, Any]]:
    activities = client.get_activities_by_date(start.isoformat(), end.isoformat())
    running = [activity for activity in activities if is_running_activity(activity)]
    return sorted(running, key=lambda item: (activity_date(item), str(item.get("startTimeLocal", ""))))


def collect_snapshots(
    client: Garmin,
    start: dt.date,
    end: dt.date,
    *,
    skip_missing_zones: bool = True,
) -> list[ZoneSnapshot]:
    snapshots: list[ZoneSnapshot] = []
    for activity in get_running_activities(client, start, end):
        activity_id = int(activity["activityId"])
        try:
            thresholds = extract_thresholds(client.get_activity_hr_in_timezones(activity_id))
        except Exception as exc:
            if not skip_missing_zones:
                raise
            print(f"Skipping activity {activity_id}: {exc}", file=sys.stderr)
            continue
        snapshots.append(
            ZoneSnapshot(
                activity_id=activity_id,
                activity_date=activity_date(activity),
                activity_name=str(activity.get("activityName") or ""),
                thresholds=thresholds,
            )
        )
    return snapshots


def changed_snapshots(snapshots: Iterable[ZoneSnapshot]) -> list[ZoneSnapshot]:
    """Return dates whose final threshold set differs from the preceding run date.

    The first date is a comparison baseline and is not emitted. For multiple
    runs on the same date, the final activity is treated as that day's value.
    """
    final_by_date: dict[dt.date, ZoneSnapshot] = {}
    for snapshot in snapshots:
        final_by_date[snapshot.activity_date] = snapshot

    changes: list[ZoneSnapshot] = []
    previous: tuple[int, ...] | None = None
    for date in sorted(final_by_date):
        snapshot = final_by_date[date]
        if previous is not None and snapshot.thresholds != previous:
            changes.append(snapshot)
        previous = snapshot.thresholds
    return changes


def write_csv(snapshots: Iterable[ZoneSnapshot], stream: TextIO) -> None:
    fieldnames = ["date", "activity_id", "activity_name", "zone1_min", "zone2_min", "zone3_min", "zone4_min", "zone5_min"]
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    for snapshot in snapshots:
        writer.writerow(
            {
                "date": snapshot.activity_date.isoformat(),
                "activity_id": snapshot.activity_id,
                "activity_name": snapshot.activity_name,
                **{f"zone{index}_min": value for index, value in enumerate(snapshot.thresholds, start=1)},
            }
        )


def login() -> Garmin:
    username = os.environ.get("GARMIN_USERNAME")
    password = os.environ.get("GARMIN_PASSWORD")
    token_dir = Path(os.environ.get("GARMIN_TOKEN_DIR", "~/.garminconnect")).expanduser()

    client = Garmin(username or "", password or "")
    if token_dir.exists():
        client.login(str(token_dir))
    elif username and password:
        client.login()
        token_dir.mkdir(parents=True, exist_ok=True)
        client.garth.dump(str(token_dir))
    else:
        raise RuntimeError(
            "Set GARMIN_USERNAME and GARMIN_PASSWORD for first login, or provide GARMIN_TOKEN_DIR containing saved tokens."
        )
    return client


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-date", type=parse_date, default=DEFAULT_START_DATE)
    parser.add_argument("--end-date", type=parse_date, default=dt.date.today())
    parser.add_argument("--output", type=Path, help="CSV path; defaults to stdout")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail instead of skipping activities without usable HR-zone data",
    )
    parser.add_argument(
        "--raw-json",
        type=Path,
        help="Optional path for all parsed activity snapshots as JSON",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.start_date > args.end_date:
        raise SystemExit("--start-date must not be after --end-date")

    snapshots = collect_snapshots(
        login(),
        args.start_date,
        args.end_date,
        skip_missing_zones=not args.strict,
    )
    changes = changed_snapshots(snapshots)

    if args.raw_json:
        args.raw_json.write_text(
            json.dumps(
                [
                    {
                        "date": item.activity_date.isoformat(),
                        "activity_id": item.activity_id,
                        "activity_name": item.activity_name,
                        "thresholds": item.thresholds,
                    }
                    for item in snapshots
                ],
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    if args.output:
        with args.output.open("w", encoding="utf-8", newline="") as stream:
            write_csv(changes, stream)
    else:
        write_csv(changes, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
