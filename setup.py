# Copyright (c) 2021 Cloudify Platform Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
from setuptools import setup
from setuptools import find_packages


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def get_version(rel_file='plugin.yaml'):
    lines = read(rel_file)
    for line in lines.splitlines():
        if 'package_version' in line:
            split_line = line.split(':')
            line_no_space = split_line[-1].replace(' ', '')
            line_no_quotes = line_no_space.replace('\'', '')
            return line_no_quotes.strip('\n')
    raise RuntimeError('Unable to find version string.')


setup(
    name="cloudify-starlingx-plugin",
    version=get_version(),
    author="Cloudify.Co",
    author_email="cosmo-admin@cloudify.co",
    packages=find_packages(),
    license="LICENSE",
    description="Represent StarlingX Workloads in Cloudify.",
    install_requires=[
        'distributedcloud-client',
        'cgtsclient',
        'httplib2',
        'cloudify-common',
        'babel',  # Required by distributedcloud-client
        'PrettyTable<0.8,>=0.7.2',  # Required by distributedcloud-client
    ]
)
