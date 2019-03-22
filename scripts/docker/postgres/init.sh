#!/bin/bash

# Install Multicorn
echo "~~~~~~~~~~~~~ Installing multicorn"
rm -rf /tmp/Multicorn
cd /tmp
git clone git://github.com/Kozea/Multicorn.git
cd Multicorn
git checkout tags/v1.3.4
make && make install

# Install neo4j fdw
echo "~~~~~~~~~~~~~ Installing Neo4j FDW"
if [ -d "/source" ]; then
  cd /source/
else
  cd /neo4j-fdw/source/
fi
make install
