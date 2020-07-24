#!/bin/bash

CSQL='/source/test/sql/000_create_extensions_wrappers_current.sql'; [[ -f $CSQL ]] && rm $CSQL
COUT='/source/test/expected/000_create_extensions_wrappers_current.sql'; [[ -f $COUT ]] && rm $COUT
cp /source/test/sql/000_create_extensions_wrappers.legacy /source/test/sql/000_create_extensions_wrappers_legacy.sql
cp /source/test/expected/000_create_extensions_wrappers.legacy /source/test/expected/000_create_extensions_wrappers_legacy.out
