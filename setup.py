#!/usr/bin/env python
#coding:utf-8
import os
from mass2mole.ImportDependence import *
from mass2mole.CustomClass import *
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README.md')).read()
except:
    README = 'https://github.com/cycleuser/MassToMole/blob/main/README.md'



setup(name='mass2mole',
      version= version,
      description='A tool to calculate from mass percetange to mole percentage.',
      longdescription=README,
      author='cycleuser',
      author_email='cycleuser@cycleuser.org',
      url='https://github.com/cycleuser/MassToMole',
      packages=['mass2mole'],
      package_data={
          'mass2mole': ['*.py','*.txt','*.png','*.qm','*.ttf','*.ini','*.md'],},
      include_package_data=True,
      install_requires=[
                        'pandas',
                        'chempy',
                        'PyQt5'
                         ],
     )