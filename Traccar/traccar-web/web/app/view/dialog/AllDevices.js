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

Ext.define('Traccar.view.dialog.AllDevices', {
    extend: 'Traccar.view.dialog.Base',

    requires: [
        'Traccar.view.ClearableComboBox',
        'Traccar.view.dialog.AllDevicesController'
    ],

    title: Strings.alldevicesDialog,
    controller: 'alldevicescontroller',

    items: {
        xtype: 'form',
        items: [{
            xtype: 'fieldset',
            title: Strings.sharedRequired,
            items: [{
                xtype: 'textfield',
                name: 'id',
                reference: 'id',
                hidden: true,
            }, {
                xtype: 'displayfield',
                name: 'loc_id',
                reference: 'loc_id',
                id: 'loc_id',
                fieldLabel: Strings.adID,
            }, {
                xtype: 'textfield',
                name: 'name',
                reference: 'name',
                fieldLabel: Strings.adName,
                allowBlank: false
            }, {
                xtype: 'numberfield',
                name: 'imei',
                reference: 'imei',
                id: 'imei',
                maxLength: '15',
                fieldLabel: Strings.adIMEI,
                allowBlank: false
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