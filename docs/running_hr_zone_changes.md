# Running HR-zone threshold history

`running_hr_zone_changes.py` scans Garmin Connect running activities from 2022-05-02 onward, reads the heart-rate time-in-zone data stored on each activity, and writes only dates whose five zone lower boundaries differ from the preceding running date.

The first running date is used as the comparison baseline and is not output. If there are multiple runs on one date, the final activity on that date is used.

## Authentication

For the first login:

```bash
export GARMIN_USERNAME='your-email'
export GARMIN_PASSWORD='your-password'
python running_hr_zone_changes.py --output running_hr_zone_changes.csv
```

Tokens are saved by default under `~/.garminconnect`. On later runs, the saved token directory is used. Override it with `GARMIN_TOKEN_DIR`.

## Usage

```bash
python running_hr_zone_changes.py \
  --start-date 2022-05-02 \
  --output running_hr_zone_changes.csv
```

Optional arguments:

- `--end-date YYYY-MM-DD`: defaults to today.
- `--strict`: fail when an activity has no usable HR-zone payload instead of skipping it.
- `--raw-json PATH`: also save all parsed activity snapshots for troubleshooting.

CSV columns:

```text
date,activity_id,activity_name,zone1_min,zone2_min,zone3_min,zone4_min,zone5_min
```

Each zone value is the lower boundary in bpm reported by Garmin's activity `hrTimeInZones` endpoint.

## Tests

```bash
python -m unittest discover -s tests
```

## API note

`garminconnect` is an unofficial wrapper around Garmin Connect's private API. Garmin may change response fields without notice. The parser accepts several known wrapper shapes and skips malformed activities by default.
