/*
 * Copyright 2017 Anton Tananaev (anton@traccar.org)
 * Copyright 2017 Andrey Kunitsyn (andrey@traccar.org)
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
Ext.define('Traccar.view.edit.ToolbarAllDevicesModifiedController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.toolbaralldevicesmodifiedController',

    onAddClick: function() {
        var dialog, objectInstance = Ext.create(this.objectModel);
        objectInstance.store = this.getView().getStore();
        if (objectInstance.store instanceof Ext.data.ChainedStore) {
            objectInstance.store = objectInstance.store.getSource();
        }
        dialog = Ext.create(this.objectDialog);
        dialog.down('form').loadRecord(objectInstance);
        dialog.show();
    },

    onEditClick: function() {
        var dialog, objectInstance = this.getView().getSelectionModel().getSelection()[0];
        dialog = Ext.create(this.objectDialog);
        var record = dialog.down('form').loadRecord(objectInstance);
        console.log(record);
        dialog.down('form').loadRecord(objectInstance);
        dialog.show();
    },

    onRemoveClick: function() {
        var device = this.getView().getSelectionModel().getSelection()[0];
        var deviceid = device.get('id');
        var userid = Traccar.app.getUser().get('id');

        Ext.Msg.confirm("Device", "Remove item", function(btn) {
            if (btn === 'yes') {
                const Http = new XMLHttpRequest();
                const url = 'http://127.0.0.1:5000/removedevice/' + deviceid + "?" + "id=" + userid;
                Http.open("GET", url);
                Http.send();
                var store = Ext.getStore('AllRegDevices');
                store.load();
            }
        });
    },

    onSelectionChange: function(selection, selected) {
        var disabled = selected.length === 0;
        this.lookupReference('toolbarEditButton').setDisabled(disabled);
        this.lookupReference('toolbarRemoveButton').setDisabled(disabled);
    }
});