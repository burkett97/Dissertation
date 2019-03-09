#!/usr/bin/env python3

# Jack Burkett- C1616242 Cardiff University

# Modules to import
import re
import os
import time
import pymysql
import pymysql.cursors
import requests, sys
import xml.etree.ElementTree as ET
from datetime import datetime

# System Config
IP = "192.168.8.1"
systemtime = datetime.today().strftime('%Y-%m-%d %-H:%M:%S%z')


# Messages to locator --> Locator V2
Location_Message = "smslink123456"

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
def sendsms(NumbersToSendTo = [], * args):

    timewaited = 30

    token, sessionID = authenticate()
    LengthofLoc = len(Location_Message)
    
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}

    systime = datetime.today().strftime('%Y-%m-%d %-H:%M:%S%z')

    numbers = ""
    
    for number in NumbersToSendTo:
        sms_phone = "<Phone>" + number + "</Phone>"
        numbers = numbers + sms_phone

    SMS = "<request><Index>-1</Index><Phones>" + numbers + "</Phones><Sca/><Content>" + Location_Message + "</Content><Length>" + str(LengthofLoc) + "</Length><Reserved>1</Reserved><Date>" + systime + "</Date></request>"

    send = requests.post("http://" + IP + "/api/sms/send-sms", data=SMS, headers=headers)

    # Once SMS is sent pass number and system time to receivesms to get response
    print("SMS has been sent")
    time.sleep(30)
    print("Looking for reply")
    receivesms(timewaited, systime, NumbersToSendTo)

# Receive messages back
def receivesms(timewaited, systime, NumbersToSendTo = [], * args):

    token, sessionID = authenticate()
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}

    numberofmessages = len(NumbersToSendTo)

    if len(NumbersToSendTo) < 5:
        numberofmessages = 5

    SMSRetrieve="<request><PageIndex>1</PageIndex><ReadCount>" + str(numberofmessages) + "</ReadCount><BoxType>1</BoxType><SortType>0</SortType><Ascending>0</Ascending><UnreadPreferred>1</UnreadPreferred></request>"

    receive = requests.post("http://" + IP + "/api/sms/sms-list", data=SMSRetrieve, headers=headers)
    output = receive.text
    tree = ET.fromstring(output) 
    
    phoneNumbers = list()
    datesofMessages = list()
    contentofMessages = list()

    for phone in tree.iter('Phone'):
        phoneNumbers.append(phone.text)
    for date in tree.iter('Date'):
        datesofMessages.append(date.text)
    for content in tree.iter('Content'):
        contentofMessages.append(content.text)

    i = 0

    print("Time waited " + str(timewaited))
    
    # Iterate through list of phones numbers in received messages. If message in list of sms sent and the date of the message is after 
    if timewaited <= 120:
        while i < len(phoneNumbers):
            # If the number that an sms was sent to is in the list of messages and the date is after the time the message was sent...
            if phoneNumbers[i] in NumbersToSendTo:
                if datesofMessages[i] > systime:
                    # ...get the contents of the message, date and content and pass it through to be formatted
                    p = phoneNumbers[i]
                    d = datesofMessages[i]
                    c = contentofMessages[i]

                    format(p, d, c)
                    messagelog(p, d, c)
                    NumbersToSendTo.remove(p)

                    print("Message found for " + phoneNumbers[i])
            i += 1
        if len(NumbersToSendTo) != 0:
            timewaited += 15
            time.sleep(15)
            receivesms(timewaited, systime, NumbersToSendTo)
        else:
            print("Messages found")
    else:
        # Error message sent to traccar
        print("Message couldn't be found within 2 minutes for: " + ', '.join(NumbersToSendTo))

# Fomat messages
def format(p, d, c):
    # Takes the content of retrieve messages and formats it. This can then be passed to addtodb.
    splitmessage = c.split()

    first = splitmessage[0]

    if first.startswith('last:'):
        # Error message should be sent to traccar to say no GPS signal. 'No GPS Signal- the last known location is: location info"
        print("NO GPS SIGNAL- LAST KNOW LOCATION TO BE ADDED")
        lat = splitmessage[1]
        lat = lat[4:]
        lon = splitmessage[2]
        lon = lon[5:]
        speed = splitmessage[3]
        speed = speed[6:]
        date = splitmessage[4]
        date = date[2:]
        time = splitmessage[5]
        date = datetime.strptime(date, "%m/%d/%y").strftime("%Y-%m-%d")
        devdate = date + " " + time
        if len(splitmessage) > 7:
            battery = splitmessage[13]
        addtodb(p, d, lat, lon, speed, devdate, battery)

    elif first.startswith('lat:'):
        print("GPS SIGNAL")
        lat = splitmessage[0]
        lat = lat[4:]
        lon = splitmessage[1]
        lon = lon[5:]
        speed = splitmessage[2]
        speed = speed[6:]
        date = splitmessage[3]
        date = date[2:]
        time = splitmessage[4]
        date = datetime.strptime(date, "%m/%d/%y").strftime("%Y-%m-%d")
        devdate = date + " " + time
        if len(splitmessage) > 6:
            battery = splitmessage[7]
        addtodb(p, d, lat, lon, speed, devdate, battery)

# Add the location info to the database
def addtodb(phone, messdate, lat, lon, speed, devdate, battery):
    # Connects to the database and tc_positions table and checks
    host = 'localhost'
    user = 'jack'
    password = 'somepassword'
    port = 3306
    db = 'traccar'
    
    conn = pymysql.connect(host=host, user=user,password=password,port=port, db=db, cursorclass=pymysql.cursors.DictCursor)

    # devdate = '2019-03-09 14:31:00'
    # messdate = '2019-03-09 14:30:00'
    # lat = '51.48802'
    # lon = '-3.17283'
    # speed = float(speed)
    devdate = str(devdate)
    messdate = str(messdate)
    lat = str(lat)
    lon = str(lon)
    speed = float(speed)
    
    try: 
        with conn.cursor() as cursor:
            sql = "INSERT INTO tc_positions (protocol, deviceid, devicetime, fixtime, valid, latitude, longitude, altitude, speed, course) VALUES ('sms', 2, %s, %s, 1, %s, %s, 0, %s, 0)"
            cursor.execute(sql,(devdate, messdate, lat, lon, speed))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

    # INSERT INTO tc_positions (protocol, deviceid, devicetime, fixtime, valid, latitude, longitude, altitude, speed, course) VALUES ('sms', 2, '2019-03-09 14:31:00', '2019-03-09 14:31:00', 1, 0, 0, 5, 0, 0);

# Log every message received
def messagelog(p, d, c):
    # Every time a sms is sent and the message received, the message and information is logged

    messageid = 0

    c = c.replace('\n', ' ').replace('\r', '')

    # Will make log directory if not there
    try:
        original_umask = os.umask(0)
        os.makedirs('log/', mode= 0o755, exist_ok=False)
    except FileExistsError:
        pass
    finally:
        os.umask(original_umask)

    # Will create file if not there
    if not os.path.exists('log/messagelog.txt'):
        with open('log/messagelog.txt', 'w'):
            pass   
    
    if os.stat("log/messagelog.txt").st_size == 0:
        with open("log/messagelog.txt", "a") as file:
            file.write(str(messageid) + ", " + p + ', ' + d + ', ' + c + ';\n')
    else:
        with open("log/messagelog.txt", "r+") as file:
            last_line = file.readlines()[-1]
            messageid = last_line.split(',')[0]
            messageid =  int(messageid) + 1
        with open("log/messagelog.txt", "a") as file:
            file.write(str(messageid) + ", " + p + ', ' + d + ', ' + c + ';\n')

# Function to delete SMS from modem (not in use at the moment)
def deletesms(index):
    # Once information has been added to database and the message has been logged into file the message can be deleted from modem to save space
    token, sessionID = authenticate()
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}
    
    Delete="<request><Index>" + index + "</Index></request>"

    delete = requests.post("http://" + IP + "/api/sms/delete-sms", data=Delete, headers=headers)
    pass

# NumbersToSendTo = ['+447445819958']
NumbersToSendTo = ['+447498285350']
# NumbersToSendTo = ['+447498285350', '+447445819958']

sendsms(NumbersToSendTo)

# References: 
    # Using inspiration and ideas from code at Reference: https://stackoverflow.com/questions/38016641/sending-and-receiving-sms-by-command-line-with-huawei-e3131-and-hilink-on-a-debi
    # Aswell as from Reference: https://stackoverflow.com/questions/22561947/huawei-api-sms-documentation?rq=1 for retrieving the sessionid and token in python
# Talking point for written: 
    # efficiency of this program as you have to send sms for one number then wait for it to respond, rather than move on to next number
    # will need to address this by putting a main function that for each number that is passed into this it then runs sendsms for each 