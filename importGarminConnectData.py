from garminconnect import Garmin
import datetime
import csv

# Initialize the Garmin Connect client
client = Garmin("tsuyoshi_hatao@yahoo.co.jp", "18Mar1969")
client.login()

# Set the date range (adjust as needed)
end_date = datetime.date.today()
start_date = end_date - datetime.timedelta(days=3*365)  # 3 years of data

# Prepare CSV file
with open('garmin_data.csv', 'w', newline='') as csvfile:
    fieldnames = ['Date', 'Resting HR', 'Sleep Score', 'Stress', 'Body Battery High', 'Body Battery Low', 'Weight']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    # Iterate through each day
    current_date = start_date
    while current_date <= end_date:
        date_str = current_date.strftime("%Y-%m-%d")
        print(f"Fetching data for {date_str}")

        # Fetch data for each metric
        rhr_data = client.get_resting_heart_rate(date_str)
        sleep_data = client.get_sleep_data(date_str)
        stress_data = client.get_stress_data(date_str)
        body_battery_data = client.get_body_battery(date_str)
        weight_data = client.get_body_composition(date_str)

        # Extract relevant information
        rhr = rhr_data.get('value', {}).get('restingHeartRate', None) if rhr_data else None
        sleep_score = sleep_data.get('sleepScoreValue', None) if sleep_data else None
        stress = stress_data.get('avgStressLevel', None) if stress_data else None
        body_battery_high = max(point['value'] for point in body_battery_data) if body_battery_data else None
        body_battery_low = min(point['value'] for point in body_battery_data) if body_battery_data else None
        weight = weight_data.get('weight', None) if weight_data else None

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
