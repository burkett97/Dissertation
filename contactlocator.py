#!/usr/bin/env python3

# Jack Burkett- C1616242 Cardiff University

# Modules to import
import re
import time
import requests, sys
import xml.etree.ElementTree as ET
from datetime import datetime

# System Config
IP = "192.168.8.1"
systime = datetime.today().strftime('%Y-%m-%d %-H:%M:%S%z')

# Messages to locator --> Locator V2
Location_Message = "smslink123456"
# Status_Message = "Check123456"

# Get sessionid
def authenticate():
    url = ("http://" + IP + "/html/index.html")
    request = requests.get(url)
    
    # Access cookie and retrieve sessionID
    setcookie = request.headers.get('set-cookie')
    sessionID = setcookie.split(';')[0]        
    
    # Get token
    token =  re.findall(r'"([^"]*)"', request.text)[2]
    return token, sessionID

# Sends SMS to locator
def sendsms(number):
    token, sessionID = authenticate()
    LengthofLoc = len(Location_Message)
    # LengthofStat = len(Status_Message)
    
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}

    SMS = "<request><Index>-1</Index><Phones><Phone>+" + str(number) + "</Phone></Phones><Sca/><Content>" + Location_Message + "</Content><Length>" + str(LengthofLoc) + "</Length><Reserved>1</Reserved><Date>" + systime + "</Date></request>"

    send = requests.post("http://" + IP + "/api/sms/send-sms", data=SMS, headers=headers)

    # return the time the message was sent
    return systime

# Receive last 5 messages sent back

def receivesms(number):

    time.sleep(30)
    token, sessionID = authenticate()
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}

    SMSRetrieve="<request><PageIndex>1</PageIndex><ReadCount>5</ReadCount><BoxType>1</BoxType><SortType>0</SortType><Ascending>0</Ascending><UnreadPreferred>1</UnreadPreferred></request>"

    receive = requests.post("http://" + IP + "/api/sms/sms-list", data=SMSRetrieve, headers=headers)

    output = receive.text
    print(output)

    # Keep track of time as if over 2 mins then return an error
    # XML handler: look at <messages> then the Time on the 1st message --> if less than systime then no message has been received --> wait 15 seconds
        # If time on 1st message is later than systime then look at number in phone and see if it matches one sent to sms
            # If it matches look at content as can assume (based on time frame) this is the relevant message, format content and pass to add to database
            # If it doesn't match wait another 15 seconds and repeat


    # wait for 30 seconds 
    # retrieve the messages in XML
    # Look for most recent message from number and time.
    # If time is after the systime when message is sent (i.e. last message from that number) then retrieve the contents of that message and format
    # If the message isn't there yet (i.e. locator hasn't responded yet) then wait another 20 seconds and retrieve the messages again


def format():
    # Takes the content of retrieve messages and formats it and adds the relevant information. This can then be passed to addtodb.
    pass

def addtodb():
    # This will take relevant information from the received message 
    pass

def messagelog():
    # Every time a set of 5 messages are retrieved the are stored into a log file. Each text is assigned a unique id and this id is checked when added to log to ensure there are no duplicates.
    pass 

def deletesms(index):
    # Once information has been added to database and the message has been logged into file the message can be deleted from modem to save space
    token, sessionID = authenticate()
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}
    
    Delete="<request><Index>" + index + "</Index></request>"

    delete = requests.post("http://" + IP + "/api/sms/delete-sms", data=Delete, headers=headers)
    pass
sendsms(+447498285350)
receivesms(+447498285350)





# Using inspiration and ideas from code at Reference: https://stackoverflow.com/questions/38016641/sending-and-receiving-sms-by-command-line-with-huawei-e3131-and-hilink-on-a-debi
# Aswell as from Reference: https://stackoverflow.com/questions/22561947/huawei-api-sms-documentation?rq=1 for retrieving the sessionid and token in python


# Talking point: efficiency of this program as you have to send sms for one number then wait for it to respond, rather than move on to next number
# will need to address this by putting a main function that for each number that is passed into this it then runs sendsms for each 