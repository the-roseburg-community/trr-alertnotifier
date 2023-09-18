# Author: Joseph Ziegler
#

import os
import requests # pip

PASSWORD = os.getenv('PASSWORD')
USERNAME = os.getenv('USERNAME')

api_url = "https://api.broadcastify.com/owner/"

try:
  with open('feeds.txt', 'r') as file:
    for line in file:
      feed = line.strip().split()
      if len(feed) >= 2:
        feed_id = int(feed[0])
        emails = feed[1:]

        full_feed_url = api_url + "?a=feed&feedId=" + str(feed_id) + "&type=json&u=" + USERNAME + "&p=" + PASSWORD
        payload={}
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


          print("Feed Name: %s, %s County - %s" % (feed_name,county_name,county_state))
          print("Listeners: %d" % listeners)
        else:
          print("Failed to retrieve data from the API. Status code:", response.status_code)

      else:
        print("Invalid line:", line)
except Exception as error:
  print(error)

