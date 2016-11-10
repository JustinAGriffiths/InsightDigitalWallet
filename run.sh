#!/bin/bash

if [ ! -f paymo_input/batch_payment.csv ]; then
    wget https://github.com/InsightDataScience/digital-wallet/blob/master/paymo_input/batch_payment.txt paymo_input/
fi

if [ ! -f paymo_input/stream_payment.csv ]; then
    wget https://github.com/InsightDataScience/digital-wallet/blob/master/paymo_input/stream_payment.txt paymo_input/
fi


echo 'Running src/antifraud.py'
python src/antifraud.py -h
time python src/antifraud.py $@