#!/usr/bin/env python

from distutils.core import setup
from version import __version__

setup(name='CCS Deploy Lambda',
      version=__version__,
      license='MIT',
      description='Utilities to be used to deploy AWS Lambda',
      author='Caio Caçador da Silva',
      author_email='caiocacador.s@gmail.com',
      url='https://github.com/caio-cacador/ccs_deploy_lambda',
      packages=['deploy_lambda'])
