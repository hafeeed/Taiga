# Copyright (C) 2014 Andrey Antukh <niwi@niwi.be>
# Copyright (C) 2014 Jesús Espino <jespinog@gmail.com>
# Copyright (C) 2014 David Barragán <bameda@dbarragan.com>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys
from django.apps import AppConfig
from django.db.models import signals

from . import signal_handlers as handlers


def connect_events_signals():
    signals.post_save.connect(handlers.on_save_any_model, dispatch_uid="events_change")
    signals.post_delete.connect(handlers.on_delete_any_model, dispatch_uid="events_delete")


def disconnect_events_signals():
    signals.post_save.disconnect(dispatch_uid="events_change")
    signals.post_delete.disconnect(dispatch_uid="events_delete")


class EventsAppConfig(AppConfig):
    name = "taiga.events"
    verbose_name = "Events App Config"

    def ready(self):
        connect_events_signals()
