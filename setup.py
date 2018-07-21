# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2018 by Lars Klitzke, Lars.Klitzke@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import setuptools

# read in the long description written in the README.md file
with open("README.md", "r") as fh:
    long_description = fh.read()

__version__ = '1.2.1'

setuptools.setup(
    name='binance2delta',
    version=__version__,
    description='Package with tools to query Binance and to generate csv files for import transactions into delta.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Lars Klitzke',
    author_email='Lars.Klitzke@gmail.com',
    classifiers=(
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
        "Natural Language :: English",
    ),
    entry_points={
        'console_scripts': [
            'binance2delta = binance2delta.convert:main',
            'binancecrawler = binance2delta.crawler:main'
        ]
    },
    packages=setuptools.find_packages(),
    install_requires=[
        'requests',
        'xlrd'
    ],

)
