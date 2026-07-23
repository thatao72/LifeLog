# how to push files to Google Apps Studio: use clasp
## files to be pushed:
- Code.js
- CustomFmenu.js
- index.html
- charts.html
# clasp configuration is in .clasp.json and .claspignore
> clasp push

# how to push client.js to unpkg
# 1. Ensure client.js is part of a public npm package.
# 2. Update the package version in package.json.
# 3. Publish the package to npm:
> npm publish
# 4. Access the file via unpkg (in html code e.g. in index.html):
#    https://unpkg.com/<package-name>@<version>/client.js

# files for main.py local run
Usually, local token.json is expired and you need to rerun auth.py after removeing token.json (>rm token.json; >python auth.py)
- .env : all environment variables
- client_secret_.json : downloaded secret for Google Drive
- token.json : token to access to files on Google Drive (past uploaded data)
- auth.py : generate token.json with client_secret_.json
-- legacy files: garminConnectActivities.py and filtered_activities.csv

# how to deploy main.py as Google Cloud Run
## run Docker with VSCode Container extension
- Use Dockerfile to define what to do
- Run Docker.app (double click the file in Application directory)
- Open Command Palette → “Container Images: Build Image…”
- Select Dockerfile path, enter FULL Artifact Registry image name (e.g. asia-northeast1-docker.pkg.dev/importgarminconnect/import-garmin-connect/import-garmin-connect:latest)
- Wait for build output in VS Code Terminal/Output.
- Then Push image by clicking on latest IMAGES. Sometime auth expired and you will be asked to run "gcloud auth login".

# Cloud Run Job Deployment via Google Cloud Console

This guide outlines the steps to deploy a containerized Python script as a **Cloud Run Job** using the Google Cloud Console, assuming the container image has already been built and pushed to **Artifact Registry**.

## Prerequisites

* A **Google Cloud Project** with billing enabled.
* The **Cloud Run Admin API** enabled.
* Your final container image pushed to a **Google Artifact Registry** repository (e.g., `REGION-docker.pkg.dev/PROJECT-ID/REPO-NAME/IMAGE-NAME:TAG`).

---

## Step 1: Navigate to Cloud Run Jobs

1.  Go to the **Google Cloud Console**.
2.  In the main navigation menu, select **Cloud Run**.
3.  Ensure you are on the **Jobs** tab (not the Services tab).
4.  Click the **CREATE JOB** button.

## Step 2: Configure Basic Job Settings

You will be taken to the "Create job" form. Configure the following core settings:

* **Region:** Select the geographic location for your job execution (this defines the **server region**).
* **Job Name:** Provide a unique, descriptive name for your job (e.g., `daily-etl-processor`).
* **Container Image URL:** Enter the **full path** to your image in Artifact Registry (e.g., `us-central1-docker.pkg.dev/my-project/my-repo/my-job:v1`).

## Step 3: Configure Job Execution Parameters

Expand the **Container, Networking, Security** section to set runtime behavior:

* **Tasks:** Define the number of parallel instances. Set this to **`1`** for a standard, sequential run, or higher for parallel processing.
* **CPU & Memory:** Allocate the necessary **CPU** and **Memory** resources for your script's execution.
* **Timeout:** Set the maximum duration a single task can run before cancellation (maximum of 24 hours).
* **Max Retries:** Configure how many times a task should automatically restart if it fails.
* **Environment Variables:** If your Python code requires configuration at runtime (like database connection strings or input paths), define them here as **Key/Value** pairs.
* **Service Account:** Verify or set the **Service Account** that the job will run as, ensuring it has the necessary IAM permissions (e.g., to read from or write to Cloud Storage).

## Step 4: Deploy and Execute

1.  Review all settings.
2.  Click the **CREATE** button. This deploys the job definition.
3.  After successful creation, navigate to the Job's details page and click the **EXECUTE** button to start the first run immediately. You can monitor the status on the **Executions** tab.

---

# Running HR-zone threshold change history

`running_hr_zone_changes.py` retrieves running activities from Garmin Connect and compares the lower boundaries of heart-rate zones 1–5 stored on each activity.

Only dates whose threshold set differs from the preceding running date are written to CSV. The first running date is used as the baseline and is not output. If multiple runs occur on the same date, the final activity on that date is used.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Garmin credentials in zsh

If `.env` contains `export` statements:

```bash
source .env
```

If `.env` does not contain `export` statements:

```bash
set -a
source .env
set +a
```

Required variables:

```bash
GARMIN_USERNAME='Garmin Connect email address'
GARMIN_PASSWORD='Garmin Connect password'
GARMIN_TOKEN_DIR="$HOME/.garminconnect"
```

Confirm that they are exported:

```bash
env | grep '^GARMIN_'
```

Do not commit `.env` or Garmin authentication tokens.

## Unit tests

```bash
python -m unittest discover -s tests -v
```

## Short-period validation

```bash
python running_hr_zone_changes.py \
  --start-date 2026-06-01 \
  --end-date 2026-07-22 \
  --output ./running_hr_zone_changes.csv \
  --raw-json ./running_hr_zone_snapshots.json
```

- `running_hr_zone_changes.csv`: threshold-change dates only
- `running_hr_zone_snapshots.json`: all retrieved running threshold snapshots

If no threshold changed during the selected period, the CSV contains only its header.

## Full history from 2022-05-02

Omitting `--end-date` uses the execution date.

```bash
python running_hr_zone_changes.py \
  --start-date 2022-05-02 \
  --output ./running_hr_zone_changes.csv \
  --raw-json ./running_hr_zone_snapshots.json
```

## CSV columns

```text
date,activity_id,activity_name,zone1_min,zone2_min,zone3_min,zone4_min,zone5_min
```

Each `zoneN_min` is the lower heart-rate boundary for that zone in bpm.

## Error investigation

By default, activities without usable HR-zone data are skipped. Add `--strict` to stop at the first retrieval or parsing error.

```bash
python running_hr_zone_changes.py \
  --start-date 2026-06-01 \
  --end-date 2026-07-22 \
  --output ./running_hr_zone_changes.csv \
  --raw-json ./running_hr_zone_snapshots.json \
  --strict
```
