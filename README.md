# Yosemite Campsite Availability
This is a simple script to notify when a yosemite campsite is available to book. Support logging list of campsite availabilities to a csv, and email/SMS notifications.

# Instructions
Install requirements:
```
pip install -r requirements.txt
```

Notes: Fill out campsites.ini with your Gmail and Twilio details if you plan on using the email and/or text notification features.
Otherwise, comment out ```send_twilio(MESSAGE_BODY)``` and/or ```send_gmail(MESSAGE_BODY)``` respectively in campsites.py.

Basic Usage: `python3 campsites.py --start_date 2019-07-04 --end_date 2019-09-04 --days-to-include 4,5,6`

Use on AWS Lambda:

1. pip install all requirements locally inside this folder. Click [here](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html) for more details.
2. package up the folder as a zip file
3. Setup a new lambda function on aws and upload your python zip.
4. Fill out appropriate os environment variables such as email username/password.
5. Setup CloudWatch Events to create a cron job to your lambda function every X minutes


## Initial Inspiration
https://github.com/bri-bri/yosemite-camping
