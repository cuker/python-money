#!/usr/bin/env python

from setuptools import setup, find_packages

VERSION = '0.0.1'
LONG_DESC = """\
python-money provides carefully designed basic Python primitives for working with money and currencies.

The primary objectives of this module is to aid in the development of financial applications by increasing testability and reusability, reducing code duplication and reducing the risk of defects occurring in the code.

The module defines two basic Python classes -- a Currency class and a Money class. It also pre-defines all the world's currencies, according to the ISO 4217 standard. The classes define some basic operations for working with money, overriding Python's addition, substraction, multiplication, etc. in order to account for working with money in different currencies. They also define currency-aware comparison operators. To avoid floating point precision errors in monetary calculations, the module uses Python's Decimal type exclusively.

The design of the module is based on the Money enterprise design pattern, as described in Martin Fowler's "Patterns of Enterprise Application Architecture".

This project also contains Django helper classes for easy integration with python-money.
"""

setup(name='python-money',
      version=VERSION,
      description="A simple library for managing monetary data",
      long_description=LONG_DESC,
      classifiers=[
          'Programming Language :: Python',
          'Operating System :: OS Independent',
          'Natural Language :: English',
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
      ],
      keywords='currency money business accounting cash django enterprise e-commerce',
      #author='s3x3y1',
      #author_email='s3x3y1',
      maintainer = 'Jason Kraus',
      maintainer_email = 'zbyte64@gmail.com',
      url='http://wiki.github.com/jkp/soaplib-lxml',
      license='New BSD License',
      packages=find_packages(exclude=['ez_setup', 'money', 'tests']),
      zip_safe=False,
      install_requires=[
      ],
      #test_suite='tests.test_suite',
      )
