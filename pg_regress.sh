#!/bin/bash

rm -f /tmp/regression.diffs

TEST_DIRECTORY=$1

TEST_SUITE=""
for file in $TEST_DIRECTORY/sql/*.sql
do
  NAME=`basename $file .sql`
  TEST_SUITE="$TEST_SUITE $NAME"
done

echo "$TEST_SUITE"
su postgres <<EOF
  export PATH=$PATH:/usr/lib/postgresql/10/lib/pgxs/src/test/regress/
  cd $TEST_DIRECTORY
  echo "pg_regress $TEST_SUITE"
  pg_regress --outputdir=/tmp $TEST_SUITE
EOF

if [ -f '/tmp/regression.diffs' ]; then
  exit 1
fi
