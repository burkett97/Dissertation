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

Ext.define('Traccar.view.edit.SchedulesController', {
    extend: 'Traccar.view.edit.ToolbarScheduleModifiedController',
    alias: 'controller.schedules',

    requires: [
        'Traccar.view.dialog.Schedule',
        'Traccar.view.permissions.Geofences',
        'Traccar.view.BaseWindow',
        'Traccar.model.Schedule'
    ],

    objectModel: 'Traccar.model.Schedule',
    objectDialog: 'Traccar.view.dialog.Schedule',
    removeTitle: Strings.scheduleDialog,


    onSelectionChange: function(selection, selected) {
        var disabled = selected.length === 0;
        // this.lookupReference('toolbarGeofencesButton').setDisabled(disabled);
        this.callParent(arguments);
    }
});