/*
 * Copyright 2015 - 2017 Anton Tananaev (anton@traccar.org)
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

Ext.define('Traccar.view.edit.Devices', {
    extend: 'Traccar.view.GridPanel',
    xtype: 'devicesView',

    requires: [
        'Traccar.AttributeFormatter',
        'Traccar.view.edit.DevicesController',
        'Traccar.view.ArrayListFilter',
        'Traccar.view.DeviceMenu'
    ],

    controller: 'devices',

    store: 'Devices',

    stateful: true,
    stateId: 'devices-grid',

    tbar: {
        componentCls: 'toolbar-header-style',
        defaults: {
            xtype: 'button',
            disabled: true,
            tooltipType: 'title'
        },
        items: [{
            xtype: 'tbtext',
            html: Strings.deviceTitle,
            baseCls: 'x-panel-header-title-default'
        }, {
            xtype: 'tbfill',
            disabled: false
        }, {
            handler: 'onAddClick',
            reference: 'toolbarAddButton',
            glyph: 'xf067@FontAwesome',
            tooltip: Strings.sharedAdd
        }, {
            handler: 'onEditClick',
            reference: 'toolbarEditButton',
            glyph: 'xf040@FontAwesome',
            tooltip: Strings.sharedEdit
        }, {
            handler: 'onRemoveClick',
            reference: 'toolbarRemoveButton',
            glyph: 'xf00d@FontAwesome',
            tooltip: Strings.sharedRemove
        }, { /* Locator button added by Jack changing reference to deviceLocateButton disables the button therefore, the locate button takes the place of command*/
            handler: 'onLocateClick',
            reference: 'deviceCommandButton',
            glyph: 'xf14e@FontAwesome',
            tooltip: Strings.deviceLocate
        }, {
            // Command button disabled by Jack and locate button takes it place
            // handler: 'onCommandClick',
            // reference: 'deviceCommandButton',
            // glyph: 'xf093@FontAwesome',
            // tooltip: Strings.deviceCommand
            // }, {
            xtype: 'deviceMenu',
            reference: 'toolbarDeviceMenu',
            enableToggle: false
        }]
    },

    listeners: {
        rowclick: 'onSelectionChange',
        itemkeyup: 'onSelectionChange'
    },

    // // Temporarily disabled the online, offline and unknown status colours
    viewConfig: {
        enableTextSelection: true,
        getRowClass: function(record) {
            var result = '';
            // status = record.get('status');
            if (record.get('disabled')) {
                result = 'view-item-disabled ';
            }
            // if (status) {
            //     result += Ext.getStore('DeviceStatuses').getById(status).get('color');
            // }
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
                text: Strings.deviceIdentifier,
                dataIndex: 'uniqueId',
                hidden: true,
                filter: 'string'
            }, {
                text: Strings.sharedPhone,
                dataIndex: 'phone',
                hidden: true
            }, {
                text: Strings.deviceModel,
                dataIndex: 'model',
                hidden: true
            }, {
                text: Strings.deviceContact,
                dataIndex: 'contact',
                hidden: true
            }, {
                text: Strings.groupDialog,
                dataIndex: 'groupId',
                // hidden: true,
                filter: {
                    type: 'list',
                    labelField: 'name',
                    store: 'Groups'
                },
                // renderer: Traccar.AttributeFormatter.getFormatter('groupId')
                renderer: function(value, meta, store, record) {
                    var group, store;
                    if (value > 0) {
                        var groupcolour = Ext.getStore('Groups').getById(value).get('groupcolour');
                        var coloursforwhitetext = ['000000', '993300', '333300', '003300', '003366', '000080', '333399', '333333', '800000', '808000', '008000',
                            '008080', '0000FF', '666699', '808080', '339966', '3366FF', '800080', '969696', '993366'
                        ];
                        if (groupcolour != null) {
                            if (coloursforwhitetext.includes(groupcolour)) {
                                textcolour = 'color: white;';
                            } else {
                                textcolour = 'color: black;';
                            }
                            meta.style = 'background-color: #' + groupcolour + ';' + textcolour;
                        }
                        store = Ext.getStore('AllGroups');
                        if (store.getTotalCount() === 0) {
                            store = Ext.getStore('Groups');
                        }
                        group = store.getById(value);
                        return group ? group.get('name') : value;
                    }
                    return null;
                }
            },
            {
                text: Strings.sharedDisabled,
                dataIndex: 'disabled',
                renderer: Traccar.AttributeFormatter.getFormatter('disabled'),
                hidden: true,
                filter: 'boolean'
            },
            {
                text: Strings.sharedGeofences,
                dataIndex: 'geofenceIds',
                hidden: true,
                filter: {
                    type: 'arraylist',
                    idField: 'id',
                    labelField: 'name',
                    store: 'Geofences'
                },
                renderer: function(value) {
                    var i, name, result = '';
                    if (Ext.isArray(value)) {
                        for (i = 0; i < value.length; i++) {
                            name = Traccar.AttributeFormatter.geofenceIdFormatter(value[i]);
                            if (name) {
                                result += name + (i < value.length - 1 ? ', ' : '');
                            }
                        }
                    }
                    return result;
                }
            },
            {
                text: Strings.deviceLastUpdate,
                dataIndex: 'lastUpdate',
                filter: 'string',
            },
            {
                text: Strings.deviceStatus,
                dataIndex: 'status',
                renderer: function(value, meta, record, rowIndex) {
                    var status, id, battery;
                    battery = record.get('battery');
                    if (battery > 15) {
                        id = 'online';
                    } else if (battery < 15 && battery > 5) {
                        id = 'lowbattery';
                    } else if (battery < 5 && battery != 0) {
                        id = 'criticalbattery';
                    } else if (battery == 0) {
                        id = 'unknown';
                    }
                    status = Ext.getStore('DeviceStatuses').getById(id);
                    colour = Ext.getStore('DeviceStatuses').getById(id).get('color');
                    meta.style = 'background-color:' + colour + ';';

                    if (status) {
                        return status.get('name');
                    }
                    return null;
                }
            },
            {
                text: Strings.deviceBattery,
                dataIndex: 'battery',
                filter: 'string',
            }
        ]
    }
});