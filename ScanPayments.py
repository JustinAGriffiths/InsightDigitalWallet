#!/bin/env python

max_events=5000000

class user() :
    def __init__(self, i) :
        self.ID=i
        self.friends=set()
        self.status=0
        self.network=set()
        pass

    def __hash__(self):
        return hash(self.ID)

    def __eq__(self, other):
        return self.ID==other.ID

    def __ne__(self, other):
        return self.ID!=other.ID

    def status(self):
        print self.status


    def add_friend(self, u):        
        self.friends.add(u)
        u.friends.add(self)
        pass
    
    def build_network(self, flist):
        for f in self.friends :
            for ff in f.friends :
                if ff in flist :
                    self.network.clear()
                    return True
                self.network.add(ff)
                continue
            continue
        return False

    


users={}
def get_user(ID, create_new=False):
    if ID in users: return users[ID]
    if create_new :
        u=user(ID)
        users[ID]=u
        return u

# for i in xrange(0,10):
#     u=user(i)
#     v=user(i+10)
#     w=user(i+100)
#     users.add(u)
#     users.add(v)
#     users.add(w)
#     u.add_friend(v)
#     u.add_friend(w)


# print len(users)

# for u in users: print len(u.friends)

# import sys
# sys.exit(0)

f=open('batch_payment.csv','r')

counter=0
for line in f:
    if(counter==0) : 
        counter=counter+1
        continue
    if(counter%100000==0): print counter
    if(counter>=max_events): break
    counter=counter+1
    fields=line.split(',')

    id_from=int(fields[1])
    id_to=int(fields[2])
    user_from=get_user(id_from, True)
    user_to=get_user(id_to, True)
    user_from.add_friend(user_to)

    continue


print len(users)


f=open('stream_payment.csv', 'r')

counter=0
depth={}
def add_depth(msg):
    if msg in depth: depth[msg]+=1
    else : depth[msg]=1
    pass

for line in f:
    if(counter==0) : 
        counter=counter+1
        continue
    if(counter%100000==0): print counter
    if(counter>=max_events): break
    counter=counter+1
    fields=line.split(',')

    decision=False

    id_from=int(fields[1])
    id_to=int(fields[2])

    if( (id_from not in users) or (id_to not in users) ):
        #print id_from, id_to, len(users)
        add_depth('new user')
        decision=True
        continue

    user_from=users[id_from]
    user_to=users[id_to]

    if(user_to in user_from.friends):
        add_depth('payee friend')
        decision=True
        continue

    for friend in user_from.friends :
        if user_to in friend.friends :
            add_depth('payee friend 2')
            decision=True
            break
        pass
 
    if decision : continue

    if(user_from.build_network(user_to.friends)):
        decision=True
        add_depth('payee friend 3')
        user_from.network.clear()
        pass

    if decision : 
        continue
   
    if(user_to.build_network(user_from.network)):
        decision=True
        add_depth('payee friend 4')        
        pass

    user_from.network.clear()
    user_to.network.clear()

    if decision==False : add_depth('WARNING')

    pass



print ''
for key,value in sorted(depth.iteritems()):
    print key.ljust(20, ' '), ' : ', value





    

