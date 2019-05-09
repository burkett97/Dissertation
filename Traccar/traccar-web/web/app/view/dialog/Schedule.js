/*
 * Copyright 2016 - 2017 Anton Tananaev (anton@traccar.org)
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

Ext.define('Traccar.view.dialog.Schedule', {
    extend: 'Traccar.view.dialog.Base',

    requires: [
        'Traccar.view.dialog.ScheduleController',
        'Traccar.view.ClearableComboBox',
        'Traccar.view.CustomTimeField'
    ],

    title: Strings.scheduleDialog,
    controller: 'schedulecontrol',

    items: {
        xtype: 'form',
        items: [{
            xtype: 'fieldset',
            title: Strings.sharedRequired,
            items: [{
                xtype: 'textfield',
                reference: 'scheduleid',
                name: 'id',
                hidden: true,
            }, {
                xtype: 'textfield',
                reference: 'schedulename',
                name: 'name',
                fieldLabel: Strings.sharedName,
                allowBlank: false,
            }]
        }, {
            xtype: 'fieldset',
            title: Strings.sharedExtra,
            collapsible: true,
            collapsed: true,
            items: [{
                xtype: 'tagfield',
                maxWidth: Traccar.Style.formFieldWidth,
                name: 'devices',
                reference: 'deviceId',
                fieldLabel: Strings.deviceParent,
                store: 'Devices',
                queryMode: 'local',
                displayField: 'name',
                valueField: 'id'
            }, {
                xtype: 'tagfield',
                maxWidth: Traccar.Style.formFieldWidth,
                name: 'groups',
                reference: 'groupId',
                fieldLabel: Strings.groupParent,
                store: 'Groups',
                queryMode: 'local',
                displayField: 'name',
                valueField: 'id'
            }, {
                // PERIOD -------------
                fieldLabel: Strings.schedulePeriod,
                reference: 'periodField',
                name: 'period',
                xtype: 'combobox',
                store: 'SchedulePeriods',
                editable: false,
                valueField: 'key',
                displayField: 'name',
                queryMode: 'local',
                listeners: {
                    change: 'onPeriodChange',
                }
            }, {
                fieldLabel: Strings.schedulePeriodDays,
                reference: 'periodDayField',
                xtype: 'tagfield',
                maxWidth: Traccar.Style.formFieldWidth,
                name: 'days',
                store: 'SchedulePeriodsDays',
                queryMode: 'local',
                displayField: 'name',
                valueField: 'key',
                hidden: true,
                fieldLabel: Strings.schedulePeriodDays
            }, {
                xtype: 'fieldcontainer',
                reference: 'everyField',
                hidden: true,
                fieldLabel: Strings.schedulePeriodEvery,
                items: [{
                    xtype: 'numberfield',
                    reference: 'everyValue',
                    name: 'periodvalue',
                    minValue: 1,
                    maxValue: 60
                }, {
                    xtype: 'clearableComboBox',
                    fieldLabel: '',
                    name: 'periodformat',
                    reference: 'everyFormat',
                    store: 'SchedulePeriodsFormat',
                    displayField: 'name',
                    valueField: 'key',
                }]
            }, {
                // TIMING -------------
                fieldLabel: Strings.scheduleTiming,
                reference: 'timingField',
                xtype: 'combobox',
                name: 'timing',
                store: 'ScheduleTimings',
                valueField: 'key',
                displayField: 'name',
                queryMode: 'local',
                listeners: {
                    change: 'onTimingChange'
                }
            }, {
                xtype: 'customTimeField',
                hidden: true,
                reference: 'timingHourTimeField',
                value: new Date(),
                name: 'hourvalue',
                fieldLabel: Strings.scheduleTimingHour
            }, {
                xtype: 'customTimeField',
                reference: 'timingFromField',
                hidden: true,
                value: new Date(),
                name: 'fromvalue',
                fieldLabel: Strings.scheduletimeFrom
            }, {
                xtype: 'fieldcontainer',
                reference: 'timingEveryField',
                hidden: true,
                fieldLabel: Strings.schedulePeriodEvery,
                items: [{
                    xtype: 'numberfield',
                    name: 'timeEveryValue',
                    reference: 'timeEveryValue',
                    minValue: 1,
                    maxValue: 60,
                }, {
                    xtype: 'clearableComboBox',
                    fieldLabel: '',
                    name: 'timeEveryFormat',
                    reference: 'timeEveryFormat',
                    store: 'ScheduleTimingsFormat',
                    displayField: 'name',
                    valueField: 'key'
                }]
            }, {
                xtype: 'customTimeField',
                reference: 'timingTillField',
                hidden: true,
                value: new Date(),
                name: 'tillvalue',
                fieldLabel: Strings.scheduletimeTill
            }, {
                xtype: 'fieldcontainer',
                layout: 'vbox',
                reference: 'startonContainer',
                fieldLabel: Strings.scheduleStartingOn,
                items: [{
                    xtype: 'datefield',
                    reference: 'fromDateField',
                    name: 'startDate',
                    startDay: Traccar.Style.weekStartDay,
                    format: Traccar.Style.dateFormat,
                    minValue: new Date(),
                    value: new Date()
                }, {
                    xtype: 'customTimeField',
                    name: 'startTime',
                    reference: 'fromTimeField',
                    value: new Date()
                }]
            }, {
                xtype: 'fieldcontainer',
                layout: 'vbox',
                reference: 'endonContainer',
                fieldLabel: Strings.scheduleEndingOn,
                items: [{
                    xtype: 'datefield',
                    reference: 'toDateField',
                    name: 'endDate',
                    startDay: Traccar.Style.weekStartDay,
                    format: Traccar.Style.dateFormat,
                    minValue: new Date(),
                    value: new Date(new Date().getTime() + 30 * 60 * 1000)
                }, {
                    xtype: 'customTimeField',
                    reference: 'toTimeField',
                    name: 'endTime',
                    value: new Date(new Date().getTime() + 30 * 60 * 1000)
                }]
            }, {
                xtype: 'checkboxfield',
                inputValue: true,
                uncheckedValue: false,
                name: 'disabled',
                fieldLabel: Strings.sharedDisabled,
                reference: 'disabledField'
            }]
        }]
    },
    buttons: [{
        glyph: 'xf00c@FontAwesome',
        tooltip: Strings.sharedSave,
        tooltipType: 'title',
        minWidth: 0,
        handler: 'onSaveClick'
    }, {
        glyph: 'xf00d@FontAwesome',
        tooltip: Strings.sharedCancel,
        tooltipType: 'title',
        minWidth: 0,
        handler: 'closeView'
    }]
});