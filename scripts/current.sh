#!/bin/bash

rm /source/test/sql/000_create_extensions_wrappers_legacy.sql
rm /source/test/expected/000_create_extensions_wrappers_legacy.out
cp /source/test/sql/000_create_extensions_wrappers.current /source/test/sql/000_create_extensions_wrappers_current.sql
cp /source/test/expected/000_create_extensions_wrappers.current /source/test/expected/000_create_extensions_wrappers_current.out
