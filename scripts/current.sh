#!/bin/bash

CSQL='/source/test/sql/000_create_extensions_wrappers_legacy.sql'; [[ -f $CSQL ]] && rm $CSQL
COUT='/source/test/expected/000_create_extensions_wrappers_legacy.out'; [[ -f $COUT ]] && rm $COUT
cp /source/test/sql/000_create_extensions_wrappers.current /source/test/sql/000_create_extensions_wrappers_current.sql
cp /source/test/expected/000_create_extensions_wrappers.current /source/test/expected/000_create_extensions_wrappers_current.out
