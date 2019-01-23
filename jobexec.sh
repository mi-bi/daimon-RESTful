#!/usr/bin/env bash

OUTPUTFILE="result.txt"

date > $OUTPUTFILE
sleep 3
date >> $OUTPUTFILE
sleep 3
echo ":END:" >> $OUTPUTFILE

