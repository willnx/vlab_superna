#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
superna RESTful API
"""
from setuptools import setup, find_packages


setup(name="vlab-superna-api",
      author="Nicholas Willhite,",
      author_email='willnx84@gmail.com',
      version='0.0.1',
      packages=find_packages(),
      include_package_data=True,
      package_files={'vlab_superna_api' : ['app.ini']},
      description="superna",
      install_requires=['flask', 'ldap3', 'pyjwt', 'uwsgi', 'vlab-api-common',
                        'ujson', 'cryptography', 'vlab-inf-common', 'celery']
      )
