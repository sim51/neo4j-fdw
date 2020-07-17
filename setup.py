from setuptools import setup, find_packages
import neo4jPg

setup(
      name             = neo4jPg.__package__,
      version          = "__VERSION__",
      author           = neo4jPg.__author__,
      author_email     = neo4jPg.__email__,
      url              = neo4jPg.__url__,
      packages         = find_packages(),
      install_requires = [ 'neo4j-driver==1.7.6','neobolt==1.7.16', 'python-dateutil' ]
)
