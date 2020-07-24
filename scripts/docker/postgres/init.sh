#!/bin/bash

pip install --upgrade pip

# Install Multicorn
echo "~~~~~~~~~~~~~ Installing multicorn"
cd ~
if [ ! -d "/Multicorn" ]; then
  git clone git://github.com/Kozea/Multicorn.git
fi
cd Multicorn
git checkout tags/v1.3.4
make PYTHON_OVERRIDE=python2.7 && make PYTHON_OVERRIDE=python2.7 install


# Install neo4j fdw
echo "~~~~~~~~~~~~~ Installing Neo4j FDW"
cd /neo4j-fdw/source/
make PYTHON=python2.7 install

