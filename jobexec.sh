#!/usr/bin/env bash

OUTPUTFILE="result.nc"

date > $OUTPUTFILE
sleep 3
date >> $OUTPUTFILE
sleep 3
echo ":END:" >> $OUTPUTFILE

