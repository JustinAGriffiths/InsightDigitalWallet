#!/bin/bash

if [ ! -f batch_payment.csv ]; then
    wget https://github.com/InsightDataScience/digital-wallet/blob/master/paymo_input/batch_payment.txt
fi

if [ ! -f stream_payment.csv ]; then
    wget https://github.com/InsightDataScience/digital-wallet/blob/master/paymo_input/stream_payment.txt
fi

imp="scan_payments.cxx"
if [[ $1 ]]; then imp="ScanPayments.py"; fi

if [ "$imp" == "scan_payments.cxx" ]; then
    g++ scan_payments.cxx -std=c++11 -fpermissive -O2 -o scan_payments 
    time ./scan_payments
else
    time python $imp
fi