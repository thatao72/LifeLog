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

# how to deploy main.py as Google Cloud Run
## run Docker with VSCode Container extension
- Use Dockerfile to define what to do
- Run Docker.app (double click the file in Application directory)
- Open Command Palette → “Container Images: Build Image…”
- Select Dockerfile path, enter image name (e.g. lifelog:local)
- Wait for build output in VS Code Terminal/Output.

# files for main.py local run
- .env : all environment variables
- client_secret_.json : downloaded secret for Google Drive
- token.json : token to access to files on Google Drive (past uploaded data)
- auth.py : generate token.json with client_secret_.json
-- legacy files: garminConnectActivities.py and filtered_activities.csv

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
* **CPU & Memory:** Allocate the necessary **CPU** and **Memory** resources for your Python script's execution.
* **Timeout:** Set the maximum duration a single task can run before cancellation (maximum of 24 hours).
* **Max Retries:** Configure how many times a task should automatically restart if it fails.
* **Environment Variables:** If your Python code requires configuration at runtime (like database connection strings or input paths), define them here as **Key/Value** pairs.
* **Service Account:** Verify or set the **Service Account** that the job will run as, ensuring it has the necessary IAM permissions (e.g., to read from or write to Cloud Storage).

## Step 4: Deploy and Execute

1.  Review all settings.
2.  Click the **CREATE** button. This deploys the job definition.
3.  After successful creation, navigate to the Job's details page and click the **EXECUTE** button to start the first run immediately. You can monitor the status on the **Executions** tab.
