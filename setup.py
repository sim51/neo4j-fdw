from setuptools import setup, find_packages

import neo4jPg

setup(
      name             = neo4jPg.__package__,
      version          = neo4jPg.__version__,
      description      = "",
      author           = neo4jPg.__author__,
      author_email     = neo4jPg.__email__,
      url              = neo4jPg.__url__,
      packages         = find_packages(),
      install_requires =[
          'py2neo'
          ]
      )
