#!/usr/bin/env python3

# Jack Burkett- Cardiff University

# Modules to import
import re
import pprint
import sys
import os
import time
import json
import pymysql
import pymysql.cursors
import requests, sys
import xml.etree.ElementTree as ET
from datetime import datetime

from flask import Flask, render_template, jsonify
from flask import request
from flask_cors import CORS
from flaskext.mysql import MySQL

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
scheduler.start()


# Messages to locator --> Locator V2
Location_Message = "smslink123456"

app = Flask(__name__)

starttime = datetime.today().strftime('%Y-%m-%d %-H:%M:%S%z')

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
def sendsms(NumbersToSendTo,stats, ten):

    scheduler.print_jobs()

    timewaited = 30

    # Get session id and token from authenticate
    token, sessionID = authenticate()
    LengthofLoc = len(Location_Message)
    
    # Add them to headers
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}

    # Get system time which will be used for date message is sent
    systime = datetime.today().strftime('%Y-%m-%d %-H:%M:%S%z')

    numbers = ""
    
    # Iterate through the list of numbers and concatenate them as <Phone>Number</Phone> in order to add them to request
    for number in NumbersToSendTo:
        sms_phone = "<Phone>" + str(number) + "</Phone>"
        numbers = numbers + sms_phone

    SMS = "<request><Index>-1</Index><Phones>" + numbers + "</Phones><Sca/><Content>" + Location_Message + "</Content><Length>" + str(LengthofLoc) + "</Length><Reserved>1</Reserved><Date>" + systime + "</Date></request>"

    # Post request enables SMS to be sent
    send = requests.post("http://" + IP + "/api/sms/send-sms", data=SMS, headers=headers)
    stats[0] += 1

    # Once SMS is sent pass number and system time to receivesms to get response
    print("SMS has been sent")
    time.sleep(30)
    print("Looking for reply")
    receivesms(timewaited, systime, NumbersToSendTo, stats, ten)
    return "Sent"

# Receive messages back
def receivesms(timewaited, systime, NumbersToSendTo, stats, ten):

    token, sessionID = authenticate()
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}

    numberofmessages = len(NumbersToSendTo)

    if len(NumbersToSendTo) < 5:
        numberofmessages = 5

    SMSRetrieve="<request><PageIndex>1</PageIndex><ReadCount>" + str(numberofmessages) + "</ReadCount><BoxType>1</BoxType><SortType>0</SortType><Ascending>0</Ascending><UnreadPreferred>1</UnreadPreferred></request>"

    receive = requests.post("http://" + IP + "/api/sms/sms-list", data=SMSRetrieve, headers=headers)
    output = receive.text
    tree = ET.fromstring(output) 

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

    numbers = NumbersToSendTo
    
    # Iterate through list of phones numbers in received messages. If message in list of sms sent and the date of the message is after 
    if timewaited <= 120:
        i = 0
        # for no in inboxphoneNumbers:
        while i < len(inboxphoneNumbers):
            # If the number that an sms was sent to is in the list of messages and the date is after the time the message was sent...
            # if no in NumbersToSendTo:
            if inboxphoneNumbers[i] in NumbersToSendTo:
                # if datesofMessages[i] > systime:
                if datesofMessages[i] > systime:
                    # ...get the contents of the message, date and content and pass it through to be formatted
                    p = inboxphoneNumbers[i]
                    d = datesofMessages[i]
                    c = contentofMessages[i]
                    mess_id = messageid[i]

                    stats[1] += 1

                    dtime = d[-5:]
                    stime = systime[-5:]
                    timeformat = '%M:%S'

                    responsetime = datetime.strptime(dtime, timeformat) - datetime.strptime(stime, timeformat)
                    responsetime = int(responsetime.total_seconds())
                    stats[2] = stats[2] + abs(responsetime)

                    format(c, stats, ten)
                    messagelog(systime, p, d, c)
                    numbers.remove(p)
                    deletesms(mess_id)

                    print("Message found for " + inboxphoneNumbers[i])
            i += 1
        if len(numbers) != 0:
            timewaited += 15
            time.sleep(15)
            receivesms(timewaited, systime, NumbersToSendTo, stats, ten)
        else:
            print("Messages found")
    else:
        # Error message sent to traccar
        print("Message couldn't be found within 2 minutes for: " + ', '.join(numbers))
        stats[7] += 1 

        if ten == True:
            open('stats10.txt', 'w').close()
            with open('stats10.txt', 'w') as file:
                i = 0
                for number in stats:
                    if i < 7:
                        file.write("%s, " % number)
                    else:
                        file.write("%s" % number)
                    i += 1
        elif ten == False:
            open('stats20.txt', 'w').close()
            with open('stats20.txt', 'w') as file:
                i = 0
                for number in stats:
                    if i < 7:
                        file.write("%s, " % number)
                    else:
                        file.write("%s" % number)
                    i += 1
    return "Received"

# Log every message received
def messagelog(systime, p, d, c):
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
            file.write(str(messageid) + ", " + systime + ", " + p + ', ' + d + ', ' + c + ';\n')
    else:
        with open("log/messagelog.txt", "r+") as file:
            last_line = file.readlines()[-1]
            messageid = last_line.split(',')[0]
            messageid =  int(messageid) + 1
        with open("log/messagelog.txt", "a") as file:
            file.write(str(messageid) + ", " + systime + ", " + p + ', ' + d + ', ' + c + ';\n')

    return "Logged"

# Fomat messages
def format(c, stats, ten):
    # Takes the content of retrieve messages and formats it. This can then be passed to addtodb.
    splitmessage = c.split()

    first = splitmessage[0]

    if first.startswith('last:'):
        print("NO GPS SIGNAL- LAST KNOW LOCATION TO BE ADDED")
        stats[3] +=1

    elif first.startswith('lat:'):
        print("GPS SIGNAL")
        stats[4] += 1


    elif first.startswith('maps.'):
        print("Map")
        stats[5] += 1

    else:
        print("Error Message")
        stats[6] += 1
    
    open('stats.txt', 'w').close()
    with open('stats.txt', 'w') as file:
        i = 0
        for number in stats:
            if i < 7:
                file.write("%s, " % number)
            else:
                file.write("%s" % number)
            i += 1
    
    if ten == True:
        open('stats10.txt', 'w').close()
        with open('stats10.txt', 'w') as file:
            i = 0
            for number in stats:
                if i < 7:
                    file.write("%s, " % number)
                else:
                    file.write("%s" % number)
                i += 1
    elif ten == False:
        open('stats20.txt', 'w').close()
        with open('stats20.txt', 'w') as file:
            i = 0
            for number in stats:
                if i < 7:
                    file.write("%s, " % number)
                else:
                    file.write("%s" % number)
                i += 1
    return "Formatted"

# # Function to delete SMS from modem (not in use at the moment)
def deletesms(index):
    # Once information has been added to database and the message has been logged into file the message can be deleted from modem to save space
    token, sessionID = authenticate()
    headers = { "__RequestVerificationToken": token, "Content-Type": "text/xml", "Cookie": sessionID}
    
    Delete="<request><Index>" + index + "</Index></request>"

    delete = requests.post("http://" + IP + "/api/sms/delete-sms", data=Delete, headers=headers)
    
    return "Message deleted"
    
def endschedule():
    scheduler.remove_job('everymin')
    scheduler.remove_job('endmin')

    # os.rename('stats.txt', '5minstats.txt')

def sms():

    stats = list()

    if not os.path.exists('stats.txt'):
        with open('stats.txt', 'w'):
            pass
            
    with open('stats.txt') as file: 
        values = file.read()
        if len(values) == 0:
            stats = [0, 0, 0, 0, 0, 0, 0, 0]
        else:
            values = values.split(",")
            stats = [0, 0, 0, 0, 0, 0, 0, 0]
            i = 0
            for v in values:
                stats[i] = int(v)
                i += 1

    number = ['+44 + Enter a number']
    sendsms(number, stats)

def min10():
    
    stats = list()

    if not os.path.exists('stats10.txt'):
        with open('stats10.txt', 'w'):
            pass
            
    with open('stats10.txt') as file: 
        values = file.read()
        if len(values) == 0:
            stats = [0, 0, 0, 0, 0, 0, 0, 0]
        else:
            values = values.split(",")
            stats = [0, 0, 0, 0, 0, 0, 0, 0]
            i = 0
            for v in values:
                stats[i] = int(v)
                i += 1

    number = ['+44 + Enter a number']
    sendsms(number, stats, True)

def min20():
    
    stats = list()

    if not os.path.exists('stats20.txt'):
        with open('stats20.txt', 'w'):
            pass
            
    with open('stats20.txt') as file: 
        values = file.read()
        if len(values) == 0:
            stats = [0, 0, 0, 0, 0, 0, 0, 0]
        else:
            values = values.split(",")
            stats = [0, 0, 0, 0, 0, 0, 0, 0]
            i = 0
            for v in values:
                stats[i] = int(v)
                i += 1
    
    number = ['+44 + Enter a number']
    sendsms(number, stats, False)

# scheduler.add_job(sms, 'cron', minute='*/1', id='every1min')
scheduler.add_job(min10, 'cron', minute='*/10', id='every10min')
scheduler.add_job(min20, 'cron', minute='*/20', id='every20min')

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