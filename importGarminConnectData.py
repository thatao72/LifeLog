from garminconnect import Garmin
import datetime
import csv
import json

# Initialize the Garmin Connect client
client = Garmin("tsuyoshi_hatao@yahoo.co.jp", "18Mar1969")
client.login()

# Set the date range (adjust as needed)
start_date = datetime.date(2022,4,25)
end_date = datetime.date.today()

# Prepare CSV file
with open('garmin_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['Date', 'Resting HR', 'Sleep Score', 'Stress', 'Body Battery High', 'Body Battery Low', 'Weight']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    body_composition_data = client.get_body_composition(start_date, end_date)
    weight_dict = {item['calendarDate']: item['weight'] for item in body_composition_data.get('dateWeightList', [])}
    
    # Iterate through each day
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"\nFetching data for {date_str}")

        sleep_data = client.get_sleep_data(date_str)
        user_summary = client.get_user_summary(date_str)

        # Extract relevant information (adjust based on actual data structure)
        rhr = user_summary.get('restingHeartRate', None) if user_summary else None
        sleep_score = sleep_score = sleep_data.get("dailySleepDTO", {}).get("sleepScores", {}).get("overall", {}).get("value") if sleep_data else None
        stress = user_summary.get('averageStressLevel', None) if user_summary else None
        body_battery_high = user_summary.get('bodyBatteryHighestValue', None) if user_summary else None
        body_battery_low = user_summary.get('bodyBatteryLowestValue', None) if user_summary else None
        weight = weight_dict.get(date_str)
        if weight is not None:
            weight /= 1000.0
    
        # Write data to CSV
        writer.writerow({
            'Date': date_str,
            'Resting HR': rhr,
            'Sleep Score': sleep_score,
            'Stress': stress,
            'Body Battery High': body_battery_high,
            'Body Battery Low': body_battery_low,
            'Weight': weight
        })

        current_date += datetime.timedelta(days=1)

print("Data extraction complete. Results saved in garmin_data.csv")
