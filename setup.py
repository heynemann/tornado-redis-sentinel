#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from tornado_redis_sentinel import __version__

tests_require = [
    'mock',
    'nose',
    'coverage',
    'yanc',
    'preggy',
    'tox',
    'ipdb',
    'coveralls',
]

setup(
    name='tornado-redis-sentinel',
    version=__version__,
    description='Tornado redis library based in toredis that supports sentinel connections.',
    long_description='''
Tornado redis library based in toredis that supports sentinel connections.
''',
    keywords='tornado redis sentinel',
    author='Globo.com',
    author_email='timehome@corp.globo.com',
    url='',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
    ],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'toredis',
        'six'
    ],
    extras_require={
        'tests': tests_require,
    }
)
