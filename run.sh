#!/bin/bash

if [ `head -c4 paymo_input/batch_payment.txt` == "time" ]; then
    echo "doing simple test"
    echo "usage is"
    python src/antifraud.py -h
    python src/antifraud.py -i paymo_input/batch_payment.txt -s paymo_input/stream_payment.txt
    exit
fi

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
