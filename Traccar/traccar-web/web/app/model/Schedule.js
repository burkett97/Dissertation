/*
 * Copyright 2016 Anton Tananaev (anton@traccar.org)
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

Ext.define('Traccar.model.Schedule', {
    extend: 'Ext.data.Model',
    identifier: 'negative',

    fields: [{
        name: 'id',
        type: 'int'
    }, {
        name: 'name',
        type: 'string'
    }, {
        name: 'devices',
        type: 'string'
    }, {
        name: 'groups',
        type: 'string'
    }, {
        name: 'period',
        type: 'string'
    }, {
        name: 'days',
        type: 'string'
    }, {
        name: 'periodvalue',
        type: 'string'
    }, {
        name: 'periodformat',
        type: 'string'
    }, {
        name: 'timing',
        type: 'string'
    }, {
        name: 'hourvalue',
        type: 'string'
    }, {
        name: 'fromvalue',
        type: 'string'
    }, {
        name: 'timeEveryValue',
        type: 'string'
    }, {
        name: 'timeEveryFormat',
        type: 'string'
    }, {
        name: 'tillvalue',
        type: 'string'
    }, {
        name: 'startDate',
        type: 'date',
        dateFormat: 'c'
    }, {
        name: 'startTime',
        type: 'date',
        dateFormat: 'c'
    }, {
        name: 'endDate',
        type: 'date',
        dateFormat: 'c'
    }, {
        name: 'endTime',
        type: 'date',
        dateFormat: 'c'
    }, {
        name: 'disabled',
        type: 'boolean'
    }]
});