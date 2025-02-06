from garminconnect import Garmin
import datetime
import pytz
import csv
import io
import os
import requests

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload, HttpRequest

SCOPES = ['https://www.googleapis.com/auth/drive.file']

def build_drive_service_locally():
    try:
        # Import dotenv and google.oauth2.credentials dynamically (only for local use)
        from dotenv import load_dotenv
        from google.oauth2.credentials import Credentials
        
        # Load environment variables from .env file
        load_dotenv()

        # Get credentials from token.json
        creds = None
        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not creds or not creds.valid:
            raise Exception("Invalid or missing credentials. Please authenticate locally using token.json.")

        # Build and return the Drive API service
        return build('drive', 'v3', credentials=creds)
    except ImportError as e:
        raise ImportError("Missing required libraries for local execution. Install `dotenv` and `google-auth-oauthlib`.")

def get_metadata_server_token():
    metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
    headers = {"Metadata-Flavor": "Google"}
    response = requests.get(metadata_url, headers=headers)
    response.raise_for_status()
    return response.json()["access_token"]

def build_drive_service_cloud():
    # Get the access token from metadata server
    access_token = get_metadata_server_token()

    # Create a custom request object with the token
    def custom_request_builder(*args, **kwargs):
        kwargs['headers'] = kwargs.get('headers', {})
        kwargs['headers']['Authorization'] = f"Bearer {access_token}"
        return HttpRequest(*args, **kwargs)

    # Build the Drive API service
    return build('drive', 'v3', requestBuilder=custom_request_builder)

def is_running_in_cloud():
    """
    Determines if the script is running in a Google Cloud environment by checking for the metadata server.
    """
    try:
        # Attempt to access the metadata server
        response = requests.get(
            "http://metadata.google.internal/computeMetadata/v1/",
            headers={"Metadata-Flavor": "Google"},
            timeout=1  # Short timeout to avoid delays locally
        )
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def build_drive_service():
    """
    Dynamically builds the appropriate Drive API service based on the environment (local or cloud).
    """
    if is_running_in_cloud():
        print("Running in Google Cloud environment.")
        return build_drive_service_cloud()
    else:
        print("Running in local environment.")
        return build_drive_service_locally()
        
def read_existing_data(drive_service, file_id):
    request = drive_service.files().get_media(fileId=file_id, supportsAllDrives=True)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    fh.seek(0)
    data = {}
    reader = csv.DictReader(io.TextIOWrapper(fh))
    for row in reader:
        data[row['date']] = row
    return data

def write_csv(drive_service, file_id, data, fieldnames):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for date in sorted(data.keys()):
        writer.writerow(data[date])

    media = MediaIoBaseUpload(io.BytesIO(output.getvalue().encode()),
                              mimetype='text/csv',
                              resumable=True)
    drive_service.files().update(fileId=file_id, media_body=media).execute()

def main():
    # 1. Service Account setup (for Cloud Functions)
    drive_service = build_drive_service()

    # 2. Get environment variables
    garmin_username = os.environ.get("GARMIN_USERNAME")
    garmin_password = os.environ.get("GARMIN_PASSWORD")
    file_id = os.environ.get("GOOGLE_DRIVE_FILE_ID")

    if not garmin_username or not garmin_password or not file_id:
      raise ValueError("Missing environment variables: GARMIN_USERNAME, GARMIN_PASSWORD, GOOGLE_DRIVE_FILE_ID")

    # 3. Garmin Connect setup
    client = Garmin(garmin_username, garmin_password)
    client.login()

    # 4. Date range and data processing (same as before)
    start_date = datetime.date(2022, 4, 25)  # Or get from env variable if needed
    end_date = datetime.datetime.now(pytz.timezone('Asia/Tokyo')).date() + datetime.timedelta(days=-1)
    print(f"Today is {end_date}")

    fieldnames = ['date', 'restingHeartRate', 'sleepScore', 'stress', 'bodyBatteryHigh', 'bodyBatteryLow', 'weight']

    existing_data = read_existing_data(drive_service, file_id)

    if existing_data:
        last_date = max(datetime.datetime.strptime(date, "%Y-%m-%d").date() for date in existing_data.keys())
        start_date = last_date + datetime.timedelta(days=1)

    if start_date <= end_date:
        print(f"Fetching new data from {start_date} to {end_date}")

        body_composition_data = client.get_body_composition(start_date, end_date)
        weight_dict = {item['calendarDate']: item['weight'] for item in body_composition_data.get('dateWeightList', [])}

        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            print(f"\nFetching data for {date_str}")

            sleep_data = client.get_sleep_data(date_str)
            user_summary = client.get_user_summary(date_str)

            rhr = user_summary.get('restingHeartRate', None) if user_summary else None
            sleep_score = sleep_data.get("dailySleepDTO", {}).get("sleepScores", {}).get("overall", {}).get("value") if sleep_data else None
            stress = user_summary.get('averageStressLevel', None) if user_summary else None
            body_battery_high = user_summary.get('bodyBatteryHighestValue', None) if user_summary else None
            body_battery_low = user_summary.get('bodyBatteryLowestValue', None) if user_summary else None
            weight = weight_dict.get(date_str)
            if weight is not None:
                weight /= 1000.0

            existing_data[date_str] = {
                'date': date_str,
                'restingHeartRate': rhr,
                'sleepScore': sleep_score,
                'stress': stress,
                'bodyBatteryHigh': body_battery_high,
                'bodyBatteryLow': body_battery_low,
                'weight': weight
            }

            current_date += datetime.timedelta(days=1)

        write_csv(drive_service, file_id, existing_data, fieldnames)

        print("Data extraction complete. Results saved in Google Drive CSV file.")

if __name__ == "__main__":
    main()