#  Copyright 2014 Rackspace, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
import json
import operator
import tarfile
import gzip
import argparse
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

from zpmlib import zpm, miniswift

import jinja2

# List of function that will be the top-level zpm commands.
_commands = []


def set_up_arg_parser():
    parser = argparse.ArgumentParser(
        description='ZeroVM Package Manager',
        epilog=("See 'zpm <command> --help' for more information on a specific"
                " command."),
    )
    subparsers = parser.add_subparsers(description='available subcommands',
                                       metavar='COMMAND')

    for cmd in all_commands():
        subparser = subparsers.add_parser(cmd.__name__, help=cmd.__doc__)
        # Add arguments in reverse order: the last decorator
        # (bottom-most in the source) is called first, so its
        # arguments will be at the front of the list.
        for args, kwargs in reversed(getattr(cmd, '_args', [])):
            subparser.add_argument(*args, **kwargs)
        subparser.set_defaults(func=cmd)

    return parser


def command(func):
    """Register `func` as a top-level zpm command.

    The name of the function will be the name of the command and any
    cmdline arguments registered with `arg` will be available.
    """
    _commands.append(func)
    return func


def arg(*args, **kwargs):
    """Decorator for adding command line argument.

    The `args` and `kwargs` will eventually be passed to
    `ArgumentParser.add_argument`.
    """
    def decorator(func):
        if not hasattr(func, '_args'):
            func._args = []
        func._args.append((args, kwargs))
        return func
    return decorator


def all_commands():
    return sorted(_commands, key=operator.attrgetter('__name__'))


@command
@arg('dir', help='Non-existent or empty directory',
     metavar='WORKING_DIR', nargs='?',
     default=os.getcwd())
def new(args):
    """
    Create a default ZeroVM application ``zar.json`` specification in the
    target directory. If no directory is specified, ``zar.json`` will be
    created in the current directory.
    """

    try:
        zarjson = zpm.create_project(args.dir)
    except RuntimeError as err:
        print(err.message)
    else:
        print("Created '%s'" % zarjson)


@command
def bundle(args):
    """Bundle a ZeroVM application

    This command creates a ZAR using the instructions in ``zar.json``.
    The file is read from the project root.
    """
    root = zpm.find_project_root()
    zpm.bundle_project(root)


@command
@arg('zar', help='A ZeroVM artifact')
@arg('target', help='Swift path (directory) to deploy into')
@arg('--execute', action='store_true', help='Immediatedly '
     'execute the deployed Zar (for testing)')
@arg('--os-auth-url', default=os.environ.get('OS_AUTH_URL'),
     help='OpenStack auth URL. Defaults to $OS_AUTH_URL.')
@arg('--os-tenant-name', default=os.environ.get('OS_TENANT_NAME'),
     help='OpenStack tenant. Defaults to $OS_TENANT_NAME.')
@arg('--os-username', default=os.environ.get('OS_USERNAME'),
     help='OpenStack username. Defaults to $OS_USERNAME.')
@arg('--os-password', default=os.environ.get('OS_PASSWORD'),
     help='OpenStack password. Defaults to $OS_PASSWORD.')
def deploy(args):
    """Deploy a ZeroVM application

    This deploys a zar onto Swift. The zar can be one you have
    downloaded or produced yourself :ref:`zpm-bundle`.

    You will need to know the Swift authentication URL, username,
    password, and tenant name. These can be supplied with command line
    flags (see below) or you can set the corresponding environment
    variables. The environment variables are the same as the ones used
    by the `Swift command line tool <http://docs.openstack.org/
    user-guide/content/swift_commands.html>`_, so if you're already
    using that to upload files to Swift, you will be ready to go.
    """
    print('deploying %s' % args.zar)

    tar = tarfile.open(args.zar)
    zar = json.load(tar.extractfile('zar.json'))

    client = miniswift.ZwiftClient(args.os_auth_url,
                                   args.os_tenant_name,
                                   args.os_username,
                                   args.os_password)
    client.auth()

    path = '%s/%s' % (args.target, os.path.basename(args.zar))
    client.upload(path, gzip.open(args.zar).read())

    swift_path = urlparse.urlparse(client._swift_url).path
    if swift_path.startswith('/v1/'):
        swift_path = swift_path[4:]

    swift_url = 'swift://%s/%s' % (swift_path, path)
    job = json.load(tar.extractfile('%s.json' % zar['meta']['name']))
    device = {'device': 'image', 'path': swift_url}
    for group in job:
        group['file_list'].append(device)
    job_json = json.dumps(job)
    client.upload('%s/%s.json' % (args.target, zar['meta']['name']), job_json)

    # TODO(mg): inserting the username and password in the uploaded
    # file makes testing easy, but should not be done in production.
    # See issue #44.
    deploy = {'auth_url': args.os_auth_url,
              'tenant': args.os_tenant_name,
              'username': args.os_username,
              'password': args.os_password}
    for path in zar.get('ui', ['index.html', 'style.css', 'zebra.js']):
        # Upload UI files after expanding deployment parameters
        tmpl = jinja2.Template(tar.extractfile(path).read())
        output = tmpl.render(deploy=deploy)
        client.upload('%s/%s' % (args.target, path), output)

    if args.execute:
        print('job template:')
        from pprint import pprint
        pprint(job)
        print('executing')
        client.post_job(job)

    print('app deployed to\n  %s/%s/' % (client._swift_url, args.target))
