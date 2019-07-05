#!/usr/bin/env python
"""Find campground availabilities for Yosemite
Example usaage: python3 campsites.py --start_date 2019-07-04 --end_date 2019-09-04 --days-to-include 4,5,6
"""
from datetime import datetime, timedelta
import configparser
import smtplib
import csv
import argparse
import requests
from twilio.rest import Client

PARKS = {
    "232447": "UPPER PINES",
    "232450": "LOWER PINES",
    "232449": "NORTH PINES",
    "232448": "TUOLOMNE MEADOWS",
    "232446": "Wawona",
}


BASE_URL = "https://www.recreation.gov"
CAMPGROUND_AVAILABILITY = "/api/camps/availability/campground/"
CAMPSTIES_URL = "/camping/campsites/"

config = configparser.ConfigParser()
config.read("campsites.ini")


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


def get_next_day(date):
    date_object = datetime.strptime(date, "%Y-%m-%d")
    next_day = date_object + timedelta(days=1)
    return datetime.strftime(next_day, "%Y-%m-%d")


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


def save_results_to_file(start_date, end_date, campsites):
    results_file = f"results/results_{start_date}_{end_date}.csv"
    with open(results_file, "w") as out:
        csv_out = csv.writer(out)
        csv_out.writerow(["park", "date", "url"])
        for campsite in campsites:
            csv_out.writerow(campsite)


def send_twilio(message_body):
    account_sid = config["TWILIO"]["AccountSid"]
    auth_token = config["TWILIO"]["AuthToken"]
    client = Client(account_sid, auth_token)

    client.messages.create(
        to=config["TWILIO"]["ToNumber"], from_=config["TWILIO"]["FromNumber"], body=message_body
    )


def send_email(message_body):
    gmail_server = "smtp.gmail.com"
    gmail_port = 465
    gmail_user = config["GMAIL"]["GmailAccount"]
    gmail_password = config["GMAIL"]["GmailPassword"]
    sent_from = gmail_user
    to = gmail_user

    subject = "Yosemite Campground Availabilites Found"
    message = f"Subject: {subject}\n\n{message_body}"

    server = smtplib.SMTP_SSL(gmail_server, gmail_port)
    server.login(gmail_user, gmail_password)
    server.sendmail(sent_from, to, message)
    server.quit()


if __name__ == "__main__":
    PARSER = argparse.ArgumentParser()

    PARSER.add_argument(
        "--start_date", required=True, type=str, help="Start date [YYYY-MM-DD]"
    )
    PARSER.add_argument("--end_date", type=str, help="End date [YYYY-MM-DD]")

    PARSER.add_argument(
        "--days-to-include",
        required=True,
        type=str,
        help="Comma seperated string of days of week to include from 0-6 [0,1,2,3,4,5,6]",
    )

    ARGS = PARSER.parse_args()
    ARG_DICT = vars(ARGS)
    LIST_DAYS_TO_INCLUDE = [int(x) for x in ARG_DICT["days_to_include"].split(",")]
    if "end_date" not in ARG_DICT or not ARG_DICT["end_date"]:
        ARG_DICT["end_date"] = get_next_day(ARG_DICT["start_date"])

    CAMPSITES = get_available_campsites(
        ARG_DICT["start_date"], ARG_DICT["end_date"], LIST_DAYS_TO_INCLUDE
    )

    if CAMPSITES:
        MESSAGE_BODY = ""
        for campsite in CAMPSITES:
            MESSAGE_BODY += f"\n{campsite[0]}, Booking URL: {campsite[2]}, available on {campsite[1]}.\n"

        # Comment out whichever notification mechanism you want disabled
        send_twilio(MESSAGE_BODY)
        send_email(MESSAGE_BODY)
        save_results_to_file(ARG_DICT["start_date"], ARG_DICT["end_date"], CAMPSITES)
