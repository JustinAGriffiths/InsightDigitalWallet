#!/bin/env python

#________________________________________
def usage():
    """
    
    """

#________________________________________
class transaction() :
    def __init__(self, p1, p2, a):
        self.payer=p1
        self.payee=p2
        self.amount=a
        

#________________________________________
class user() :
    def __init__(self, i) :
        self.ID=i
        self.friends=set()
        self.status=0
        self.network=set()
        self.transactions={}
        self.pending={}
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
        self.update_pending()
        u.friends.add(self)
        u.update_pending()
        pass
    
    def build_network(self, flist=set()):
        for f in self.friends :
            if len(f.friends & flist) > 0 :
                self.network.clear()
                return True
            self.network.update(f.friends)
            continue
        return False

    def add_transaction(self, t, u):
        if u in self.transactions: self.transactions[u].append(t)
        else : self.transactions[u]=[t]
        pass

    def add_pending(self, t, u):
        if u in self.pending: self.pending[u].append(t)
        else : self.pending[u]=[t]
        pass
    
    def update_pending(self):
        pop=[]
        for u,l in self.pending.iteritems():
            if u in self.friends:
                for t in l : 
                    self.add_transaction(t, u)
                    pop.append(u)
                    continue
                pass
            continue
        for u in pop: self.pending.pop(u)



#________________________________________
users={}
def get_user(ID, create_new=False):
    if ID in users: return users[ID]
    if create_new :
        u=user(ID)
        users[ID]=u
        return u
    return None

depth={}
transaction_list=[]
fraudulent_users={}

#________________________________________
def add_depth(msg, val, del_time, fraudster=-1):
    if msg in depth: 
        l=depth[msg]
        l[0]=l[0]+1
        l[1]+=del_time
        if(del_time>l[2]) : l[2]=del_time
    else : depth[msg]=[1, del_time, del_time]
    transaction_list.append([val, len(transaction_list)]);
    if fraudster>=0:
        if fraudster in fraudulent_users: fraudulent_users[fraudster]=fraudulent_users[fraudster]+1
        else : fraudulent_users[fraudster]=1
    pass



#________________________________________
def do_diagnostics():
    fdiagnostic=open('paymo_output/diagnostics.txt', 'w')
    for key,value in sorted(depth.iteritems()):
        print key.ljust(20, ' '), ' : ', value[0]
        fdiagnostic.write('%s: %i; avetime=%f; maxtime=%f \n' %(key.ljust(20, ' '), value[0], value[1]/value[0]*1., value[2]))
        continue

    max_friends=None
    max_network=None
    total_friends=0
    total_network=0
    for ID,user in users.iteritems() :
        if not max_friends or len(user.friends) > len(max_friends.friends) : max_friends = user
        user.build_network()
        if not max_network or len(user.network) > len(max_network.network) :
            total_network=total_network+len(user.network)
            if max_network  :
                max_network.network.clear()
                pass
            max_network=user
            pass
        else : 
            total_network=total_network+len(user.network)
            user.network.clear()
            pass
        total_friends+=len(user.friends)
        
            
    fdiagnostic.write('\nMost Friends uid=%i, nFriends=%i\n' %(max_friends.ID, len(max_friends.friends)))
    fdiagnostic.write('Most Network uid=%i, nNetwork=%i\n' %(max_network.ID, len(max_network.network)))
    fdiagnostic.write('Total Friends: %i\nTotal Network: %i\nAverage Friends: %f\nAverage Network: %f\n' %(total_friends, total_network, total_friends/len(users)*1., total_network/len(users)*1.))

    fdiagnostic.close()


    ffraudUsers=open('paymo_output/fraud_user_count.txt', 'w')
    for fraudster,val in fraudulent_users.iteritems():
        ffraudUsers.write('%i %i\n' %(fraudster, val)) 
        continue
    ffraudUsers.close()

    pass


#________________________________________
def main(arg_list):

    import argparse

    parser = argparse.ArgumentParser(description="Verify Payments")

    parser.add_argument('-a', '--add-as-friend', const=True, default=False, nargs='?',
                        help='while looking at stream, add as friends if transaction is verified, can help reduce time for future searches',
                        dest='add_as_friend')
    parser.add_argument('-n', '--add-new-user', const=True, default=False, nargs='?',
                        help='a new user is unverified for the first encounter, but the payer friends them, so they are a part of the network for future transactions ',
                        dest='add_new_user')
    parser.add_argument('-q', '--quiet',  const=True, default=False, nargs='?',
                        help='do a simple analysis on the users', dest='quiet')
    parser.add_argument('-d', '--diagnostic',  const=True, default=False, nargs='?',
                        help='do timing diagnostics', dest='do_diagnostic')

    parser.add_argument('-i', '--in-file', default=['paymo_input/batch_payment.csv'], nargs='+',
                        help='input batch file[s]', dest='infiles')
    parser.add_argument('-s', '--stream-file', default=['paymo_input/stream_payment.csv'], nargs='+',
                        help='input stream file[s]', dest='streamfiles')
#     parser.add_argument('-t', '--track-transactions', const=True, default=False, nargs='?', dest='track_transactions',
#                         help='keep track of pending approved transactions for users, pending can be approved with subsequent runs -r/--repeat and -a/--add-as-friend and -n --add-new-user')
    parser.add_argument('-r', '--repeat-stream', default=1, nargs='?', type=int, dest='iterations',
                        help='run over stream file again, should include with -a/-n/-t')


    args = parser.parse_args()

    counter=0
    for fname in args.infiles :
        f=open(fname,'r')

        first_line=True
        for line in f:
            if(first_line) : 
                first_line=False
                continue
            if(counter%100000==0 and not args.quiet): print counter
            #if(counter>100000) : break
            counter=counter+1
            fields=line.split(',')
        
            id_from=int(fields[1])
            id_to=int(fields[2])
            user_from=get_user(id_from, True)
            user_to=get_user(id_to, True)
            user_from.add_friend(user_to)


#             if args.track_transactions :
#                 t=transaction(user_from, user_to, float(fields[3]))
#                 user_from.add_transaction(t, user_to)
#                 user_to.add_transaction(t, user_from)
            
            continue
        f.close()
        continue

    if not args.quiet : print 'Total users=', len(users)


    counter=0    
    import time
    for iteration in xrange(0, args.iterations):
        for fname in args.streamfiles:
            f=open(fname, 'r')
            
            first_line=True
            for line in f:
                if(first_line) : 
                    first_line=False
                    continue
                if(counter%100000==0 and not args.quiet): print counter
                #if(counter>100000) : break;
                counter=counter+1
                fields=line.split(',')

                decision=False

                id_from=int(fields[1])
                id_to=int(fields[2])
                
                start=time.time()

                if(id_from not in users) :
                    add_depth('new user', 5, time.time()-start, fraudster=id_from)
                    if args.add_new_user : 
                        user_from=get_user(id_from, True)
#                         if args.track_transactions :
#                             user_to=get_user(id_to, True)
#                             t=transaction( user_from, user_to, float(fields[3]))
#                             user_to.add_pending(t, user_from)
#                             user_from.add_pending(t, user_to)
#                             pass
                        pass
                    continue

                if (id_to not in users) :
                    add_depth('new user', 5, time.time()-start, fraudster=id_to)
                    if args.add_new_user : 
                        user_to=get_user(id_to, True)
#                         if args.track_transactions :
#                             user_from=get_user(id_from, True)
#                             t=transaction( user_from, user_to, float(fields[3]))
#                             user_to.add_pending(t, user_from)
#                             user_from.add_pending(t, user_to)
#                             pass
                        pass                        
                    continue

                user_from=users[id_from]
                user_to=users[id_to]

                if(user_to in user_from.friends):
                    add_depth('payee friend', 1, time.time()-start)
                    decision=True
                    continue

                if len(user_to.friends & user_from.friends)>0: 
                    add_depth('payee friend 2', 2, time.time()-start)
                    decision=True
                    continue

                if(user_from.build_network(user_to.friends)):
                    decision=True
                    add_depth('payee friend 3', 3, time.time()-start)
                    user_from.network.clear()
                    continue
   
                if(user_to.build_network(user_from.network)):
                    decision=True
                    add_depth('payee friend 4', 4, time.time()-start)        
                    pass

                user_from.network.clear()
                user_to.network.clear()

                if decision==False : add_depth('unverified', 0, time.time()-start)
        
                if decision==True and args.add_as_friend : user_from.add_friend(user_to)

#                 if args.track_transactions:
#                     t=transaction(user_from, user_to, float(fields[3]))
#                     if decision : 
#                         user_from.add_transaction(t, user_to)
#                         user_to.add_transaction(t, user_from)
#                     else :
#                         user_from.add_pending(t, user_to)
#                         user_to.add_pending(t, user_from)
#                     pass

                continue#loop over file
            f.close()
            continue#loop over files
        continue#loop over iterations

    

#     if(args.track_transactions):
#         for u in users :
#             before=len(u.pending)
#             u.update_pending()
#             after=len(u.pending)
#             print before, after

    if(args.do_diagnostic) : do_diagnostics()

        

    #fout=open('paymo_output/out_py.txt', 'w')
    fout1=open('paymo_output/output1.txt','w')
    fout2=open('paymo_output/output2.txt','w')
    fout3=open('paymo_output/output3.txt','w')
    for l in transaction_list: 
        #fout.write('%i %i\n' %(l[1],l[0]))
        if l[0]==1 : fout1.write('trusted\n')
        else : fout1.write('unverified\n')
        if l[0]==1 or l[0]==2 : fout2.write('trusted\n')
        else : fout2.write('unverified\n')
        if l[0]==1 or l[0]==2 or l[0]==3 or l[0]==4 : fout3.write('trusted\n')
        else : fout3.write('unverified\n')
        continue
    #fout.close()
    fout1.close()
    fout2.close()
    fout3.close()

#________________________________________
if __name__ == "__main__":
    import sys
    main(sys.argv[1:])
