#!/bin/bash

if [ ! -f paymo_input/batch_payment.csv ]; then
    `cat paymo_input/batch_payment.txt`
fi

if [ ! -f paymo_input/stream_payment.csv ]; then
    `cat paymo_input/stream_payment.txt`
fi


python src/antifraud.py -h

echo ""
echo 'Running src/antifraud.py'

time python src/antifraud.py $@