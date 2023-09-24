# Author: Joseph Ziegler
# Email: joseph@josephziegler.com
# Description:
#   This python application sends email-based text messages to all numbers listed in the numbers.txt file if
#   a specific feed on Broadcastify contains an alert that belongs to the account owner of the credentials used.

import os
import requests                # Install with pip
from mailersend import emails  # Install with pip

from_address = "noreply@roseburg.city"

PASSWORD = os.getenv('PASSWORD')                        # Environment variable for Broadcastify feed owner password
USERNAME = os.getenv('USERNAME')                        # Environment variable for Broadcastify feed owner username
mailer = emails.NewEmail(os.getenv('MAILSEND_API_KEY')) # Environment variable for Mailersend API Key
feed_id = "40833"                                       # Broadcastify Feed ID

# Phone carrier dictionary
carrier_mapping = {
  "googlefi": "msg.fi.google.com",
  "verizon": "vtext.com",
  "tmobile": "tmomail.net",
  "att": "txt.att.net",
  "spectrum": "vtext.com",
  "xfinity": "vtext.com",
  "uscellular": "email.uscc.net"
}

api_url = "https://api.broadcastify.com/owner/"

def mail(subject, content):
  mail_body = {}
  try:
    with open('numbers.txt', 'r') as file:
      mail_list = []  # Initialize mail_list
      for line in file:
        number = line.strip().split()
        if len(number) >= 2:  # Make sure that both the number and carrier exist in the text file
          phone_number = int(number[0])
          provider = number[1]
          print(phone_number)
          print(provider)
          if provider in carrier_mapping:
            adjusted_carrier = carrier_mapping[provider]
            email = str(phone_number) + "@" + adjusted_carrier
            print("Email is %s" % email)

            # Create a new email_info dictionary for each email
            email_info = {
              "from": {
                "email": from_address,
                "name": "The Roseburg Receiver"
              },
              "to": [
                {
                  "email": email,
                  "name": "TRR Member"
                }
              ],
              "subject": subject,
              "text": content,
            }

            mail_list.append(email_info)
        else:
          print("Invalid line:", line)
    print(mail_list)
    # print(mailer.send_bulk(mail_list))  # Send Email
  except Exception as e:
    print(e)


## Script start
state_file_path = "previous_state.txt" # Use a state file in order to understand if the alert already sent a text or if the alert message has changed.
try:
  with open(state_file_path, "r") as state_file:
    previous_state = state_file.read().strip()
except FileNotFoundError:
  print("Creating state file")
  previous_state = None

try:
  full_feed_url = api_url + "?a=feed&feedId=" + str(feed_id) + "&type=json&u=" + USERNAME + "&p=" + PASSWORD
  payload = {}
  headers = {}
  response = requests.request("GET", full_feed_url, headers=headers, data=payload)
  if response.status_code == 200:
    data = response.json()

    content = data["Feed"][0]

    counties = content["Counties"]
    county_info = counties[0]

    feed_name = content["descr"]
    listeners = content["listeners"]
    county_name = county_info['name']
    county_state = county_info["stateName"]

    if int(listeners) > 40:  # If there is an alert
      #current_value = data["specific_field"] # Data for the alert message
      #if previous_state is None or previous_state != current_value:
        print("%s %s" % (feed_name, str(listeners)))
        mail("Feed " + feed_name + " has an alert!", "Feed " + feed_name + " has an alert! It also has " + str(listeners) + " listeners. This is a TEST ONLY. This is not a real alert.")
        print("Feed Name: %s, %s County - %s" % (feed_name, county_name, county_state))
        print("Listeners: %d" % listeners)

        # Save the updated state to the file
        with open(state_file_path, "w") as state_file:
          state_file.write(str(current_value))
  else:
    print("Failed to retrieve data from the API. Status code:",
      response.status_code)
except Exception as error:
  print(error)


