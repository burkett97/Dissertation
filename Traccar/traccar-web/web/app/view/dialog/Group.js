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
Ext.define('Traccar.view.dialog.Group', {
    extend: 'Traccar.view.dialog.Base',

    requires: [
        'Traccar.view.ClearableComboBox',
        'Traccar.view.dialog.GroupController',
        'Ext.picker.Color',
    ],

    title: Strings.groupDialog,
    controller: 'groupcontrol',

    items: {
        xtype: 'form',
        items: [{
            xtype: 'textfield',
            reference: 'groupid',
            name: 'id',
            hidden: true,
        }, {
            xtype: 'fieldset',
            title: Strings.sharedRequired,
            items: [{
                xtype: 'textfield',
                name: 'name',
                reference: 'name',
                fieldLabel: Strings.sharedName,
                allowBlank: false
            }]

        }, {
            xtype: 'fieldset',
            title: Strings.sharedExtra,
            collapsible: true,
            collapsed: true,
            items: [{
                xtype: 'clearableComboBox',
                name: 'groupId',
                fieldLabel: Strings.groupParent,
                store: 'Groups',
                queryMode: 'local',
                displayField: 'name',
                valueField: 'id'
            }, {
                xtype: 'fieldcontainer',
                name: 'colourdisplay',
                reference: 'colourdisplay',
                fieldLabel: Strings.groupColour,
                items: [{
                    xtype: 'displayfield',
                    editable: false,
                    name: 'groupcolour',
                    id: 'groupcolour',
                    reference: 'groupcolour',
                }, {
                    xtype: 'colorpicker',
                    fieldLabel: '',
                    name: 'groupColour',
                    reference: 'groupColour',
                    handler: function(value) {
                        Ext.getCmp('groupcolour').setValue(this.value);
                    },
                }]
            }]
        }]
    },

    buttons: [{
        text: Strings.sharedAttributes,
        handler: 'showAttributesView'
    }, {
        xtype: 'tbfill'
    }, {
        glyph: 'xf00c@FontAwesome',
        reference: 'saveButton',
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