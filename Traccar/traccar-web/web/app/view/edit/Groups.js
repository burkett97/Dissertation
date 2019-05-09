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

Ext.define('Traccar.view.edit.Groups', {
    extend: 'Traccar.view.GridPanel',
    xtype: 'groupsView',

    requires: [
        'Traccar.AttributeFormatter',
        'Traccar.view.edit.GroupsController',
        'Traccar.view.edit.Toolbar'
    ],

    controller: 'groups',
    store: 'Groups',

    tbar: {
        xtype: 'editToolbar',
        items: [{
            xtype: 'button',
            disabled: true,
            handler: 'onGeofencesClick',
            reference: 'toolbarGeofencesButton',
            glyph: 'xf21d@FontAwesome',
            tooltip: Strings.sharedGeofences,
            tooltipType: 'title'
        }, {
            xtype: 'button',
            disabled: true,
            handler: 'onAttributesClick',
            reference: 'toolbarAttributesButton',
            glyph: 'xf0ae@FontAwesome',
            tooltip: Strings.sharedComputedAttributes,
            tooltipType: 'title'
        }, {
            xtype: 'button',
            disabled: true,
            handler: 'onDriversClick',
            reference: 'toolbarDriversButton',
            glyph: 'xf084@FontAwesome',
            tooltip: Strings.sharedDrivers,
            tooltipType: 'title'
        }, { /* Locator button added by Jack changing reference to deviceLocateButton disables the button therefore, the locate button takes the place of command*/
            handler: 'onLocateClick',
            reference: 'toolbarCommandsButton',
            glyph: 'xf14e@FontAwesome',
            tooltip: Strings.deviceLocate
        }, {
            //     xtype: 'button',
            //     disabled: true,
            //     handler: 'onCommandsClick',
            //     reference: 'toolbarCommandsButton',
            //     glyph: 'xf093@FontAwesome',
            //     tooltip: Strings.sharedSavedCommands,
            //     tooltipType: 'title'
            // }, {
            xtype: 'button',
            disabled: true,
            handler: 'onNotificationsClick',
            reference: 'toolbarNotificationsButton',
            glyph: 'xf003@FontAwesome',
            tooltip: Strings.sharedNotifications,
            tooltipType: 'title'
        }, {
            xtype: 'button',
            disabled: true,
            handler: 'onMaintenancesClick',
            reference: 'toolbarMaintenancesButton',
            glyph: 'xf0ad@FontAwesome',
            tooltip: Strings.sharedMaintenance,
            tooltipType: 'title'
        }]
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
            text: Strings.groupColour,
            dataIndex: 'groupcolour',
            filter: 'string',
            renderer: function(value, meta) {
                var coloursforwhitetext = ['000000', '993300', '333300', '003300', '003366', '000080', '333399', '333333', '800000', '808000', '008000',
                    '008080', '0000FF', '666699', '808080', '339966', '3366FF', '800080', '969696', '993366'
                ];
                if (coloursforwhitetext.includes(value)) {
                    textcolour = 'color: white;';
                } else {
                    textcolour = 'color: black;';
                }
                meta.style = 'background-color: #' + value + ';' + textcolour;
                return value;
            }
        }, {
            text: Strings.groupDialog,
            dataIndex: 'groupId',
            hidden: true,
            filter: {
                type: 'list',
                labelField: 'name',
                store: 'AllGroups'
            },
            renderer: Traccar.AttributeFormatter.getFormatter('groupId')
        }]
    }
});