# Yosemite Campsite Availability
This is a simple script to log list of campsite availabilities to a csv

# Instructions
Install requirements:
```
pip install -r requirements.txt
```

Notes: Fill out campsites.ini with your Gmail and Twilio details if you plan on using the email and/or text notification features.
Otherwise, comment out ```send_twilio(MESSAGE_BODY)``` and/or ```send_gmail(MESSAGE_BODY)``` respectively in campsites.py.

Usage: `python3 campsites.py --start_date 2019-07-04 --end_date 2019-09-04 --days-to-include 4,5,6`

## Initial Inspiration
https://github.com/bri-bri/yosemite-camping
