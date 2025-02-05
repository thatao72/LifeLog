from garminconnect import Garmin
import datetime
import csv
import io
import os

from google.auth import default
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
from google.oauth2 import service_account

# import requests
# from google.auth.transport.requests import Request

# def compare_tokens():
#     """
#     Compares the access token retrieved by google.auth.default() with the token from the metadata server.
#     Returns a dictionary with the tokens and whether they match.
#     """
#     try:
#         # Retrieve default credentials
#         credentials = default(scopes=['https://www.googleapis.com/auth/drive.file'])
#         # Force re-scoping with required Drive API scope
#         if credentials.requires_scopes:
#             credentials = credentials.with_scopes(['https://www.googleapis.com/auth/drive.file'])
#         credentials.refresh(Request())
#         default_token = credentials.token

#         # Retrieve token from metadata server
#         metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
#         headers = {"Metadata-Flavor": "Google"}
#         response = requests.get(metadata_url, headers=headers)
#         response.raise_for_status()  # Raise an error if the request fails
#         metadata_token = response.json()["access_token"]

#         # Compare tokens
#         tokens_match = default_token == metadata_token

#         return {
#             "default_token": default_token,
#             "metadata_token": metadata_token,
#             "tokens_match": tokens_match
#         }

#     except Exception as e:
#         return {"error": str(e)}


# def test_drive_access(access_token, file_id):
#     # Define the Google Drive API URL for the specific file
#     url = f"https://www.googleapis.com/drive/v3/files/{file_id}?fields=name,id,permissions"

#     # Set up the Authorization header with the access token
#     headers = {
#         "Authorization": f"Bearer {access_token}"
#     }

#     # Make the GET request to Google Drive API
#     response = requests.get(url, headers=headers)

#     # Print the response
#     if response.status_code == 200:
#         print("File Metadata:", response.json())
#     else:
#         print(f"Error: {response.status_code}")
#         print("Response:", response.json())

# def inspect_token(token):
#     url = "https://oauth2.googleapis.com/tokeninfo"
#     params = {"access_token": token}
#     response = requests.get(url, params=params)
#     print(response.json())

# def get_service_account_email():
#     metadata_url = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
#     headers = {"Metadata-Flavor": "Google"}
#     response = requests.get(metadata_url, headers=headers)
#     if response.status_code == 200:
#         return response.text
#     else:
#         raise Exception(f"Failed to fetch service account email: {response.status_code}, {response.text}")

# from google.auth.transport.requests import Request
# def test_adc():
#     credentials, project = default(scopes=['https://www.googleapis.com/auth/drive.file'])
#     print(f"Credentials Type: {type(credentials)}")
#     print(f"Project: {project}")
#     if credentials.requires_scopes:
#         print("Scopes are required but not set.")
#     else:
#         print(f"Scopes: {credentials.scopes}")

#     # Refresh credentials
#     credentials.refresh(Request())

#     # Test Google Drive API access
#     drive_service = build('drive', 'v3', credentials=credentials)
#     results = drive_service.files().list(pageSize=10).execute()
#     print(results)


# def test_cred():
#     """Tests the default credentials and reports information."""
#     # creds, project = default(scopes=['https://www.googleapis.com/auth/drive.file'])
#     creds = service_account.Credentials.from_service_account_file('/app/secret/cloud-run-service-account-key')  # Path matches the mount path

#     # if creds.valid:
#     print("Credentials are valid.")

#     if creds.service_account_email:
#         print(f"Service account email: {creds.service_account_email}")
#     else:
#         print("Not a service account.")

#     if creds.expired:
#         print("Credentials are expired. Refresh if needed.")

#     if hasattr(creds, 'scopes'):
#         print(f"Scopes: {creds.scopes}")

#     try:
#         drive_service = build('drive', 'v3', credentials=creds)
#         files = drive_service.files().list().execute()  # Attempt a Drive operation
#         print("Successfully listed files (indirect permission check).")
#         # You could also print a file name for further verification:
#         if files.get('files'):
#             print(f"Example file name: {files.get('files')[0].get('name')}")
#         else:
#             print("No files found in Drive (check sharing settings).")

#     except Exception as e:
#         print(f"Error accessing Google Drive (permission issue?): {e}")

#     # else:
#     #     print("Credentials are not valid.")

# def test_drive_access():
#     creds, _ = default(scopes=['https://www.googleapis.com/auth/drive.file'])
#     drive_service = build('drive', 'v3', credentials=creds)

#     file_id = os.environ.get("GOOGLE_DRIVE_FILE_ID")

#     if not file_id:
#         raise ValueError("Missing GOOGLE_DRIVE_FILE_ID environment variable")

#     try:
#         # Try to get file metadata (a simple test)
#         file = drive_service.files().get(fileId=file_id, supportsAllDrives=True).execute()
#         print(f"File found: {file.get('name')}") # Print the file name to verify
#     except Exception as e:
#         print(f"Error accessing file: {e}")

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
    # creds, _ = default(scopes=['https://www.googleapis.com/auth/drive.file'])
    creds = service_account.Credentials.from_service_account_file('/app/secret/cloud-run-service-account-key')
    drive_service = build('drive', 'v3', credentials=creds)

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
    end_date = datetime.date.today() + datetime.timedelta(days=-1)

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