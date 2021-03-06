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

from fuelclient.commands import base
from fuelclient.common import data_utils


class OpenstackConfigMixin(object):

    entity_name = 'openstack-config'

    @staticmethod
    def add_env_arg(parser):
        parser.add_argument(
            '-e', '--env',
            type=int, required=True,
            help='Environment ID.')

    @staticmethod
    def add_file_arg(parser):
        parser.add_argument(
            '-f', '--file', required=True,
            type=str, help='YAML file that contains openstack configuration.')

    @staticmethod
    def add_config_id_arg(parser):
        parser.add_argument(
            'config',
            type=int, help='Openstack configuration ID.'
        )

    @staticmethod
    def add_node_id_arg(parser):
        parser.add_argument(
            '-n', '--node',
            type=int, default=None, help='Node ID.'
        )

    @staticmethod
    def add_node_role_arg(parser):
        parser.add_argument(
            '-r', '--role',
            type=str, default=None, help='Node role.'
        )

    @staticmethod
    def add_deleted_arg(parser):
        parser.add_argument(
            '-D', '--deleted',
            type=bool, default=False, help='Show deleted configurations.'
        )

    @staticmethod
    def add_force_arg(parser):
        parser.add_argument(
            '-f', '--force',
            action='store_true', help='Force configuration update.'
        )


class OpenstackConfigList(OpenstackConfigMixin, base.BaseCommand):
    """List all openstack configurations.
    """

    columns = (
        'id', 'is_active', 'config_type',
        'cluster_id', 'node_id', 'node_role')

    def get_parser(self, prog_name):
        parser = super(OpenstackConfigList, self).get_parser(prog_name)

        self.add_env_arg(parser)
        self.add_node_id_arg(parser)
        self.add_node_role_arg(parser)
        self.add_deleted_arg(parser)

        return parser

    def take_action(self, args):
        data = self.client.get_filtered(
            cluster_id=args.env, node_id=args.node,
            node_role=args.role, is_active=(not args.deleted))
        data = data_utils.get_display_data_multi(self.columns, data)

        return self.columns, data


class OpenstackConfigDownload(OpenstackConfigMixin, base.BaseCommand):
    """Download specified configuration file.
    """

    def get_parser(self, prog_name):
        parser = super(OpenstackConfigDownload, self).get_parser(prog_name)

        self.add_config_id_arg(parser)
        self.add_file_arg(parser)

        return parser

    def take_action(self, args):
        file_path = self.client.download(args.config, args.file)

        msg = ("OpenStack configuration with id={0} "
               "downloaded to {1}\n").format(args.config, file_path)
        self.app.stdout.write(msg)


class OpenstackConfigUpload(OpenstackConfigMixin, base.BaseCommand):
    """Upload new opesntack configuration from file.
    """

    def get_parser(self, prog_name):
        parser = super(OpenstackConfigUpload, self).get_parser(prog_name)

        self.add_env_arg(parser)
        self.add_node_id_arg(parser)
        self.add_node_role_arg(parser)
        self.add_file_arg(parser)

        return parser

    def take_action(self, args):
        config = self.client.upload(
            path=args.file, cluster_id=args.env,
            node_id=args.node, node_role=args.role)

        msg = "OpenStack configuration with id {0} " \
              "uploaded from file '{0}'\n".format(config.id, args.file)
        self.app.stdout.write(msg)


class OpenstackConfigExecute(OpenstackConfigMixin, base.BaseCommand):
    """Execute openstack configuration deployment.
    """

    def get_parser(self, prog_name):
        parser = super(OpenstackConfigExecute, self).get_parser(prog_name)

        self.add_env_arg(parser)
        self.add_node_id_arg(parser)
        self.add_node_role_arg(parser)
        self.add_force_arg(parser)

        return parser

    def take_action(self, args):
        self.client.execute(
            cluster_id=args.env, node_id=args.node, node_role=args.role,
            force=args.force)

        msg = "OpenStack configuration execution started.\n"
        self.app.stdout.write(msg)
