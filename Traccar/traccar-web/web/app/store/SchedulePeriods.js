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

Ext.define('Traccar.store.SchedulePeriods', {
    extend: 'Ext.data.Store',
    fields: ['key', 'name'],

    data: [{
        key: 'customd',
        name: Strings.scheduleperiodCustomDay
    }, {
        key: 'customp',
        name: Strings.scheduleperiodCustomPeriod
    }, {
        key: 'every1days',
        name: Strings.scheduleperiodEveryday
    }, {
        key: 'every2days',
        name: Strings.scheduleperiodEvery2days
    }, {
        key: 'every3days',
        name: Strings.scheduleperiodEvery3days
    }, {
        key: 'every1weeks',
        name: Strings.scheduleperiodEveryWeek
    }, {
        key: 'every2weeks',
        name: Strings.scheduleperiodEvery2Weeks
    }]
});