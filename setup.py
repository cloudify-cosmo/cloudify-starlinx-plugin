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
import re
import pathlib
from setuptools import setup
from setuptools import find_packages


def get_version():
    current_dir = pathlib.Path(__file__).parent.resolve()
    with open(os.path.join(current_dir, 'cloudify_starlingx/__version__.py'),
              'r') as outfile:
        var = outfile.read()
        return re.search(r'\d+.\d+.\d+', var).group()


setup(
    name="cloudify-starlingx-plugin",
    version=get_version(),
    author="Cloudify.Co",
    author_email="cosmo-admin@cloudify.co",
    packages=find_packages(),
    license="LICENSE",
    description="Represent StarlingX Workloads in Cloudify.",
    install_requires=[
        'PrettyTable<0.8,>=0.7.2',  # Required by distributedcloud-client
        'distributedcloud-client',
        'cloudify-common',
        'cgtsclient',
        'httplib2',
        'babel',  # Required by distributedcloud-client
    ]
)
