from garminconnect import Garmin
import datetime
import csv
import io
import os

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

from dotenv import load_dotenv

def read_existing_data(drive_service, file_id):  # Pass drive_service as argument
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

def write_csv(drive_service, file_id, data, fieldnames): # Pass drive_service as argument
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
    SCOPES = ['https://www.googleapis.com/auth/drive.file']  # Correct scope
    creds = service_account.Credentials.from_service_account_info(
        info={},  # Empty dict for Cloud Functions auto-detection
        scopes=SCOPES
    )

    drive_service = build('drive', 'v3', credentials=creds)

    # 2. Get environment variables
    garmin_username = os.environ.get("GARMIN_USERNAME")
    garmin_password = os.environ.get("GARMIN_PASSWORD")
    file_id = os.environ.get("GOOGLE_DRIVE_FILE_ID")  # Get file ID from env variable

    if not garmin_username or not garmin_password or not file_id:
      raise ValueError("Missing environment variables: GARMIN_USERNAME, GARMIN_PASSWORD, GOOGLE_DRIVE_FILE_ID")

    # 3. Garmin Connect setup
    client = Garmin(garmin_username, garmin_password)
    client.login()

    # 4. Date range and data processing (same as before)
    start_date = datetime.date(2022, 4, 25)  # Or get from env variable if needed
    end_date = datetime.date.today() + datetime.timedelta(days=-1)

    fieldnames = ['date', 'restingHeartRate', 'sleepScore', 'stress', 'bodyBatteryHigh', 'bodyBatteryLow', 'weight']

    existing_data = read_existing_data(drive_service, file_id) # Pass drive_service

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

        write_csv(drive_service, file_id, existing_data, fieldnames)  # Pass drive_service

        print("Data extraction complete. Results saved in Google Drive CSV file.")

if __name__ == "__main__":
    main()