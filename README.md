# Broadcastify SMS Notifier
Send emails when a specific Broadcastify feed is an alerting (you must be the owner of the feed)

Although this mentions SMS, this script uses the email-based SMS messaging that most mobile carriers provide.

## To Use
Update the env file with your Broadcastify username and password.
Emails are handled by an email service. MailerSend is used in this script (mailersend.com). Get an API token from this service and add it to the env file as well.

## Docker
To run, simply build the container and then run it:

1. `docker build -t notifier .`
2. `docker run --rm -v $PWD:/app --env-file env feed`
