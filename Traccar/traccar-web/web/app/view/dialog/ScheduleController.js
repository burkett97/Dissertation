/*
 * Copyright 2016 - 2017 Anton Tananaev (anton@traccar.org)
 * Copyright 2016 - 2017 Andrey Kunitsyn (andrey@traccar.org)
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */

Ext.define('Traccar.view.dialog.ScheduleController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.schedulecontrol',

    onSaveClick: function(button) {

        var message, valid = true,
            errormessages = [];

        // **** USER ID ****
        var userid = Traccar.app.getUser().get('id');

        // **** SCHEDULE ID ****        
        var scheduleid = this.lookupReference('scheduleid').getValue();

        // **** SCHEDULE NAME ****        
        var schedulename = this.lookupReference('schedulename').getValue();

        // Check name isn't empty
        if (schedulename == '') {
            valid = false;
            message = "Name cannot be empty \n";
            errormessages.push(message);
        }

        // **** DEVICES ****
        var device = this.lookupReference('deviceId').getValue();
        // If devices are empty set to null
        if (device == '') {
            device = "null";
        }

        // **** GROUPS ****
        var group = this.lookupReference('groupId').getValue();
        // If groups are empty set to null
        if (group == "") {
            group = "null";
        }

        // ***** DEVICES & GROUPS VALIDATION *****
        // Check a device or group has been selected
        if (device == 'null' && group == 'null') {
            valid = false;
            message = "A Device or/and Group must be selected";
            errormessages.push(message);
        }

        // ***** PERIOD *****
        var period, everyValue, everyFormat;
        var periodfield = this.lookupReference('periodField').getValue();

        // Get values from specific fields depending on period field value
        if (periodfield == 'customd') {
            period = this.lookupReference('periodDayField').getValue();

            // Check if day field isn't empty
            if (period == null) {
                valid = false;
                message = "Day field cannot be empty";
                errormessages.push(message);
            }

        } else if (periodfield == 'customp') {
            everyValue = this.lookupReference('everyValue').getValue();
            everyFormat = this.lookupReference('everyFormat').getValue();
            period = "every" + everyValue + everyFormat;

            if (everyValue == null || everyFormat == null) {
                valid = false;
                message = "All period fields must be completed";
                errormessages.push(message);
            }

        } else if (periodfield != null) {
            period = periodfield;

        } else if (periodfield == null) { // Check period isn't empty
            valid = false;
            message = "Period cannot be empty";
            errormessages.push(message);
        }

        // ***** TIMING *****
        var timing, from, timeEveryValue, timeEveryFormat, till;
        var timingfield = this.lookupReference('timingField').getValue();

        // Get values from specific fields depending on timing field value
        if (timingfield == 'customh') {
            timing = this.lookupReference('timingHourTimeField').getValue();

            // Check hour field isn't empty
            if (timing == null) {
                valid = false;
                message = "Hour field cannot be empty";
                errormessages.push(message);
            }

        } else if (timingfield == 'customw') {
            from = this.lookupReference('timingFromField').getValue();
            from = from.getHours() + ":" + from.getMinutes();
            timeEveryValue = this.lookupReference('timeEveryValue').getValue();
            timeEveryFormat = this.lookupReference('timeEveryFormat').getValue();
            till = this.lookupReference('timingTillField').getValue();
            till = till.getHours() + ":" + till.getMinutes();
            timing = from + ";" + timeEveryValue + timeEveryFormat + ";" + till;

            // Check from, every, format or till field aren't empty
            if (from == null || timeEveryValue == null || timeEveryFormat == null || till == null) {
                valid = false;
                message = "All timing fields must be completed";
                errormessages.push(message);
            }

        } else if (timingfield != null) {
            timing = timingfield;
        } else if (timingfield == null) { // Check timing isn't empty
            valid = false;
            message = "Timing cannot be empty";
            errormessages.push(message);
        }

        // **** START DATE AND TIME ****
        var startingfield = this.lookupReference('fromDateField').getValue();
        var startingdate = startingfield.getFullYear() + '-' + ((('0' + (startingfield.getMonth() + 1)).slice(-2))) + '-' + (('0' + startingfield.getDate()).slice(-2));
        var startingtime = this.lookupReference('fromTimeField').getValue();
        startingtime = (('0' + startingtime.getHours()).slice(-2)) + ":" + (('0' + startingtime.getMinutes()).slice(-2));

        var starting = startingdate + "_" + startingtime;

        // **** END DATE AND TIME ****

        var endingfield = this.lookupReference('toDateField').getValue();
        var endingdate = endingfield.getFullYear() + '-' + ((('0' + (endingfield.getMonth() + 1)).slice(-2))) + '-' + (('0' + endingfield.getDate()).slice(-2));
        var endingtime = this.lookupReference('toTimeField').getValue();
        endingtime = (('0' + endingtime.getHours()).slice(-2)) + ":" + (('0' + endingtime.getMinutes()).slice(-2));

        var ending = endingdate + "_" + endingtime;

        // **** DISABLED ****
        var disabled = this.lookupReference('disabledField').getValue();

        // Check starting date and time aren't empty
        if (startingdate == null || startingtime == null) {
            valid = false;
            message = "Starting date and time cannot be empty";
            errormessages.push(message);
        }
        // Check ending date and time aren't empty
        if (endingdate == null || endingtime == null) {
            valid = false;
            message = "Ending date and time cannot be empty";
            errormessages.push(message);
        }
        // Check that ending date is after or equal to starting date
        if (new Date(startingdate) > new Date(endingdate)) {
            valid = false;
            message = "Ending date must be after starting date";
            errormessages.push(message);
        }
        // If ending date is same as starting date, make sure end time is after start time     
        if (new Date(startingdate) == new Date(endingdate)) {
            if (new Date(startingtime) > new Date(endingtime)) {
                valid = false;
                message = "Ending time must be after starting date";
                errormessages.push(message);
            }
        }

        var today = new Date();
        var date = today.getFullYear() + '-' + (today.getMonth() + 1) + '-' + today.getDate();
        var time = today.getHours() + ":" + today.getMinutes();

        if (date == startingdate && time >= startingtime) {
            console.log(date)
        }

        if (valid == true) {
            const Http = new XMLHttpRequest();
            const url = 'http://127.0.0.1:5000/scheduleadd/' + userid + "/" + schedulename + "/" + device + "/" + group + "/" + period + "/" + timing + "/" + starting + "/" + ending + "/" + disabled + "?" + "scheduleid=" + scheduleid;
            Http.open("GET", url);
            Http.send();

            var store = Ext.getStore('AllSchedules');
            store.load();
            this.closeView();
        } else {
            Ext.Msg.alert("Error", errormessages.join('<br/>'));
        }
    },

    // Shows and hides the relevant period fields when required
    onPeriodChange: function(combobox, newValue) {
        var custom = newValue;

        switch (newValue) {
            case 'customd':
                this.lookupReference('periodDayField').setHidden(false);
                this.lookupReference('everyField').setHidden(true);
                break;
            case 'customp':
                this.lookupReference('periodDayField').setHidden(true);
                this.lookupReference('everyField').setHidden(false);
                break;
            case 'every1days':
                this.lookupReference('periodDayField').setHidden(true);
                this.lookupReference('everyField').setHidden(true);
                break;
            case 'every2days':
                this.lookupReference('periodDayField').setHidden(true);
                this.lookupReference('everyField').setHidden(true);
                break;
            case 'every3days':
                this.lookupReference('periodDayField').setHidden(true);
                this.lookupReference('everyField').setHidden(true);
                break;
            case 'every1weeks':
                this.lookupReference('periodDayField').setHidden(true);
                this.lookupReference('everyField').setHidden(true);
                break;
            case 'every2weeks':
                this.lookupReference('periodDayField').setHidden(true);
                this.lookupReference('everyField').setHidden(true);
                break;
            default:
                this.lookupReference('periodDayField').setHidden(true);
                this.lookupReference('everyField').setHidden(true);
                break;
        }
    },

    // Shows and hides the relevant timing fields when required
    onTimingChange: function(combobox, newValue) {
        var timing, custom = newValue;

        switch (newValue) {
            case 'customh':
                this.lookupReference('timingHourTimeField').setHidden(false);
                this.lookupReference('timingFromField').setHidden(true);
                this.lookupReference('timingEveryField').setHidden(true);
                this.lookupReference('timingTillField').setHidden(true);
                break;
            case 'customw':
                this.lookupReference('timingHourTimeField').setHidden(true);
                this.lookupReference('timingFromField').setHidden(false);
                this.lookupReference('timingEveryField').setHidden(false);
                this.lookupReference('timingTillField').setHidden(false);
                break;
            case 'every5mins':
                this.lookupReference('timingHourTimeField').setHidden(true);
                this.lookupReference('timingFromField').setHidden(true);
                this.lookupReference('timingEveryField').setHidden(true);
                this.lookupReference('timingTillField').setHidden(true);
                break;
            case 'every10mins':
                this.lookupReference('timingHourTimeField').setHidden(true);
                this.lookupReference('timingFromField').setHidden(true);
                this.lookupReference('timingEveryField').setHidden(true);
                this.lookupReference('timingTillField').setHidden(true);
                break;
            case 'every30mins':
                this.lookupReference('timingHourTimeField').setHidden(true);
                this.lookupReference('timingFromField').setHidden(true);
                this.lookupReference('timingEveryField').setHidden(true);
                this.lookupReference('timingTillField').setHidden(true);
                break;
            case 'every1hr':
                this.lookupReference('timingHourTimeField').setHidden(true);
                this.lookupReference('timingFromField').setHidden(true);
                this.lookupReference('timingEveryField').setHidden(true);
                this.lookupReference('timingTillField').setHidden(true);
                break;
            case 'every2hrs':
                this.lookupReference('timingHourTimeField').setHidden(true);
                this.lookupReference('timingFromField').setHidden(true);
                this.lookupReference('timingEveryField').setHidden(true);
                this.lookupReference('timingTillField').setHidden(true);
                break;
            default:
                this.lookupReference('timingHourTimeField').setHidden(true);
                this.lookupReference('timingFromField').setHidden(true);
                this.lookupReference('timingEveryField').setHidden(true);
                this.lookupReference('timingTillField').setHidden(true);
                break;
        }
    }
});