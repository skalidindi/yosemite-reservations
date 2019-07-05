# Yosemite Campsite Availability

## How to Use

Run this function on AWS Lambda

Note that some env variables need to be set for this to work. Example below.

- DAYS_TO_INCLUDE=5,6
- START_DATE=2022-04-01
- END_DATE=2022-08-30
- TWILIO_ACCOUNT_SID=XXXXXX
- TWILIO_AUTH_TOKEN=XXXXXXX
- TWILIO_FROM_NUMBER=XXXXXX
- TWILIO_TO_NUMBER=XXXXXXXX

You can set up an AWS Cloud Watch Event to run this function on some regular cadence.

## Local Testing

Follow https://docs.aws.amazon.com/lambda/latest/dg/images-test.html

Note: You will need to still set the env variables mentioned above. You could pass them directly from the docker run command.

## Deployment to AWS Lambda

You can fork this codebase and add your own secrets to automatically deploy to aws lambda.
Otherwise, simply run the aws console to manually push an image ECR and deploy to your lambda function.
