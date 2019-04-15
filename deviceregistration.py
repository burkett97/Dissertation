#!/usr/bin/env python3

# Jack Burkett- C1616242 Cardiff University

import re
import sys
import pymysql
import pymysql.cursors
from datetime import datetime

systemtime = datetime.today().strftime('%Y-%m-%d %-H:%M:%S%z')

# Script that creates a database called builtdevices and each time checks that it exists on mysql localhost
# creates a table called registereddevices with fields: Name, Unique_id, IMEI, registrationtime
# IMEI number is inputted
# Name is just LOC_number that increments- primary key
# Unique id is just LC followed by the serial number part of the IMEI- this will be the unique key
# IMEI inputted into table
# Creation date inputs time device registered

host = 'localhost'
user = 'jack'
password = 'somepassword'
port = 3306
db = 'built_devices'

# Takes input of IMEI
def main():
    createdatabase()
    # Take input as IMEI- check its in correct format. If it is ask user to confirm that information is correct. This is then passed to UniqueID and then from there added to db
    welcome = "  Welcome to device registration"
    
    print("-" * (len(welcome)+ 4))
    print(welcome)
    print("-" * (len(welcome)+ 4) +'\n')
    
    print("Please input the IMEI number of the device")
    print("If you need help type --help \n")
    print("To exit at any time type exit\n")
    
    valid_input = False

    counter = 0
    # Will ask for IMEI input until the correct IMEI is inputted or IMEI number is inputted incorrectly 5 times. It will then close the program.
    while valid_input == False and counter < 5:
        input_verification = False
        verification_counter = 0
        IMEI = input("IMEI:")
        # Checks that input is just numbers
        if IMEI == 'exit':
            print("Program is closing")
            raise SystemExit
        elif IMEI == '--help':
            print("About IMEI:\n")
            print("An IMEI number is a 15 digit number printed on a mobile device. Every device has one and is unique to that device.")
            print("Often this is under the cover. On the locators please remove the back plate to reveal it")
            print("If there are any letters before or after please ignore and just type the 15 numbers\n")

            print("This program works by taking the IMEI and generating a simple name and unique id that can be added to the device")
            print("It then will add the locators information to a database in order to register the device.\n")

            print("To continue with the program please type Y otherwise type any other key and the program will close")
            helpinput = input()

            if helpinput == 'Y' or helpinput == 'y':
                valid_input = False
                print()
            else:
                raise SystemExit

        elif not re.match("^[0-9]*$", IMEI):
            counter += 1
            print("\n**Error! Only numbers allowed!**")
            print("Please re-enter the IMEI\n")
        # Checks that input is 15 characters in length
        elif len(IMEI) != 15:
            counter += 1
            print("\n**Error! IMEI numbers must be 15 numbers in length!**")
            print("Please re-enter the IMEI\n")
        # If it is correct the input will be printed out and user has to verify its correct
        else:
            # The program will ask for verification 3 times and then will restart and ask for IMEI number again. Uses y or n for yes or no
            while input_verification == False and verification_counter < 3:
                print("\nYour input was:", IMEI)
                print("Is this correct? Type Y for yes or N for No")
                verification = input()
                # If user says yes then finish as valid input and verified
                if verification.lower() == 'y':
                    print("Ok! Your IMEI number has been inputted!")
                    valid_input = True
                    input_verification = True
                    uniqueIDformat(IMEI)
                # If user says this is wrong then restart and ask for IMEI number again with a new set of 5 attempts
                elif verification.lower() == 'n':
                    print("\nPlease enter the correct IMEI number")
                    # Reset valid_input and set input_verification to True to finish this while loop
                    valid_input = False
                    input_verification = True
                    counter = 0
                else:
                    # Asks user to check input
                    if verification_counter < 2:
                        print("\nPlease check your input it should either be Y or N")
                    # Once this has been done 3 times it will restart and ask for IMEI number again but won't reset IMEI attempts
                    elif verification_counter == 2:
                        print("\n**Error! IMEI number not verified! Please re-enter the IMEI number**\n")
                        counter += 1
                        valid_input == False
                    verification_counter += 1
    

    if counter == 5:
        print("You are entered the wrong IMEI number 5 times. The program will now close!")

# Creates build_devices database if it doesn't exist        
def createdatabase():
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
        sql = "CREATE DATABASE IF NOT EXISTS built_devices"
        cursor.execute(sql)
    
    createtable()

# Creates registered_devices table if it doesn't exist
def createtable():
    
    conn = pymysql.connect(host=host, user=user, password=password, port=port, db=db, cursorclass=pymysql.cursors.DictCursor)

    cursor = conn.cursor()

    sql = "SHOW TABLES"
    cursor.execute(sql)
    tables = cursor.fetchall()

    table_exists = False

    for table in tables:
        if table["Tables_in_built_devices"] == 'registered_devices':
            table_exists = True

    if table_exists == False:
        sql = "CREATE TABLE IF NOT EXISTS registered_devices(id int NOT NULL AUTO_INCREMENT PRIMARY KEY, Name varchar(32) NOT NULL, UniqueID varchar(32) NOT NULL UNIQUE, IMEI varchar(32) NOT NULL, RegistrationDate TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"
        cursor.execute(sql)

# Creates the name for the device
def nameformat():
    
    # Get last value in Name and get number attached. Increment by one and thats name of device
    conn = pymysql.connect(host=host, user=user, password=password, port=port, db=db, cursorclass=pymysql.cursors.DictCursor)

    cursor = conn.cursor()
    
    name = 'LOC_01'

    sql = "SELECT * FROM registered_devices ORDER BY id DESC LIMIT 1"
    cursor.execute(sql)
    rows = cursor.fetchone()
    if rows:
        for key, value in rows.items():
            if key == 'Name':
                number = value[4:]
                number =  int(number) + 1
                if int(number) < 10:
                    number = '0' + str(number)
                    name = 'LOC_' + number
                else:
                    name = 'LOC_' + number
    return name

# Creates the uniqueid for the device
def uniqueIDformat(IMEI):
    # Takes the serial number part of the IMEI number and adds it to LC to create a unique id
    serialnumber = IMEI[8:14]
    uniqueid = 'LC'+ str(serialnumber)
    addtodb(IMEI, uniqueid)

# Adds all the informatio to the database
def addtodb(IMEI, uniqueid):
    name = nameformat()

    conn = pymysql.connect(host=host, user=user, password=password, port=port, db=db, cursorclass=pymysql.cursors.DictCursor)

    cursor = conn.cursor()
    try: 
        sql = "INSERT INTO registered_devices (Name, UniqueID, IMEI) VALUES (%s, %s, %s)"
        cursor.execute(sql,(name, uniqueid, IMEI))
        conn.commit()
        print("\nThe devices was successfully registered!")
        print("Device with IMEI number: " + IMEI + " has unique id " + uniqueid + "\n")
    except:
        conn.rollback()
    finally:
        conn.close()

if __name__== "__main__":
  main()

# Add menu that allows- register device, show all registered devices, edit registered device