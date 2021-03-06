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

"""
ZeroVM Package Manager
"""

from setuptools import find_packages
from setuptools import setup

VERSION = '0.1'

setup(
    name='zpm',
    version=VERSION,
    maintainer='Rackspace ZeroVM Team',
    maintainer_email='zerovm@rackspace.com',
    url='https://github.com/zerovm/zpm',
    description='ZeroVM Package Manager',
    long_description=__doc__,
    platforms=['any'],
    packages=find_packages(exclude=['zpmlib.tests', 'zpmlib.tests.*']),
    provides=['zpm (%s)' % VERSION],
    install_requires=['requests', 'jinja2<2.7'],
    license='Apache 2.0',
    keywords='zpm zerovm zvm',
    classifiers=(
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Build Tools',
    ),
    scripts=['zpm'],
)
