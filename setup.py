from setuptools import setup, find_packages
import os

version = '0.1'
history = os.path.join("docs", "HISTORY.txt")
readme = os.path.join("src", "menhir", "simple", "tag", "README.txt")

setup(name='menhir.simple.tag',
      version=version,
      description="",
      long_description= "%s\n%s" % (open(readme).read(), open(history).read()),
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='',
      author_email='',
      url='',
      license='GPL',
      packages=find_packages('src', exclude=['ez_setup']),
      package_dir={'': 'src'},
      namespace_packages=['menhir', 'menhir.simple'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'dolmen.app.layout',
          'dolmen.app.security',
          'dolmen.app.site',
          'dolmen.content',
          'fanstatic',
          'lovely.tag >= 1.1dev',
          'setuptools',
          'zeam.form.viewlet',
          ],
      entry_points="""
      # -*- Entry points: -*-
      [fanstatic.libraries]
      tag_resources = menhir.simple.tag.browser:TagResources
      """,
      )
