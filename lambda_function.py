import os
from datetime import datetime
import smtplib
import requests
# from twilio.rest import Client

GMAIL_ACCOUNT = os.environ["gmail_account"]
GMAIL_PASSWORD = os.environ["gmail_password"]
START_DATE = os.environ["start_date"]
END_DATE = os.environ["end_date"]
LIST_DAYS_TO_INCLUDE = [int(x) for x in os.environ["days_to_include"].split(",")]
# TWILIO_ACCOUNT_SID = os.environ["twilio_account_sid"]
# TWILIO_AUTH_TOKEN = os.environ["twilio_auth_token"]
# TWILIO_TO_NUM = os.environ["twilio_to_num"]
# TWILIO_FROM_NUM = os.environ["twilio_from_num"]

PARKS = {
    # "232446": "Wawona",
    "232447": "UPPER PINES",
    # "232448": "TUOLOMNE MEADOWS",
    "232449": "NORTH PINES",
    "232450": "LOWER PINES",
}

BASE_URL = "https://www.recreation.gov"
CAMPGROUND_AVAILABILITY = "/api/camps/availability/campground/"
CAMPSTIES_URL = "/camping/campsites/"

def get_available_campsites(start_time, end_time, list_days_to_include):
    available_campsites = []
    try:
        for park in PARKS:
            campground_availabilities = get_campground_availabilities(
                park, start_time, end_time
            )
            for _, campsite_details in campground_availabilities["campsites"].items():
                available_campsites = (
                    available_campsites
                    + get_availabilities_for_campsite(
                        PARKS[park], campsite_details, list_days_to_include
                    )
                )
    except RuntimeError as err:
        print("Runtime error: {0}".format(err))

    return available_campsites

def get_availabilities_for_campsite(park, campsite_details, list_days_to_include):
    availabilities = []
    campground_available_status = "Available"
    if campsite_details["campsite_type"] == "STANDARD NONELECTRIC":
        for time, reservation_status in campsite_details["availabilities"].items():
            if reservation_status == campground_available_status:
                url = BASE_URL + CAMPSTIES_URL + campsite_details["campsite_id"]
                date = datetime.strptime(time, "%Y-%m-%dT%H:%M:%SZ")
                date_string = datetime.strftime(date, "%Y-%m-%d (%A)")
                if date.weekday() in list_days_to_include:
                    availabilities.append((park, date_string, url))
    return availabilities

def get_campground_availabilities(campground_id, start_time, end_time):
    start_of_day_time = "T00:00:00.000Z"

    response = requests.get(
        BASE_URL + CAMPGROUND_AVAILABILITY + campground_id,
        params={
            "start_date": start_time + start_of_day_time,
            "end_date": end_time + start_of_day_time,
        },
        headers={
            "authority": "www.recreation.gov",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_4) \
                AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/75.0.3770.100 Safari/537.36",
        },
    )
    return response.json()


# def send_twilio(message_body):
#     account_sid = TWILIO_ACCOUNT_SID
#     auth_token = TWILIO_AUTH_TOKEN
#     client = Client(account_sid, auth_token)

#     client.messages.create(
#         to=TWILIO_TO_NUM,
#         from_=TWILIO_FROM_NUM,
#         body=message_body,
#     )


def send_email(message_body):
    gmail_server = "smtp.gmail.com"
    gmail_port = 465

    subject = "Yosemite Campground Availabilites Found"
    message = f"Subject: {subject}\n\n{message_body}"

    server = smtplib.SMTP_SSL(gmail_server, gmail_port)
    server.login(GMAIL_ACCOUNT, GMAIL_PASSWORD)
    server.sendmail(GMAIL_ACCOUNT, GMAIL_ACCOUNT, message)
    server.quit()


def lambda_handler(event, _):
    campsites = get_available_campsites(START_DATE, END_DATE, LIST_DAYS_TO_INCLUDE)
    message_body = ""

    if campsites:
        for campsite in campsites:
            message_body += f"\n{campsite[0]}, Booking URL: \
                {campsite[2]}, available on {campsite[1]}.\n"

        # Comment out whichever notification mechanism you want disabled
        # send_twilio(message_body)
        send_email(message_body)

    return message_body
