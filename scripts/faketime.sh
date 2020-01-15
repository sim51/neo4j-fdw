#!/bin/sh
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/faketime/libfaketime.so.1
export FAKETIME_DONT_RESET=1
export FAKETIME="@2019-07-14 17:30:00"

