# InsightDigitalWallet

## Synopsis

This is a solution to networking payers with payees to verify whether a transaction is b/w two
users who are in the same network defined as being connected in the fourth generation or less.  Where
0th generation would be self, 1st would be friends, 2nd share a mutual friend, 3rd have mutual friends 
that are friends, 4th etc.

Payer(A) -- B -- C -- D -- E

where A is friends with B, B with C, C with D, ...

### Strategy

The strategy is to :
  1) check if payee is registered, e.g. has made a transaction
  2) check if payee and payer are friends (1st gen)
  3) check if payee is friends with one of the payer's friends (2nd gen)
  4) check if a friend of the payee is in the 2nd generation network of the payor (friend of friends) (3rd gen)
  5) check if the payee's 2nd generation network has an intersection with the payor's 2nd generation network

Data structure is simple c or python struct:

```
struct user {
       int id;
       unordered_set<user*> friends;
       unordered_set<user*> network; //2nd gen created and destroyed as needed
};
```

2nd generation networks are built per transaction on a need basis (that is strategy through 3 fails above) and are
destroyed subsequently.  As second generation networs are built, checks are made to see if a match can be made, if so
the network construction is abandoned since a match was made.  Keeping the 2nd gen networks around is too memory intensive--
estimate O(100M) users would be in the sum of all networks when there are O(80k) users.

Output is not as described here:

https://github.com/InsightDataScience/digital-wallet/blob/master/README.md

since this was just for fun :)

## Usage

download the data files doing:

```
wget https://github.com/InsightDataScience/digital-wallet/blob/master/paymo_input/batch_payment.txt 
wget https://github.com/InsightDataScience/digital-wallet/blob/master/paymo_input/stream_payment.txt

to test do:

./run.sh [implementation] #implemntation is either scan_payments.cxx or ScanPayments.py, default is the cxx
```
