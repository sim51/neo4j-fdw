#!/bin/bash

rm /source/test/sql/000_create_extensions_wrappers_current.sql
rm /source/test/expected/000_create_extensions_wrappers_current.out
cp /source/test/sql/000_create_extensions_wrappers.legacy /source/test/sql/000_create_extensions_wrappers_legacy.sql
cp /source/test/expected/000_create_extensions_wrappers.legacy /source/test/expected/000_create_extensions_wrappers_legacy.out
