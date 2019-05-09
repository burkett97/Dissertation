#!/usr/bin/env python3

# Jack Burkett- Cardiff University

# Modules to import
import re
import sys
import os
import time
import json
import pymysql
import pymysql.cursors
import requests, sys
import xml.etree.ElementTree as ET
from datetime import datetime
from datetime import timedelta

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flaskext.mysql import MySQL
from flask_sqlalchemy import SQLAlchemy

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor

# System Config
IP = "192.168.8.1"
systemtime = datetime.today().strftime('%Y-%m-%d %-H:%M:%S%z')

# Config for Apscheduler
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': False,
    'max_instances': 2000 
}

scheduler = BackgroundScheduler(executors=executors, job_defaults=job_defaults)

# For running job store from MYSQL so rules don't need to be reinitialised --> problems with removing jobs though
# url = 'mysql+pymysql://jack:somepassword@localhost/traccar'
# scheduler.add_jobstore('sqlalchemy', alias='default',url=url)

scheduler.start()

# Messages to locator --> Locator V2
Location_Message = "smslink123456"

# Config for Flask- MYSQL
app = Flask(__name__)
CORS(app)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'jack'
app.config['MYSQL_DATABASE_PASSWORD'] = 'somepassword'
app.config['MYSQL_DATABASE_DB'] = 'traccar'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

# Function for locating a single locator from Active devices view
@app.route('/locate/<phonenumber>/<phoneid>')
def singlelocate(phonenumber, phoneid):
    # Put phone id and phone number into a list
    NumbersToSendTo = list()
    phone_id = list ()
    NumbersToSendTo.append(phonenumber)
    phone_id.append(phoneid)
    sendsms(phone_id, NumbersToSendTo)
    return "Single locate complete"

# Function for locating a group of locations from Group view
@app.route('/grouplocate/<groupid>') 
def grouplocate(groupid):
    # Connect to tc_devices databases retrieve ids and numbers of locators
    conn = mysql.connect()
    cursor = conn.cursor()

    sql = "SELECT id, phone FROM tc_devices WHERE groupid = %s"
    cursor.execute(sql,(groupid))
    rows = cursor.fetchall()

    # Put the phone ids and numbers into lists
    Phoneids = list()
    NumbersToSendTo = list()

    for i in rows:
        phoneid = i[0]
        phonenumber = i[1]

        Phoneids.append(phoneid)
        NumbersToSendTo.append(phonenumber)
    
    sendsms(Phoneids, NumbersToSendTo)
    return "Group locate complete"

# Get sessionid and session token
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
def sendsms(phoneid, NumbersToSendTo):

    # Print scheduled jobs everytime sendsms is run
    scheduler.print_jobs()
    timewaited = 30

    # Clear outbox messages if 50 messages have been sent
    if sendsms.counter % 50 == 0:
        clearoutbox()

    # Get session id and token from authenticate
    token, sessionID = authenticate()
    LengthofLoc = len(Location_Message)
    
    # Add them to headers
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}

    # Get system time which will be used for date message is sent
    systime = datetime.today().strftime('%Y-%m-%d %T')

    numbers = ""
    
    # Iterate through the list of numbers and concatenate them as <Phone>Number</Phone> in order to add them to request
    for number in NumbersToSendTo:
        sms_phone = "<Phone>" + str(number) + "</Phone>"
        numbers = numbers + sms_phone

    SMS = "<request><Index>-1</Index><Phones>" + numbers + "</Phones><Sca/><Content>" + Location_Message + "</Content><Length>" + str(LengthofLoc) + "</Length><Reserved>1</Reserved><Date>" + systime + "</Date></request>"
    sendsms.counter += 1
    print(sendsms.counter)
    # Post request enables SMS to be sent
    send = requests.post("http://" + IP + "/api/sms/send-sms", data=SMS, headers=headers)

    # Once SMS is sent pass number and system time to receivesms to get response
    print("SMS has been sent")
    time.sleep(30)
    print("Looking for reply")
    receivesms(phoneid, timewaited, systime, NumbersToSendTo)
    return "Sent"

# Receive messages back
def receivesms(phoneid, timewaited, systime, NumbersToSendTo):

    # Get session id and token from authenticate and add to headers
    token, sessionID = authenticate()
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}

    # Number of messages is set to amount of numbers SMS messages were sent to
    # If amount if less than 5 set the default to 5
    numberofmessages = len(NumbersToSendTo)
    if len(NumbersToSendTo) < 5:
        numberofmessages = 5

    # Retrieve the messages
    SMSRetrieve="<request><PageIndex>1</PageIndex><ReadCount>" + str(numberofmessages) + "</ReadCount><BoxType>1</BoxType><SortType>0</SortType><Ascending>0</Ascending><UnreadPreferred>1</UnreadPreferred></request>"

    receive = requests.post("http://" + IP + "/api/sms/sms-list", data=SMSRetrieve, headers=headers)
    
    # Parse the XML format
    output = receive.text
    tree = ET.fromstring(output) 

    # Put the message ids, phone numbers, dates of messages and content of messages from inbox into lists
    messageid = list()
    inboxphoneNumbers = list()
    datesofMessages = list()
    contentofMessages = list()

    for ID in tree.iter('Index'):
        messageid.append(ID.text)
    for phone in tree.iter('Phone'):
        inboxphoneNumbers.append(phone.text)
    for date in tree.iter('Date'):
        datesofMessages.append(date.text)
    for content in tree.iter('Content'):
        contentofMessages.append(content.text)

    print("Time waited " + str(timewaited))

    phoneids = phoneid
    numbers = NumbersToSendTo
    
    # Checks Max wait time of 120 seconds hasn't been reached
    if timewaited <= 120:
        i = 0
        # Checks if all the locators have responded
        while i < len(inboxphoneNumbers):
            # Checks if number is in inbox and if so the message was received after the message was sent
            if inboxphoneNumbers[i] in NumbersToSendTo:
                if datesofMessages[i] > systime:
                    # Get the message id, content of the message and date 
                    p = inboxphoneNumbers[i]
                    d = datesofMessages[i]
                    c = contentofMessages[i]
                    mess_id = messageid[i]

                    idindex = NumbersToSendTo.index(p)
                    phone_id = phoneids[idindex]

                    # Send info to be formatted before being added to db
                    format(phone_id, p, d, c)
                    # Log message
                    messagelog(systime, p, d, c)
                    # Remove number and id from list as message for number has been found
                    numbers.remove(p)
                    phoneids.remove(phone_id)
                    # Delete the message from the Modem
                    deletesms(mess_id)

                    print("Message found for " + inboxphoneNumbers[i])
            i += 1
        if len(numbers) != 0:
            # If message isn't found and locators are still waiting for responses, wait 15 seconds then check again
            timewaited += 15
            time.sleep(15)
            receivesms(phoneids, timewaited, systime, numbers)
        else:
            print("Messages found")
    else:
        # If message not found print message --> Future work: outputs to Traccar web application
        print("Message couldn't be found within 2 minutes for: " + ', '.join(numbers))
        if receivesms.counter % 50 == 0:
            clearinbox()
        receivesms.counter += 1

    return "Received"

# Log every message received
def messagelog(systime, p, d, c):

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
    # If file is empty start message id from 0 and add info
    if os.stat("log/messagelog.txt").st_size == 0:
        with open("log/messagelog.txt", "a") as file:
            file.write(str(messageid) + ", " + systime + ", " + p + ', ' + d + ', ' + c + ';\n')
    # Else retrieve id from last line of message log, increment then add info
    else:
        with open("log/messagelog.txt", "r+") as file:
            last_line = file.readlines()[-1]
            messageid = last_line.split(',')[0]
            messageid =  int(messageid) + 1
        with open("log/messagelog.txt", "a") as file:
            file.write(str(messageid) + ", " + systime + ", " + p + ', ' + d + ', ' + c + ';\n')

    return "Logged"

# Fomat messages
def format(phoneid, p, d, c):
    # Split message and retrieve info from it and place into variables
    splitmessage = c.split()
    first = splitmessage[0]

    # Last location response from locator
    if first.startswith('last:'):
        print("NO GPS SIGNAL- LAST KNOW LOCATION TO BE ADDED")
        valid = 0
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
        battery = ''
        if len(splitmessage) > 7:
            battery = splitmessage[13]
            battery = battery.replace('%', '')
        addtodb(phoneid, p, d, lat, lon, speed, devdate, battery, valid)

    # Current location response from locator
    elif first.startswith('lat:'):
        print("GPS SIGNAL")
        valid = 1
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
        battery = ''
        if len(splitmessage) > 6:
            battery = splitmessage[7]
            battery = battery.replace('%', '')
        addtodb(phoneid, p, d, lat, lon, speed, devdate, battery, valid)

    return "Formatted"

# Add the location info to the database
def addtodb(phoneid, phone, messdate, lat, lon, speed, devdate, battery, valid):

    print("Location data added to db")

    # Connect to database and insert data for locator into tc_positions table
    conn = mysql.connect()

    devdate = str(devdate)
    messdate = str(messdate)
    lat = str(lat)
    lon = str(lon)
    speed = float(speed)
    
    if battery == '':
        battery = 0
    else:
        battery = int(battery)

    cursor = conn.cursor()
    
    try: 
        sql = "INSERT INTO tc_positions (protocol, deviceid, devicetime, fixtime, valid, latitude, longitude, altitude, speed, course) VALUES ('sms', %s, %s, %s, %s, %s, %s, 0, %s, 0)"
        cursor.execute(sql,(phoneid, devdate, messdate, valid, lat, lon, speed))
        conn.commit()

        # Retrieve the id of the position just added
        sql1 = "SELECT id FROM tc_positions ORDER BY id DESC LIMIT 1"
        cursor.execute(sql1)
        rows = cursor.fetchone()
        positionid = rows[0]

        print(positionid)

        sql2 = "UPDATE tc_devices SET lastupdate = %s, positionid = %s, battery = %s WHERE id = %s"
        cursor.execute(sql2,(devdate, positionid, battery, phoneid))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

    return "Added to DB"

# Delete SMS from modem once message has been logged
def deletesms(index):
    token, sessionID = authenticate()
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}
    
    Delete="<request><Index>" + index + "</Index></request>"

    delete = requests.post("http://" + IP + "/api/sms/delete-sms", data=Delete, headers=headers)
    
    return "Message deleted"

# Delete outbox messages 
def clearoutbox():
    
    print("Outbox messages deleted")
    token, sessionID = authenticate()
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}
        
    numberofmessages = 50

    # Retrieve the messages
    SMSRetrieve="<request><PageIndex>1</PageIndex><ReadCount>" + str(numberofmessages) + "</ReadCount><BoxType>2</BoxType><SortType>0</SortType><Ascending>0</Ascending><UnreadPreferred>1</UnreadPreferred></request>"

    receive = requests.post("http://" + IP + "/api/sms/sms-list", data=SMSRetrieve, headers=headers)
    output = receive.text
    tree = ET.fromstring(output) 

    for ID in tree.iter('Index'):
    
        token, sessionID = authenticate()
        headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}
        
        Delete="<request><Index>" + str(ID) + "</Index></request>"

        delete = requests.post("http://" + IP + "/api/sms/delete-sms", data=Delete, headers=headers)

    return output

# Delete inbox messages- removes old messages that weren't found within 2 minutes 
def clearinbox():
    
    print("Inbox messages deleted")
    token, sessionID = authenticate()
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}
        
    numberofmessages = 50

    # Retrieve the messages
    SMSRetrieve="<request><PageIndex>1</PageIndex><ReadCount>" + str(numberofmessages) + "</ReadCount><BoxType>1</BoxType><SortType>0</SortType><Ascending>0</Ascending><UnreadPreferred>1</UnreadPreferred></request>"

    receive = requests.post("http://" + IP + "/api/sms/sms-list", data=SMSRetrieve, headers=headers)
    
    output = receive.text
    tree = ET.fromstring(output) 

    messageid = list()
    datesofMessages = list()

    for ID in tree.iter('Index'):
        messageid.append(ID.text)
    for date in tree.iter('Date'):
        datesofMessages.append(date.text)

    deletedate = datetime.now() - timedelta(minutes=4)

    i = 0
    for date in datesofMessages:
        if datetime.strptime(date, '%Y-%m-%d %H:%M:%S') < deletedate:
            index = messageid[i]
            token, sessionID = authenticate()
            headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}
    
            Delete="<request><Index>" + index + "</Index></request>"

            delete = requests.post("http://" + IP + "/api/sms/delete-sms", data=Delete, headers=headers)
        i += 1
    return output

# Function to add schedule rules to database
@app.route('/scheduleadd/<userid>/<schedulename>/<device>/<group>/<period>/<timing>/<starting>/<ending>/<disabled>')
def scheduleadd(userid, schedulename, device, group, period, timing, starting, ending, disabled):
    
    scheduleid = request.args.get('scheduleid')
    scheduleid = int(scheduleid)

    # Format starting and ending data
    starting = starting.replace('_', " ")
    starting = starting + ":00"
    ending = ending.replace('_', " ")
    ending = ending + ":00"

    # Convert booleans to 0 and 1
    if disabled == 'false':
        disabled = 0
    else:
        disabled = 1

    timehour = False
    # If select hour is chosen remove date 
    if len(timing) > 28:
        timehour = True
        timing = timing.split(" ")
        timing = timing[4][:-3]
    
    # If Custom (Window) option selected make fromtill boolean = True
    fromtill = False
    if len(timing) > 14 and timehour == False:
        fromtill = True

    conn = mysql.connect()
    cursor = conn.cursor()
    
    # If schedule already exists
    if scheduleid > 0:
        try: 
            # Update schedule in tc_schedules with new data
            sql = "UPDATE tc_schedules SET name = %s, devices = %s, groups = %s, period = %s, timing = %s, startTime = %s, endTime = %s, disabled = %s WHERE id = %s"
            cursor.execute(sql,(schedulename, device, group, period, timing, starting, ending, disabled, scheduleid))
            conn.commit()
        except:
            conn.rollback()
        finally:
            conn.close()
    
        if device == 'null' and group == 'null':
            try:
                endschedulerule(scheduleid, fromtill)
            except:
                pass
        # If rule has been disabled remove schedule
        elif disabled == 1:
            try:
                endschedulerule(scheduleid, fromtill)
            except:
                pass
        # If schedule rule is enabled remove previous schedule and create new one 
        elif disabled == 0:
            endschedulerule(scheduleid, fromtill)
            createschedulerule(scheduleid, device, group, period, timing, starting, ending)          
    
    else:  
        try: 
            # Insert schedule in tc_schedules
            sql = "INSERT INTO tc_schedules (name, devices, groups, period, timing, startTime, endTime, disabled) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql,(schedulename, device, group, period, timing, starting, ending, disabled))
            conn.commit()

            # Retrieve the id of the schedule just added
            sql1 = "SELECT id FROM tc_schedules WHERE name = %s"
            cursor.execute(sql1,(schedulename))
            rows1 = cursor.fetchone()
            scheduleid = rows1[0]

            # Add id into tc_user_schedule
            sql2 = "INSERT INTO tc_user_schedule (userid, scheduleid) VALUES (%s, %s)"
            cursor.execute(sql2, (userid, scheduleid))
            conn.commit()

        except:
            conn.rollback()
        finally:
            conn.close()
        
        if device == 'null' and group == 'null':
            try:
                endschedulerule(scheduleid, fromtill)
            except:
                pass
        # If rule is disabled remove schedule
        elif disabled == 1:
            try:
                endschedulerule(scheduleid, fromtill)
            except:
                pass
        # If rule is enabled create schedule rule
        elif disabled == 0:
            createschedulerule(scheduleid, device, group, period, timing, starting, ending)         
    
    return device

# Retrieve ids and numbers from database
def getinfo(device, group):
    conn = mysql.connect()
    cursor = conn.cursor()

    devices = device.split(',')
    groups = group.split(',')

    # List of database rows
    info = list()

    # If groups and devices selected retrieve based on id and group id from tc_devices
    if group != "null" and device != "null":
        for d in devices:
            sql = "SELECT id, phone FROM tc_devices WHERE id = %s"
            cursor.execute(sql,(d))
            row = cursor.fetchone()
            try:
                info.append(list(row)) 
            except:
                pass
        for g in groups:
            sql = "SELECT id, phone FROM tc_devices WHERE groupid = %s"
            cursor.execute(sql,(g))
            row = cursor.fetchone()
            try:
                info.append(list(row)) 
            except:
                pass
    # If only device selected, retrieve id and numbers from tc_devices by id 
    elif group == "null":
        for d in devices:
            sql = "SELECT id, phone FROM tc_devices WHERE id = %s"
            cursor.execute(sql,(d))
            row = cursor.fetchone()
            info.append(list(row))  
    # If only group selected, retrieve id and numbers from tc_devices by groupid 
    elif device == "null":
        for g in groups:
            sql = "SELECT id, phone FROM tc_devices WHERE id = %s"
            cursor.execute(sql,(g))
            row = cursor.fetchone()
            info.append(list(row)) 

    # Input data from db into list for ids and numbers
    Phoneids = list()
    NumbersToSendTo = list()

    for i in info:
        phoneid = i[0]
        phonenumber = i[1]

        Phoneids.append(phoneid)
        NumbersToSendTo.append(phonenumber)

    return Phoneids, NumbersToSendTo

# Check to see whether ids and numbers are being sent to Send sms
def infocheck(Phoneids, NumbersToSendTo, device, group):
    # If phoneids and numberstosendto are empty retrieve the information from  getinfo function
    if len(Phoneids) == 0 or len(NumbersToSendTo) == 0:
        Phoneids, NumbersToSendTo = getinfo(device, group)
        sendsms(Phoneids, NumbersToSendTo)
    else:
        sendsms(Phoneids, NumbersToSendTo)

# Function that will create the startschedule rule
def createschedulerule(scheduleid, device, group, period, timing, starting, ending):

    # Get ids and numbers
    Phoneids, NumbersToSendTo = getinfo(device, group)

    # Format start time for cron format
    starting = starting.split(" ")
    date = starting[0]
    time = starting[1].split(":")
    hour = int(time[0])
    minute = int(time[1])

    startruleid = "start_" + str(scheduleid)

    # Create a job that runs the main schedule function, at the start time and passes through all the info as arguments
    scheduler.add_job(startschedulerule, 'cron', args=(scheduleid, Phoneids, NumbersToSendTo, device, group, period, timing, ending), hour=hour, minute=minute , start_date= date, id=startruleid)
    scheduler.print_jobs()

# Function for creating the actual schedule rule that sends the SMS
def startschedulerule(scheduleid, Phoneids, NumbersToSendTo, device, group, period, timing, ending):
    
    # Set the default for all to *
    defaultday = '*'
    defaultweek = '*'
    defaultmonth = '*'
    defaultdow = '*'

    # Formatting for period info into CRON format
    if "every" in period:
        search = re.findall(r'(every)(\d*)([a-z]*)', period)
        value = search[0][1]
        form = search[0][2]
        # Format value depending on whether its x amount of days, weeks or months
        if form == 'days':
            defaultday = "*/" + value
        elif form == 'weeks':
            defaultweek = "*/" + value
        elif form == 'months':
            defaultmonth = "*/" + value
    # If a day is selected for period
    else: 
        dow = period.split(',')
        defaultdow = dow[0][0:3]
        dow.remove(dow[0])
        for day in dow:
            defaultdow = defaultdow + ',' + day[0:3]

    # Set default values for time
    defaultmin = '*'
    defaulthour = '*'
    fromtill = False
    
    everytime = ''
    everymin = False
    
    # Formatting for timing info into CRON format
    if "every" in timing:
        searchtime = re.findall(r'(every)(\d*)([a-z]*)', timing)
        valuetime = searchtime[0][1]
        formtime = searchtime[0][2]
        # Format value depending on whether its x amount of mins or hours
        if formtime == "mins":
            defaultmin = "*/" + valuetime
        elif formtime == "hrs":
            defaulthour = "*/" + valuetime
    # If timing is custom (hour)
    elif len(timing) < 9:
        defaulthour = int(timing[0:2])
        defaultmin = int(timing[3:6])
    # Else timing is custom (window)
    else:
        # Set boolean to indicate its custom (Window) format
        fromtill = True
        searchtime = re.findall(r'(\d*:\d*);(\d*)([a-z]*);(\d*:\d*)', timing)
        # From
        fromtime = searchtime[0][0]
        fromtimesplit = fromtime.split(":")
        defaulthour = fromtimesplit[0]
        defaultmin = fromtimesplit[1]
        # Every:
        valuetime = searchtime[0][1] 
        formtime = searchtime[0][2]
        if formtime == "mins":
            everymin = True
            everytime = "*/" + valuetime
        elif formtime == "hrs":
            everytime = "*/" + valuetime
        # Till:
        tilltime = searchtime[0][3]
        tilltimesplit = tilltime.split(":")
        tillhour = tilltimesplit[0]
        tillmin = tilltimesplit[1]

    # Format end date
    ending = ending.split(" ")
    enddate = ending[0]
    endtime = ending[1].split(":")
    endhour = int(endtime[0])
    endminute = int(endtime[1])

    # Create the id for rules
    scheduleid = str(scheduleid)
    endruleid = "end_" + str(scheduleid)

    # If timing is custom (window) need to call another function that runs it 
    if fromtill == True:
        start_id = "start" + scheduleid + "FT"
        # This will act as the job that runs on the From time
        scheduler.add_job(schedulewindow, 'cron', args=(scheduleid, Phoneids, NumbersToSendTo, device, group, period, defaulthour, defaultmin, everytime, everymin, tillhour, tillmin), hour=defaulthour, minute=defaultmin, id=start_id) # From
        scheduler.add_job(endschedulerule, 'cron', args=(scheduleid, True), hour=endhour, minute=endminute , start_date= enddate, id=endruleid)

    # If timing is not custom (Window) run the send sms based on the schedule
    else:
        scheduler.add_job(infocheck, 'cron', args=(Phoneids, NumbersToSendTo, device, group), hour=defaulthour, minute=defaultmin, day=defaultday, day_of_week=defaultdow, week=defaultweek, month=defaultmonth, id=scheduleid)
        scheduler.add_job(endschedulerule, 'cron', args=(scheduleid, False), hour=endhour, minute=endminute , start_date= enddate, id=endruleid)

    scheduler.print_jobs()

# Function for creating schedule rule when timing = custom (Window)
def schedulewindow(scheduleid, Phoneids, NumbersToSendTo, device, group, period, defaulthour, defaultmin, everytime, everymin, tillhour, tillmin):
    
    # Format the from and til times 
    fromhour = int(defaulthour)
    frommin = int(defaultmin)
    tillhour = int(tillhour)
    tillmin = int(tillmin)

    # Set the values to CRON default
    defaultday = '*'
    defaultweek = '*'
    defaultmonth = '*'
    defaultdow = '*'

    # Format period in the same way as above
    if "every" in period:
        search = re.findall(r'(\d)([a-z]*)', period)
        value = search[0][0]
        form = search[0][1]
        if form == 'days':
            defaultday = "*/" + value
        elif form == 'weeks':
            defaultweek = "*/" + value
        elif form == 'months':
            defaultmonth = "*/" + value
    else: 
        dow = period.split(',')
        defaultdow = dow[0][0:3]
        dow.remove(dow[0])
        for day in dow:
            defaultdow = defaultdow + ',' + day[0:3]
    
    # Create job ids
    scheduleid = str(scheduleid)
    pause_id = "pause" + scheduleid + "FT" 
    resume_id = "resume" + scheduleid + "FT"

    # If for timing its every x amount of minutes
    if everymin == True:
        # Run the function for sending SMS based on the every x amount of minutes
        scheduler.add_job(infocheck, 'cron', args=(Phoneids, NumbersToSendTo, device, group), minute=everytime, day=defaultday, day_of_week=defaultdow, week=defaultweek, month=defaultmonth, id=scheduleid)
        
        # Call functions that will pause and resume the above job based on the from and till times
        scheduler.add_job(pauseschedule, 'cron', args=[scheduleid], hour=tillhour, minute=tillmin, id=pause_id) # Run till, till hour and till min
        scheduler.add_job(resumeschedule, 'cron', args=[scheduleid], hour=fromhour, minute=frommin, id=resume_id) # Resume at from hour and min
    
    # If for timing its every x amount of hours
    elif everymin == False:
        # Run the function for sending SMS based on the every x amount of hours
        scheduler.add_job(infocheck, 'cron', args=(Phoneids, NumbersToSendTo, device, group), hour=everytime, day=defaultday, day_of_week=defaultdow, week=defaultweek, month=defaultmonth, id=scheduleid)

        # Call functions that will pause and resume the above job based on the from and till times
        scheduler.add_job(pauseschedule, 'cron', args=[scheduleid], hour=tillhour, minute=tillmin, id=pause_id) # Run till, till hour and till min
        scheduler.add_job(resumeschedule, 'cron', args=[scheduleid], hour=fromhour, minute=frommin, id=resume_id) # Resume at from hour and min

    # scheduler.print_jobs()

# Function that pauses the schedule when timing = custom (window)
def pauseschedule(scheduleid):
    scheduler.pause_job(scheduleid)
    return "pause"

# Function that pauses the schedule when timing = custom (window)
def resumeschedule(scheduleid):
    scheduler.reschedule_job(scheduleid)
    return "resume"

# Function that removes the jobs on the end date of the schedule or when the schedule is removed
def endschedulerule(scheduleid, fromtill):

    # Creates all of the schedule ids
    startruleid = "start_" + str(scheduleid)
    endruleid = "end_" + str(scheduleid)
    start_id = "start" + str(scheduleid) + "FT"
    pause_id = "pause" + str(scheduleid) + "FT" 
    resume_id = "resume" + str(scheduleid) + "FT"

    # If custom (window) remove the pause, resume and the schedule window job
    if fromtill == True:
        scheduler.remove_job(start_id)
        scheduler.remove_job(pause_id)
        scheduler.remove_job(resume_id)
    
    # Remove the job for start date
    scheduler.remove_job(startruleid)
    # Remove the jobs for the actual schedule and then the job that runs this function and removes the jobs
    try:
        scheduler.remove_job(scheduleid)
        scheduler.remove_job(endruleid)
    except:
        pass

# Function for retrieving the list of schedules
@app.route('/getschedule/schedule.json')
def getschedules():

    # Get the user id from the url arguments
    userid = request.args.get('id')

    conn = mysql.connect()
    cursor = conn.cursor()
    
    # Retrieve all the schedule ids for the particular user
    sql = "SELECT scheduleid FROM tc_user_schedule WHERE userid = %s"
    cursor.execute(sql,(userid))
    rows = cursor.fetchall()
    scheduleids = list()

    for i in rows:
        scheduleids.append(int(i[0]))

    schedulerules = list()

    # Go through tc_schedules and retrieve all the information for the schedules that match that id
    for ID in scheduleids:
        sql1 = "SELECT * FROM tc_schedules WHERE id = %s"
        cursor.execute(sql1,(ID))
        schedule = cursor.fetchone()
        schedule = list(schedule)
        # Format disabled from a binary value into True and false
        for j in schedule:
            if j == b'\x00':
                schedule.remove(j)
                j = False
                schedule.append(j)
            elif j == b'\x01':
                schedule.remove(j)
                j = True
                schedule.append(j)
        schedulerules.append(schedule)

    json_data = []
    
    # Create a list of the row headers
    row_headers = [x[0] for x in cursor.description]

    # Add extra headers for the custom fields and add them to row_headers
    periodheaders = ['days', 'periodvalue', 'periodformat']
    timingheaders = ['hourvalue', 'fromvalue', 'timeEveryValue', 'timeEveryFormat', 'tillvalue']
    startendheaders = ['startDate', 'endDate']

    for ph in periodheaders:
        row_headers.append(ph)
    for th in timingheaders:
        row_headers.append(th)
    for seh in startendheaders:
        row_headers.append(seh)

    setperiods = ['every1days', 'every2days', 'every3days', 'every1weeks', 'every2weeks']

    days = ''
    periodvalue = ''
    periodformat = ''
    hourvalue = ''
    fromvalue = ''
    timeEveryValue = ''
    timeEveryFormat = ''
    tillvalue = ''
    startDate = ''
    endDate = ''

    # Get period from schedulerules and check value
    for k in schedulerules:
        period = k[4]
        # If value is Custom (day)
        if period[0] != 'e':
            days = period
            k.remove(period)
            period = 'customd'
            k.insert(4, period)
        # If value is Custom (period)
        elif period[0] == 'e' and period not in setperiods:
            search = re.findall(r'(every)(\d*)([a-z]*)', period)
            periodvalue = search[0][1]
            periodformat = search[0][2]
            k.remove(period)
            period = 'customp'
            k.insert(4, period)
        # Add values for period headings to schedule rules list
        k.extend([days, periodvalue, periodformat])

    # Get timing from schedulerules
    for k in schedulerules:    
        timing = k[5]
        startDate = k[6]
        endDate = k[7]
        # If timing is a predefined variable do nothing
        if timing[0] == 'e':
            pass
        # If timing is custom (hour)
        elif len(timing) == 5:
            hourvalue = timing
            k.remove(timing)
            timing = 'customh'
            k.insert(5, timing)
        # If timing is custom (window)
        elif len(timing) > 5:
            searchtime = re.findall(r'(\d*:\d*);(\d*)([a-z]*);(\d*:\d*)', timing)
            # From
            fromvalue = searchtime[0][0]
            if fromvalue[1] == ':':
                fromvalue = '0' + fromvalue
            if len(fromvalue[3:]) == 1:
                fromvalue = fromvalue[0:3] + '0' + fromvalue[-1]
            # Every:
            timeEveryValue = searchtime[0][1] 
            timeEveryFormat = searchtime[0][2]
            # Till:
            tillvalue = searchtime[0][3]
            if tillvalue[1] == ':':
                tillvalue = '0' + fromvalue
            if len(tillvalue[3:]) == 1:
                tillvalue = tillvalue[0:3] + '0' + tillvalue[-1]
            k.remove(timing)
            timing = 'customw'
            k.insert(5, timing)
        # Add values for all the timing headers to schedulerules list
        k.extend([hourvalue, fromvalue, timeEveryValue, timeEveryFormat, tillvalue, startDate, endDate])

    # Add them to the json_data list as a dictionary
    for rule in schedulerules:
        json_data.append(dict(zip(row_headers,rule)))
    
    # Return the schedule rules as JSON
    return json.dumps(json_data, sort_keys=True, indent=4, default=jsondateconverter, separators=(',', ': '))

# Convert datetime values from schedules into string inorder to be added to JSON 
def jsondateconverter(o): 
    if isinstance(o, datetime):
        return o.__str__()

# Function for removing a schedule
@app.route('/removeschedule/<scheduleid>')
def removeschedule(scheduleid):
    userid = request.args.get('id')

    conn = mysql.connect()
    cursor = conn.cursor()

    # Get the user id and schedule id and remove it from tc_schedules and tc_user_schedule
    try:    
        sql = "DELETE FROM tc_schedules WHERE id = %s"
        cursor.execute(sql,(scheduleid))
        conn.commit()

        sql = "DELETE FROM tc_user_schedule WHERE id = %s AND scheduleid = %s"
        cursor.execute(sql,(userid, scheduleid))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

    return "DELETED"

# Function for adding device to installation (All Devices)
@app.route('/alldevices/<name>/<IMEI>')
def adddevice(name, IMEI):

    # Get device id and user id from the arguments
    deviceid = request.args.get('deviceid')
    deviceid = int(deviceid)

    userid = request.args.get('userid')

    # Create the locator id
    serialnumber = IMEI[8:14]
    loc_id = 'LC'+ str(serialnumber)
    
    conn = mysql.connect()
    cursor = conn.cursor()

    # If device doesn't exist insert it into tc_alldevices
    if deviceid < 0:
        try: 
            sql = "INSERT INTO tc_alldevices (name, loc_id, imei) VALUES (%s, %s, %s)"
            cursor.execute(sql,(name, loc_id, IMEI))
            conn.commit()

            # Get id of device to add it to tc_user_alldevices
            sql1 = "SELECT id FROM tc_alldevices WHERE loc_id = %s"
            cursor.execute(sql1,(loc_id))
            rows = cursor.fetchone()
            deviceid = rows[0]

            sql2 = "INSERT INTO tc_user_alldevices (userid, deviceid) VALUES (%s, %s)"
            cursor.execute(sql2,(userid, deviceid))
            conn.commit()
        except:
            conn.rollback()
        finally:
            conn.close()

    # If device already exists update it  
    elif deviceid > 0: 
        try:
            sql3 = "UPDATE tc_alldevices SET name = %s, loc_id = %s, imei = %s WHERE id = %s"
            cursor.execute(sql3,(name, loc_id, IMEI, deviceid))
            conn.commit()
        except:
            conn.rollback()
        finally:
            conn.close()

    return "Added to DB"
    
# Function for removing the device
@app.route('/removedevice/<deviceid>')    
def removedevice(deviceid):
    userid = request.args.get('id')

    conn = mysql.connect()
    cursor = conn.cursor()
    
    # Using user id and device id remove device from tc_alldevices and tc_user_alldevices
    try:    
        sql = "DELETE FROM tc_alldevices WHERE id = %s"
        cursor.execute(sql,(deviceid))
        conn.commit()

        sql = "DELETE FROM tc_user_alldevices WHERE id = %s AND deviceid = %s"
        cursor.execute(sql,(userid, deviceid))
        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

    return "DELETED"

# Retrieve all the devices from tc_alldevices
@app.route('/alldevices/get')
def getalldevices():
    
    userid = request.args.get('id')

    conn = mysql.connect()
    cursor = conn.cursor()
    
    # Retrieve all the device ids for the particular user
    sql = "SELECT deviceid FROM tc_user_alldevices WHERE userid = %s"
    cursor.execute(sql,(userid))
    rows = cursor.fetchall()
    deviceids = list()

    for i in rows:
        deviceids.append(int(i[0]))
    
    alldevices = list()

    # Get the devices from tc_alldevices that match the ids
    for ID in deviceids:
        sql1 = "SELECT * FROM tc_alldevices WHERE id = %s"
        cursor.execute(sql1,(ID))
        devices = cursor.fetchone()
        alldevices.append(devices)

    json_data = []
    
    # Dump the data into JSON format and return it
    row_headers = [x[0] for x in cursor.description]
    for device in alldevices:
        json_data.append(dict(zip(row_headers,device)))
    
    return json.dumps(json_data, sort_keys=True, indent=4, default=jsondateconverter, separators=(',', ': '))

# Counter for number of SMS sent and messages received outside of 2 minutes
sendsms.counter = 0
receivesms.counter = 0
    
app.run(host= '0.0.0.0')

# ------------------------------------------------------
# References: 
# ------------------------------------------------------

# Username: Peters 2016. Sending and receiving SMS by command line with Huawei E3131 and HiLink on a debian system. [Source code].
# Available at: https://stackoverflow.com/questions/38016641/sending-and-receiving-sms-by-command-line-with-huawei-e3131-and-hilink-on-a-debi [Accessed: 18 February
# 2019]. --> Used for inspiration for sending SMS
    
# Username: BeefBurger 2017. Huawei API SMS Documentation. [Source code].
# Available at: https://stackoverflow.com/questions/22561947/huawei-api-sms-documentation?rq=1 [Accessed: 18 February
# 2019]. --> Used for retrieving the sessionid and token from Huawei Modem

# Username: Mani 2017. Python converting mysql query result to json. [Source code].
# Available at: https://stackoverflow.com/questions/43796423/python-converting-mysql-query-result-to-json [Accessed: 20 March
# 2019]. --> Used for outputting data from tables into JSON

# Szabo, Gabor n.d. How to serialize a datetime object as JSON using Python?. [Source code].
# Available at: https://code-maven.com/serialize-datetime-object-as-json-in-python [Accessed: 20 March
# 2019]. --> Used for converting datetime from table into string so it can be used in JSON

# ------------------------------------------------------
