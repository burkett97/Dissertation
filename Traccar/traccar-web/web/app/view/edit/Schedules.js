/*
 * Copyright 2016 - 2018 Anton Tananaev (anton@traccar.org)
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

Ext.define('Traccar.view.edit.Schedules', {
    extend: 'Traccar.view.GridPanel',
    xtype: 'schedulesView',

    requires: [
        'Traccar.view.edit.SchedulesController',
        'Traccar.view.edit.ToolbarScheduleModified'
    ],

    controller: 'schedules',
    store: 'AllSchedules',

    tbar: {
        xtype: 'editToolbarScheduleModified',
        items: [{
            xtype: 'button',
            disabled: true,
            handler: 'onGeofencesClick',
            reference: 'toolbarGeofencesButton',
            glyph: 'xf21d@FontAwesome',
            tooltip: Strings.sharedGeofences,
            tooltipType: 'title'
        }]
    },

    listeners: {
        selectionchange: 'onSelectionChange'
    },

    viewConfig: {
        enableTextSelection: true,
        getRowClass: function(record) {
            var result = '';
            if (record.get('disabled')) {
                result = 'view-item-disabled ';
            }
            return result;
        }
    },

    columns: {
        defaults: {
            flex: 1,
            minWidth: Traccar.Style.columnWidthNormal
        },
        items: [{
            text: Strings.sharedName,
            dataIndex: 'name',
            filter: 'string'
        }, {
            text: Strings.scheduledevices,
            dataIndex: 'devices',
            renderer: function(value) {
                // Gets the names of the devices
                var device, store;
                if (value == 'null') {
                    value = "None";
                } else if (value != 'null') {
                    store = Ext.getStore('AllDevices');
                    if (store.getTotalCount() === 0) {
                        store = Ext.getStore('Devices');
                    }
                    device = store.getById(value);
                    value = device.get('name');
                }
                return Ext.String.format(value);
            }
        }, {
            text: Strings.schedulegroups,
            dataIndex: 'groups',
            renderer: function(value) {
                // Gets the names of the groups
                var group, store;
                if (value !== 'null') {
                    store = Ext.getStore('AllGroups');
                    if (store.getTotalCount() === 0) {
                        store = Ext.getStore('Groups');
                    }
                    group = store.getById(value);
                    value = group.get('name');
                } else if (value == 'null') {
                    value = "None";
                }
                return Ext.String.format(value);
            }
        }, {
            text: Strings.scheduleperiod,
            dataIndex: 'period',
            filter: 'string',
            renderer: function(value, meta, record, rowIndex) {
                // Formats the data for period by capitalising
                if (value == 'customd') {
                    var days = record.get('days');
                    var daysarray = days.split(",");
                    for (var i = 0; i < daysarray.length; i++) {
                        var capvalue = daysarray[i].charAt(0).toUpperCase();
                        var capwo1 = daysarray[i].slice(1);
                        var day = capvalue + capwo1;
                        if (i == 0) {
                            value = day;
                        } else {
                            value = value + ", " + day;
                        }
                    }
                } else if (value == 'customp') {
                    var periodvalue = record.get('periodvalue');
                    var periodformat = record.get('periodformat');

                    var capform = periodformat.charAt(0).toUpperCase();
                    var formwo1 = periodformat.slice(1);
                    periodformat = capform + formwo1;

                    value = 'Every ' + periodvalue + ' ' + periodformat;
                } else {
                    var firstletter = value.charAt(0);
                    if (firstletter == "e") {
                        var pattern = /(every)(\d*)([a-z]*)/;
                        var match = value.match(pattern);
                        var capform = match[3].charAt(0).toUpperCase();
                        var formwo1 = match[3].slice(1);
                        var form = capform + formwo1;
                        value = "Every " + match[2] + " " + form;
                    }
                }
                return value;
            }
        }, {
            text: Strings.scheduletiming,
            dataIndex: 'timing',
            filter: 'string',
            renderer: function(value, meta, record, rowIndex) {
                // Formats for timing column- capitalises
                if (value == 'customh') {
                    value = record.get('hourvalue');
                } else if (value == 'customw') {
                    var fromvalue = record.get('fromvalue');
                    var timeEveryValue = record.get('timeEveryValue');
                    var timeEveryFormat = record.get('timeEveryFormat');
                    var tillvalue = record.get('tillvalue');

                    value = "Every " + timeEveryValue + " " + timeEveryFormat + ", From: " + fromvalue + ", Till: " + tillvalue;
                } else {
                    var firstletter = value.charAt(0);
                    if (firstletter == "e") {
                        var pattern = /(every)(\d*)([a-z]*)/;
                        var match = value.match(pattern);
                        var capform = match[3].charAt(0).toUpperCase();
                        var formwo1 = match[3].slice(1);
                        var form = capform + formwo1;
                        value = "Every " + match[2] + " " + form;
                    }
                }
                return value;
            }
        }, {
            text: Strings.schedulestarttime,
            dataIndex: 'startTime',
            filter: 'string'
        }, {
            text: Strings.scheduleendtime,
            dataIndex: 'endTime',
            filter: 'string'
        }, {
            xtype: 'booleancolumn',
            trueText: 'Yes',
            falseText: 'No',
            text: Strings.scheduledisabled,
            dataIndex: 'disabled',
            hidden: true,
        }]
    }
});