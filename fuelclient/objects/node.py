#    Copyright 2014 Mirantis, Inc.
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

from operator import attrgetter
import os

from fuelclient.cli.error import InvalidDirectoryException
from fuelclient.objects.base import BaseObject
from fuelclient.objects.environment import Environment


class Node(BaseObject):

    class_api_path = "nodes/"
    instance_api_path = "nodes/{0}/"

    attributes_urls = {
        "interfaces": ("interfaces", "default_assignment"),
        "disks": ("disks", "defaults")
    }

    @property
    def env_id(self):
        return self.get_fresh_data()["cluster"]

    @property
    def env(self):
        return Environment(self.env_id)

    def get_attributes_path(self, directory):
        return os.path.join(
            os.path.abspath(
                os.curdir if directory is None else directory),
            "node_{0}".format(self.id)
        )

    def is_finished(self, latest=True):
        if latest:
            data = self.get_fresh_data()
        else:
            data = self.data
        return data["status"] in ("ready", "error")

    @property
    def progress(self):
        data = self.get_fresh_data()
        return data["progress"]

    @property
    def labels(self):
        return self.get_fresh_data().get('labels', {})

    def get_attribute_default_url(self, attributes_type):
        url_path, default_url_path = self.attributes_urls[attributes_type]
        return "nodes/{0}/{1}/{2}".format(self.id, url_path, default_url_path)

    def get_attribute_url(self, attributes_type):
        url_path, _ = self.attributes_urls[attributes_type]
        return "nodes/{0}/{1}/".format(self.id, url_path)

    def get_default_attribute(self, attributes_type):
        return self.connection.get_request(
            self.get_attribute_default_url(attributes_type)
        )

    def get_attribute(self, attributes_type):
        return self.connection.get_request(
            self.get_attribute_url(attributes_type)
        )

    def upload_node_attribute(self, attributes_type, attributes):
        url = self.get_attribute_url(attributes_type)
        return self.connection.put_request(
            url,
            attributes
        )

    def write_attribute(self, attribute_type, attributes,
                        directory, serializer=None):
        attributes_directory = self.get_attributes_path(directory)
        if not os.path.exists(attributes_directory):
            os.mkdir(attributes_directory)
        attribute_path = os.path.join(
            attributes_directory,
            attribute_type
        )
        if os.path.exists(attribute_path):
            os.remove(attribute_path)
        return (serializer or self.serializer).write_to_path(
            attribute_path,
            attributes
        )

    def read_attribute(self, attributes_type, directory, serializer=None):
        attributes_directory = self.get_attributes_path(directory)
        if not os.path.exists(attributes_directory):
            raise InvalidDirectoryException(
                "Folder {0} doesn't contain node folder '{1}'"
                .format(directory, "node_{0}".format(self.id))
            )
        return (serializer or self.serializer).read_from_file(
            os.path.join(
                attributes_directory,
                attributes_type
            )
        )

    def deploy(self):
        self.env.install_selected_nodes("deploy", (self,))

    def provision(self):
        self.env.install_selected_nodes("provision", (self,))

    def delete(self):
        self.connection.delete_request(self.instance_api_path.format(self.id))

    def node_vms_create(self, config):
        url = "nodes/{0}/vms_conf/".format(self.id)
        return self.connection.put_request(url, {'vms_conf': config})

    def get_node_vms_conf(self):
        url = "nodes/{0}/vms_conf/".format(self.id)
        return self.connection.get_request(url)

    def set(self, data):
        return self.connection.put_request(
            self.instance_api_path.format(self.id),
            data
        )


class NodeCollection(object):

    class_api_path = "nodes/"

    def __init__(self, nodes):
        self.collection = nodes

    @classmethod
    def init_with_ids(cls, ids):
        return cls(map(Node, ids))

    @classmethod
    def init_with_data(cls, data):
        return cls(map(Node.init_with_data, data))

    def __str__(self):
        return "nodes [{0}]".format(
            ", ".join(map(lambda n: str(n.id), self.collection))
        )

    def __iter__(self):
        return iter(self.collection)

    @property
    def data(self):
        return map(attrgetter("data"), self.collection)

    @classmethod
    def get_all(cls):
        return cls(Node.get_all())

    @classmethod
    def update(cls, data):
        return BaseObject.connection.put_request(cls.class_api_path, data)

    @classmethod
    def delete_by_ids(cls, ids):
        url = '{0}?ids={1}'.format(
            cls.class_api_path,
            ','.join(map(str, ids))
        )

        return BaseObject.connection.delete_request(url)

    def filter_by_env_id(self, env_id):
        predicate = lambda node: node.data['cluster'] == env_id
        self.collection = filter(predicate, self.collection)
