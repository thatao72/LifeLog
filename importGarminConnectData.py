from garminconnect import Garmin
import datetime
import csv
import json
import io
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# Google Drive API setup
SCOPES = ['https://www.googleapis.com/auth/drive']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
drive_service = build('drive', 'v3', credentials=creds)

def read_existing_data(file_id):
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

def write_csv(file_id, data, fieldnames):
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    for date in sorted(data.keys()):
        writer.writerow(data[date])
    
    media = MediaIoBaseUpload(io.BytesIO(output.getvalue().encode()),
                              mimetype='text/csv',
                              resumable=True)
    drive_service.files().update(fileId=file_id, media_body=media).execute()

# Initialize the Garmin Connect client
client = Garmin("tsuyoshi_hatao@yahoo.co.jp", "18Mar1969")
client.login()

# Set the date range
start_date = datetime.date(2022, 4, 25)
end_date = datetime.date.today() + datetime.timedelta(days=-1)

file_id = '1TOMjmLt8fWDiuF1TUx0k4WPk0AujeNDg'  # Replace with your actual file ID
fieldnames = ['date', 'restingHeartRate', 'sleepScore', 'stress', 'bodyBatteryHigh', 'bodyBatteryLow', 'weight']

# Read existing data
existing_data = read_existing_data(file_id)

# Find the last date in existing data
if existing_data:
    last_date = max(datetime.datetime.strptime(date, "%Y-%m-%d").date() for date in existing_data.keys())
    start_date = last_date + datetime.timedelta(days=1)

if start_date <= end_date:
    print(f"Fetching new data from {start_date} to {end_date}")

    # Fetch body composition data for the new date range
    body_composition_data = client.get_body_composition(start_date, end_date)
    weight_dict = {item['calendarDate']: item['weight'] for item in body_composition_data.get('dateWeightList', [])}

    # Iterate through each day
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"\nFetching data for {date_str}")

        sleep_data = client.get_sleep_data(date_str)
        user_summary = client.get_user_summary(date_str)

        # Extract relevant information
        rhr = user_summary.get('restingHeartRate', None) if user_summary else None
        sleep_score = sleep_data.get("dailySleepDTO", {}).get("sleepScores", {}).get("overall", {}).get("value") if sleep_data else None
        stress = user_summary.get('averageStressLevel', None) if user_summary else None
        body_battery_high = user_summary.get('bodyBatteryHighestValue', None) if user_summary else None
        body_battery_low = user_summary.get('bodyBatteryLowestValue', None) if user_summary else None
        weight = weight_dict.get(date_str)
        if weight is not None:
            weight /= 1000.0

        # Add new data to existing data
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

    # Write updated data to CSV on Google Drive
    write_csv(file_id, existing_data, fieldnames)

    print("Data extraction complete. Results saved in Google Drive CSV file.")
