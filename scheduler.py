#!/usr/bin/env python3

# Import contactlocator.py in order to sendsms
import contactlocator

import sys
import re
import schedule
import threading
import pymysql
import pymysql.cursors
# from crontab import CronTab
from datetime import datetime

# Database config
host = 'localhost'
user = 'jack'
password = 'somepassword'
port = 3306
# db = 'traccar'
db = 'test'

# my_cron = CronTab(user='jack')

def main():
    addschedulejob(3)
    # accessdb()
    # testcreatedbandtable()
    # addvalues()

    # Gets the scheduleid from the web interface and uses this to get the schedule info from the database
def addschedulejob(scheduleid):
    
    conn = pymysql.connect(host=host, user=user, password=password, port=port, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    
    # Get the scheduling information from tc_scheduling
    sql = "SELECT Devices, Groups, Period, Frequency, StartTime, EndTime FROM tc_scheduling WHERE ScheduleID = %s"     
    cursor.execute(sql, (scheduleid))
    rows = cursor.fetchone()
    
    numbers, period, frequency, starttime, endtime = format(rows)

    print(numbers, period, frequency, starttime, endtime)

    # sendsms(numbers)

    # Run parallel scheduled jobs
def run_threaded(job_func):
    job_thread = threading.Thread(target=job_func)
    job_thread.start()   
    

def editschedulejob():
    pass

def removeschedulejob():
    pass

    # Gets the database output and retrieves all the relevant information and formats it
def format(rows):

    # Connect to database
    conn = pymysql.connect(host=host, user=user, password=password, port=port, db=db, cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()

    numbers, devices, groups, period, frequency = ([] for i in range(5))

    starttime = ''
    endtime = ''

    # For each column and value get the information
    for key,value in rows.items():
        # If devices listed, split them up and compare to tc_devices to get the phone number and input into list of numbers
        if key == 'Devices' and value != '':
            devices = value.split(';')
            for d in devices:
                sql = "SELECT phone FROM tc_devices WHERE uniqueid = %s"     
                cursor.execute(sql,(d))
                number = cursor.fetchone()
                numbers.append(number['phone'])
        # If group listed, split them up and compare to tc_devices to get the phone number and input into list of numbers
        elif key == 'Groups' and value != '':
            groups = value.split(';')
            for g in groups:
                sql = "SELECT phone FROM tc_devices WHERE groupid = %s"     
                cursor.execute(sql,(g))
                group = cursor.fetchone()
                numbers.append(group['phone'])
        # Get period and add to list- formatting done in createcronjobs
        elif key == 'Period':
            if value.startswith('Every'):
                per_value = value.split()[1] # Gets the value i.e. 2, 3, 4 etc
                per_format = value.split()[2] # Gets the period format i.e. days, weeks, months etc
                if per_value == '1':
                    period.append('.every().' + per_format[:-1])
                else:
                    period.append('.every(' + per_value + ').' + per_format + "()")
            # Splits days up and add them to list
            else:
                days = value.split(';')
                for d in days:
                    period.append('.every().' + d.lower() + '()')
        # Get frequency and add to list formatting done in createcronjobs
        elif key == 'Frequency':
            if value.startswith('Every'):
                freq_value = value.split()[1] # Gets the value i.e. 2, 3, 4 etc
                freq_format = value.split()[2] # Gets the period format i.e. days, weeks, months etc
                if freq_value == '1':
                    frequency.append('.every().' + freq_format[:-1])
                else:
                    frequency.append('.every(' + freq_value + ').' + freq_format + "()")
            # Splits days up by and add them to list
            elif value.startswith('0'):
                times = value.split(';')
                for t in times:
                    if len(t) == 5:
                        frequency.append(t)
                    elif len(t) > 5:
                        time_from = t.split(',')[0]
                        time_every = t.split(',')[1]
                        time_till = t.split(',')[2]
                        if time_every[-1] == 'm':
                            if time_every[:-1] == '1':
                                time_every = '.every().minute()'
                            else:
                                time_every = '.every(' + time_every[:-1] + ').minutes()'
                        elif time_every[:-1] == 'h':
                            if time_every[:-1] == '1':
                                time_every = '.every().hour()'
                            else:
                                time_every = '.every(' + time_every[:-1] + ').hours()'
                        frequency.append({'From:': time_from, 'Every:': time_every, 'Till:': time_till})
        # Get starttime and endtime
        elif key == 'StartTime':
            starttime = value
        elif key == 'EndTime':
            endtime = value

    return numbers, period, frequency, starttime, endtime


# Access the schedule database and get the numbers and the schedule rules. Pass these to run
def accessdb():
    
    host = 'localhost'
    user = 'jack'
    password = 'somepassword'
    port = 3306
    # db = 'traccar'
    db = 'test'

    conn = pymysql.connect(host=host, user=user, password=password, port=port, db=db, cursorclass=pymysql.cursors.DictCursor)

    cursor = conn.cursor()
    
    # Get devices/groups and the scheduling rules
    sql = "SELECT Devices, Groups, Period, Frequency, StartTime, EndTime, Disabled FROM tc_scheduling WHERE DISABLED = '0'"     
    cursor.execute(sql)
    rows = cursor.fetchall()

    # If there any scheduling rules go through each row
    if rows:
        for i in rows:
            numbers = list()
            devices = list()
            groups = list()
            period = list()
            frequency = list()
            starttime = ''
            endtime = ''
            # For each column and value get the information
            for key,value in i.items():
                # If devices listed, split them up and compare to tc_devices to get the phone number and input into list of numbers
                if key == 'Devices' and value != '':
                    devices = value.split(';')
                    for d in devices:
                        sql = "SELECT phone FROM tc_devices WHERE uniqueid = %s"     
                        cursor.execute(sql,(d))
                        number = cursor.fetchone()
                        numbers.append(number['phone'])
                # If group listed, split them up and compare to tc_devices to get the phone number and input into list of numbers
                elif key == 'Groups' and value != '':
                    groups = value.split(';')
                    for g in groups:
                        sql = "SELECT phone FROM tc_devices WHERE groupid = %s"     
                        cursor.execute(sql,(g))
                        group = cursor.fetchone()
                        numbers.append(group['phone'])
                # Get period and add to list- formatting done in createcronjobs
                elif key == 'Period':
                    if value.startswith('Every'):
                        period.append(value)
                    # Splits days up and add them to list
                    elif value.startswith('0'):
                        period = value.split(';')
                # Get frequency and add to list formatting done in createcronjobs
                elif key == 'Frequency':
                    if value.startswith('Every'):
                        frequency.append(value)
                    # Splits days up by and add them to list
                    elif value.startswith('0'):
                        frequency = value.split(';')
                # Get starttime and endtime
                elif key == 'StartTime':
                    starttime = value
                elif key == 'EndTime':
                    endtime = value
            createcronjobs(numbers, period, frequency, starttime, endtime)                

# Creates a cron job to run the script at the times
def createcronjobs(numbers, period, frequency, starttime, endtime):
    # print(numbers, period, frequency, starttime, endtime)

    # Numbers need to be sent to contactlocator.py
    numbers = numbers
    cron_default = {'minutes': '*', 'hour': '*', 'day(month)': '*', 'month': '*', 'day(week)': '*'}

    freq_time = ''
    time_from = ''
    time_every = ''
    time_till = ''

    # Period needs to be distinguished from Every x days/weeks/months (option1) and selected days (option2)
    for p in period:
        if p.startswith('Every'):
            # Possible values: Every x days/weeks/months
            per_value = p.split()[1] # Gets the value i.e. 2, 3, 4 etc
            per_format = p.split()[2] # Gets the period format i.e. days, weeks, months etc
        elif p.startswith('0'):
            # Possible values: 00-06
            days = p.split(';')
    for f in frequency:
        if f.startswith('Every'):
            # Possible values: Every x mins/hours
            freq_value = f.split()[1] # Gets the value i.e. 2, 3, 4 etc
            freq_format = f.split()[2] # Gets the period format i.e. mins, hours
        elif len(f) == 5:
            if freq_time == '':
                freq_time = f
            else: 
                freq_time = freq_time + "," + f
        elif (len(f)) > 5:
            time_from = f.split(',')[0]
            time_every = f.split(',')[1]
            time_till = f.split(',')[2]
        print(time_from, time_every, time_till)
    print(freq_time)
    #     elif len(p[0]) > 5:
    #     for j in days:
    #         timefrom = j.split(',')[0]
    #         timeevery = j.split(',')[1]
    #         timetill = j.split(',')[2]

    # # Formatting for frequency option 2 --> needs to be done in createcronjobs
    # if len(days[0]) > 5:
    #     for j in days:
    #         timefrom = j.split(',')[0]
    #         timeevery = j.split(',')[1]
    #         timetill = j.split(',')[2]
    # print(numbers, period, frequency, starttime, endtime)
    # pass    

def testcreatedbandtable():

    host = 'localhost'
    user = 'jack'
    password = 'somepassword'
    port = 3306
    db = 'test'

    conn = pymysql.connect(host=host, user=user, password=password, port=port, cursorclass=pymysql.cursors.DictCursor)

    cursor = conn.cursor()

    sql = "SHOW DATABASES"
    cursor.execute(sql)
    databases = cursor.fetchall()

    database_exists = False

    for database in databases:
        if database["Database"] == db:
            database_exists = True

    if database_exists == False:
        sql = "CREATE DATABASE IF NOT EXISTS test"
        cursor.execute(sql)

    conn = pymysql.connect(host=host, user=user, password=password, port=port, db=db, cursorclass=pymysql.cursors.DictCursor)

    cursor = conn.cursor()

    sql = "SHOW TABLES"
    cursor.execute(sql)
    tables = cursor.fetchall()

    table_exists = False

    for table in tables:
        if table["Tables_in_test"] == 'tc_scheduling':
            table_exists = True

    if table_exists == False:
        sql = "CREATE TABLE IF NOT EXISTS tc_scheduling(ScheduleID int NOT NULL AUTO_INCREMENT PRIMARY KEY, Name varchar(32) NOT NULL, Devices varchar(64) NOT NULL, Groups varchar(32), Period varchar(64), Frequency varchar(128), StartTime DATETIME, EndTime DATETIME, Disabled char(1) DEFAULT '0')"
        cursor.execute(sql)

def addvalues(): 

    host = 'localhost'
    user = 'jack'
    password = 'somepassword'
    port = 3306
    # db = 'traccar'
    db = 'test'

    conn = pymysql.connect(host=host, user=user, password=password, port=port, db=db, cursorclass=pymysql.cursors.DictCursor)

    cursor = conn.cursor()

    Name = 'Rule 3'
    Devices = '004'
    Groups = ''
    Period = '01'
    Frequency = 'Every 20 mins'
    StartTime = '2019-03-14 09:00:00'
    EndTime = '2019-03-15 09:00:00'
    
    sql = "INSERT INTO tc_scheduling (Name, Devices, Groups, Period, Frequency, StartTime, EndTime, Disabled) VALUES (%s, %s, %s, %s, %s, %s, %s, 1)"
    cursor.execute(sql,(Name, Devices, Groups, Period, Frequency, StartTime, EndTime))
    conn.commit()

if __name__== "__main__":
  main()

# Schedulder works by gettings all the schedule rules in the database along with the device / group ids
# It will then look at tc_devices to get the numbers of the relevant devices (individual devices) --or--
# It will look at tc_devices for all devices with the same groupid as the one requested and get the number (group of devices)
# 
# A cron job will be run based on the scheduling groups where the numbers will be passed through to the sendsms part of contactlocator.py 

# When a rule is added/deleted/edited the script is run again to update the cronjobs

# DB design: ScheduleID, Name, Devices, Groups, Period

# For each day add it as numbers where Sunday = 0 and Saturday = 6 
# For every go --> Every x days/weeks/months/years
# For frequency option 1 add it as 01:00; 02:00; 03:00; which means at 1,2,3
# For frequency option 2 add its as 01:00, 5 m, 06:00 which means every 5 mins from 01:00 - 06:00

# All list items will be split by ;

# Formatting


    # # Formatting for period option 1 --> needs to be done in createcronjobs
    # if value.startswith('Every'):
        # timeframe = value.split()[1]
        # timeformat = value.split()[2]

    # # Formatting for period option 2 --> needs to be done in createcronjos
    # elif value.startswith('0'):
        # period = value.split(';')

    # # Formatting for frequency option 1 --> needs to be done in createcronjobs
    # timeframe = value.split()[1]
    # timeformat = value.split()[2]

    # # Formatting for frequency option 2 --> needs to be done in createcronjobs
    # if len(days[0]) > 5:
    #     for j in days:
    #         timefrom = j.split(',')[0]
    #         timeevery = j.split(',')[1]
    #         timetill = j.split(',')[2]