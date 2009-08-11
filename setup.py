from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='menhir.simple.tag',
      version=version,
      description="",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['menhir', 'menhir.simple'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'setuptools',
          'lovely.tag',
          'dolmen.content',
          'dolmen.app.site',
          # -*- Extra requirements: -*-

      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
