from O365 import Account
from datetime import datetime
import pytz
import pandas as pd

# Authenticate with Outlook
credentials = ("client_id", "client_secret")
account = Account(credentials)
if not account.is_authenticated:
    account.authenticate(scopes=['basic', 'calendar_all'])

# Fetch calendar events for the year 2024
def fetch_appointments_for_year():
    schedule = account.schedule()
    calendar = schedule.get_default_calendar()

    # Define the date range for 2024
    start_date = datetime(2024, 1, 1, tzinfo=pytz.utc)
    end_date = datetime(2024, 12, 31, 23, 59, 59, tzinfo=pytz.utc)

    events = calendar.get_events(start=start_date, end=end_date)

    data = []
    for event in events:
        data.append({
            "Subject": event.subject,
            "Start": event.start.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M"),
            "End": event.end.astimezone(pytz.utc).strftime("%Y-%m-%d %H:%M"),
            "Location": event.location if event.location else "",
            "Categories": ", ".join(event.categories) if event.categories else ""
        })

    return pd.DataFrame(data)

# Save to CSV
def save_appointments_to_csv():
    try:
        df = fetch_appointments_for_year()
        df.to_csv("appointments_2024.csv", index=False)
        print("Appointments saved to appointments_2024.csv")
    except Exception as e:
        print(f"Error saving appointments: {e}")

# Run the script
if __name__ == "__main__":
    save_appointments_to_csv()