# Source code for final year project

Project: Tracking Poachers using Low-Cost GSM Location Trackers and a Modified Open-Source GPS Tracking Software

This project enables users to send SMS messages from the Huawei E3531 USB Modem to a cheap consumer-grade location device- a clone of the TK102 GPS SMS location device. As a GPS tracking software it uses Traccar (https://github.com/traccar/traccar) which has been modified to extend the features of it in order to allow the system created in this project to work.

## Requirements:

* Python 3
* MYSQL server
* Python modules:
  * Requests
  * PyMySQL
  * SQLAlchemy
  * Flask
  * Flask-CORS
  * Flask-MYSQL
  * Flask-SQLAlchemy
  * APScheduler

## Running the source code

1. Ensure all requirements are installed.
2. Clone this Github repository.
3. In MYSQL create a database for the Traccar tables, the program will automatically
create the tables for you.
4. To enable and run the Flask Server:
     * In terminal navigate to the 'Traccar/FlaskServer/' directory.
     * To make the file executable run 'chmod +x ./traccar_flask.py'.
     * Run the server by inputting '/traccar_flask.py'.
5. To run the source code in:
     * Netbeans- follow the tutorial at: https://www.traccar.org/build-in-netbeans/
     * Other compilers- follow the tutorial at: https://www.traccar.org/build/

At this point both the Traccar and Flask Server are running on ports 8082 and 5000, respectively. Open up a browser and type in ‘localhost:8082’ and the default username: admin and the default password: admin to begin using the software.

## Using the test files

Before using the test files please read the 'Readme-Testing' file as this indicates what the test results are showing

The Flask_Test.py file can be used for all of the tests and creates a Flask Server so the tests can be run. By default this file tests for every 10 and 20 minutes however this can be modified for every 1 and 5 minutes or any period you like by doing the following:

* Change the filename in line 181 and 191 to a file name that reflects the testing time i.e. stats10 is for 10 minute intensity and stats20 is for 20 minute intensity
* Do the same on lines 273 and 282
* Enter the number of the first locator in line 354 ensuring you keep the +44 format for UK numbers of changing it for whatever country SIMS you are using
* On line 377 do the same for the second locator
* Modify lines 381 and 382 under minute to reflect the testing period in CRON format i.e. \*/2 is every 2 minutes, \*/4 is every 4 minutes etc

To run the tests for only 1 intensity at a time:

* Uncomment line 380 and change minute to whatever value required
* Comment out lines 381 and 382

\* Note that the output of this test will be to the stats.txt file

When doing the battery life tests take note of the time started and then use the messagelog.txt file in the log directory to indicate the last message received for that number

## Links to videos

1. Video demonstrating modified software: https://1drv.ms/f/s!Ai5iUhtvoQq51XdI-Hrl0hxFXySS
2. Video outlining the code created and modifications made, explaining what the code does: https://1drv.ms/f/s!Ai5iUhtvoQq51Xi-0AYZ9PjUpU91 
