#!/bin/bash

# Install Multicorn
echo "~~~~~~~~~~~~~ Installing multicorn"
cd /neo4j-fdw/
git clone git://github.com/Kozea/Multicorn.git
cd Multicorn
make && make install

# Install neo4j fdw
echo "~~~~~~~~~~~~~ Installing Neo4j FDW"
cd /neo4j-fdw/source/
python setup.py install
