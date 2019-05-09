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

Ext.define('Traccar.view.dialog.AllDevicesController', {
    extend: 'Ext.app.ViewController',
    alias: 'controller.alldevicescontroller',

    onSaveClick: function(button) {

        // Get userid, and all the values from the form
        var userid = Traccar.app.getUser().get('id')
        var deviceid = this.lookupReference('id').getValue();
        var name = this.lookupReference('name').getValue();
        var imei = this.lookupReference('imei').getValue();

        // Add them to the URL request to flask server
        const Http = new XMLHttpRequest();
        const url = 'http://127.0.0.1:5000/alldevices/' + name + "/" + imei + "?" + "userid=" + userid + "&deviceid=" + deviceid;
        Http.open("GET", url);
        Http.send();

        var store = Ext.getStore('AllRegDevices');
        store.load();
        this.closeView();
    }
});