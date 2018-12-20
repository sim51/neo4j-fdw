#!/bin/bash

# Install Multicorn
echo "~~~~~~~~~~~~~ Installing multicorn"
rm -rf /tmp/Multcorn
cd /tmp
git clone git://github.com/Kozea/Multicorn.git
cd Multicorn
make && make install

# Install neo4j fdw
echo "~~~~~~~~~~~~~ Installing Neo4j FDW"
cd /source/
python setup.py install
