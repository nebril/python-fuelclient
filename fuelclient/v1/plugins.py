#    Copyright 2015 Mirantis, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from fuelclient import objects
from fuelclient.v1 import base_v1


class PluginsClient(base_v1.BaseV1Client):

    _entity_wrapper = objects.Plugins

    def sync(self, ids):
        """Synchronise plugins on file system with plugins in API service.

        :param ids: List of ids for filtering plugins
        :type ids: list
        """

        self._entity_wrapper.sync(plugin_ids=ids)


def get_client():
    return PluginsClient()
