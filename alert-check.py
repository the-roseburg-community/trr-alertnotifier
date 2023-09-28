# Author: Joseph Ziegler
# Email: joseph@josephziegler.com
# Description:
#   This python application sends email-based text messages to all numbers listed in the numbers.txt file if
#   a specific feed on Broadcastify contains an alert that belongs to the account owner of the credentials used.

import os
import requests                # Install with pip
from mailersend import emails  # Install with pip
from bs4 import BeautifulSoup  # Install with pip
import re

from_address = "noreply@roseburg.city"

PASSWORD = os.getenv('PASSWORD')                        # Environment variable for Broadcastify feed owner password
USERNAME = os.getenv('USERNAME')                        # Environment variable for Broadcastify feed owner username
mailer = emails.NewEmail(os.getenv('MAILSEND_API_KEY')) # Environment variable for Mailersend API Key
feed_id = "40833"                                       # Broadcastify Feed ID

web_url = "https://www.broadcastify.com/listen/feed/" + feed_id

# Phone carrier dictionary
carrier_mapping = {
  "att": "txt.att.net",
  "boostmobile": "sms.myboostmobile.com",
  "consumercellular": "mailmymobile.net",
  "cricketwireless": "sms.cricketwireless.net",
  "googlefi": "msg.fi.google.com",
  "metropcs": "mymetropcs.com",
  "spectrum": "vtext.com",
  "tmobile": "tmomail.net",
  "uscellular": "email.uscc.net",
  "verizon": "vtext.com",
  "xfinity": "vtext.com"
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
          if provider in carrier_mapping:
            adjusted_carrier = carrier_mapping[provider]
            email = str(phone_number) + "@" + adjusted_carrier

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
    #print(mail_list)
    print(mailer.send_bulk(mail_list))  # Send Email
  except Exception as e:
    print(e)


## Script start
state_file_path = "previous_state.txt" # Use a state file in order to understand if the alert already sent a text or if the alert message has changed.
try:
  with open(state_file_path, "r") as state_file:
    previous_state = state_file.read().strip()
    #print("previous state is %s" % previous_state) # For debugging
except FileNotFoundError:
  print("No state file")
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

    feed_name = content["descr"]            # Not calling this anywhere but here if needed
    listeners = content["listeners"]        # Not calling this anywhere but here if needed
    county_name = county_info['name']       # Not calling this anywhere but here if needed
    county_state = county_info["stateName"] # Not calling this anywhere but here if needed

    # Because the API will not return information about an alert (according to support), just do a basic web get request
    website_response = requests.get(web_url) # Fetch the data from the Broadcastify feed
    if website_response.status_code == 200:
      # Parse the HTML content of the page
      soup = BeautifulSoup(website_response.text, 'html.parser')

      # Find the div with class "messageBox"
      message_box = soup.find('div', class_='messageBox')
      if message_box:
        current_value = message_box.get_text(separator=' ')

        # Remove the "(x minutes ago)" part using regular expressions
        current_value = re.sub(r'\(\d+ minutes ago\)', '', current_value).strip()
        # Replace newline characters with spaces
        current_value = current_value.replace('\n', ' ').replace('\r', '')

        # If the div with class "messageBox" is found, print its contents
        if previous_state is None or previous_state != current_value: # Only send text if the message is recent.
          print("The Roseburg Receiver - Feed %s | %s County, %s has an alert! Alert: %s" % (feed_name, county_name, county_state, current_value))
          #mail("The Roseburg Receiver", "The Roseburg Receiver - " + feed_name + " | " + county_name + " County, " + county_state + " has an alert! Alert: " + current_value)
          mail("The Roseburg Receiver", "Alert " + current_value)
          # Save the updated state to the file
          with open(state_file_path, "w") as state_file:
            state_file.write(str(current_value))
        else:
          print("Alert is already in state file")
      else:
        # If the div is not found, print "No messages"
        print("No messages")
    else:
      # If the GET request was not successful, print an error message
      print("Failed to retrieve the website content")
  else:
    print("Failed to retrieve data from the API. Status code:",
      response.status_code)
except Exception as error:
  print(error)


