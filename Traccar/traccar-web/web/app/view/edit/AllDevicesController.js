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

Ext.define('Traccar.view.edit.AllDevicesController', {
    extend: 'Traccar.view.edit.ToolbarAllDevicesModifiedController',
    alias: 'controller.alldevices',

    requires: [
        'Traccar.view.dialog.AllDevices',
        'Traccar.view.permissions.Devices',
        'Traccar.view.BaseWindow',
    ],

    objectModel: 'Traccar.model.AllDevices',
    objectDialog: 'Traccar.view.dialog.AllDevices',

    // ** Not in use at the moment
    // onMakeActiveClick: function() {
    //     var device = this.getView().getSelectionModel().getSelection()[0];
    //     Ext.getStore('AllDevices').load();
    //     Ext.create('Traccar.view.BaseWindow', {
    //         title: Strings.deviceTitle,
    //         items: {
    //             xtype: 'devicedialogView'
    //         }
    //     }).show();
    // },

    onSelectionChange: function(selection, selected) {
        var disabled = selected.length === 0;
        // this.lookupReference('toolbarActiveButton').setDisabled(disabled);
        this.callParent(arguments);
    }
});