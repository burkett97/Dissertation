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

Ext.define('Traccar.view.edit.AllDevices', {
    extend: 'Traccar.view.GridPanel',
    xtype: 'alldevicesView',

    requires: [
        'Traccar.view.edit.AllDevicesController',
        'Traccar.view.edit.ToolbarAllDevicesModified'
    ],

    controller: 'alldevices',
    store: 'AllRegDevices',

    tbar: {
        xtype: 'editToolbarAllDevicesModified',
        // items: [{
        //     xtype: 'button',
        //     disabled: true,
        //     handler: 'onMakeActiveClick',
        //     reference: 'toolbarActiveButton',
        //     glyph: 'xf0a9@FontAwesome',
        //     tooltip: Strings.alldevicesMakeActive,
        //     tooltipType: 'title'
        // }]
    },

    listeners: {
        selectionchange: 'onSelectionChange'
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
            text: Strings.adID,
            dataIndex: 'loc_id',
            filter: 'string'
        }, {
            text: Strings.adIMEI,
            dataIndex: 'imei',
            filter: 'string'
        }]
    }
});