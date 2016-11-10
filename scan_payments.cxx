#include <map>
#include <set>
#include <vector>
#include <iostream>
#include <cstdio>
#include <unordered_set>
#include <TSystem.h>
#include <TStopwatch.h>

using namespace std;

struct transaction {
  std::string time;
  int from;
  int to;
  float price;
  transaction( std::string t, int f, int to_, float p):
    time(t),
    from(f),
    to(to_),
    price(p){}
};


class user;
template<>
struct hash<user*> {
  size_t operator()(const user* k);
};
typedef unordered_set<user*, hash<user*> > user_list;
//typedef set<user*> user_list;


struct user {
  vector<transaction*> transactions;
  
  user_list friends;
  user_list network;
  int id;
  user(int i):
    id(i){}

  bool build_network(){
    static user_list a;
    return build_network(a);
  }
  bool build_network(user_list& friends){
    network.clear();
    for(user* u : this->friends){
      for(user* v : u->friends){
	if(friends.find(v)!=friends.end()) {
	  network.clear();
	  return true;
	}
	network.insert(v);
      }
    }    
    return false;
  }

  void add_friend(user* u, bool update_network=false){
    friends.insert(u);
    u->friends.insert(this);    
    if(update_network){
      for(user* v : u->friends) {
	network.insert(v);   
	v->network.insert(this);
      }
    }
  }

  bool compare_networks(user* u){
    if(this->network.size()==0) this->build_network();
    if(u->network.size()==0) u->build_network();
    for(user* v : this->network){
      if(u->network.find(v)!=this->network.end()) return true;
    }
    return false;
  }

};

size_t hash<user*>::operator()(const user* k){
  return k->id;
}


//typedef map<int, user*> user_map;//could be vector
typedef vector<user*> user_map;// go back to vector in case ids are more random

user* get_user( int id, user_map& users, bool make_new=false){
  // user_map::iterator itr = users.find(id);
  // if(itr!=users.end()) return itr->second;

  if(id<users.size()&&users[id]!=0) return users[id];

  if(make_new) {
    user* u = new user(id);
    if(users.size()<id)
    while(users.size()<id) users.push_back(0);
    users[id]=u;
    //cout << users.size() << " " << id << endl;
    return u;
  }

  return 0;
}


bool readLine(FILE* in, const char* expr, char time[], int& from, int& to, float& price){

  static const int buffsize=65536;
  static char buff[buffsize];

    fscanf(in, "%20[^,], %i, %i, %f", time,  &from, &to, &price);
    if(std::string(time).substr(0,4)!="2016") {
      cout << "Error " << time << endl;
      return false;
    }

    fgets(buff, buffsize, in);
    return true;
}

int main(int argc, char** argv){

  //profile
  TStopwatch watch;

  std::string batch_file="batch_payment.csv";
  std::string stream_file="stream_payment.csv";
  bool update_friends=false;
  //a new user's first payment is rejected, but is added as friend
  //in the real world, this would only happen if payer verified new user
  bool add_new_users=false;
  
  for(int i=1; i != argc; ++i){
    std::string arg = argv[i];
    if(arg.length()>10 && arg.substr(0,10)=="--in-file="){
      batch_file=arg;
      batch_file.replace(0,10,"");
    }
    if(arg.length()>16 && arg.substr(0,14)=="--stream-file="){
      stream_file=arg;
      stream_file.replace(0,14,"");
    }
    if(arg=="--update-friends"){
      update_friends=true;
    }
    if(arg=="--add-users"){
      add_new_users=true;
    }        
  }
  

  FILE* in=fopen(batch_file.c_str(), "r");
  FILE* stream=fopen(stream_file.c_str(), "r");

  //skip headers
  fscanf(in, "%*[^\n]\n", NULL);
  fscanf(stream, "%*[^\n]\n", NULL);


  user_map users;
  vector<transaction*> transactions;
  
  int counter=0;
  int f, t;
  float p;
  char time[256];

  while(!feof(in)){
    counter++;
    if(counter%100000==0) {
      cout << counter << endl;
    }
    if(!readLine(in, "%20[^,], %i, %i, %f", time,  f, t, p)) return 0;

    transaction* trans = new transaction(time, f, t, p);
    transactions.push_back(trans);

    user* user_from = get_user(f, users, true);
    user* user_to = get_user(t, users, true);

    user_from->transactions.push_back(trans);
    user_to->transactions.push_back(trans);
    user_from->add_friend(user_to);//recipricates friendship
  }
  cout << "end: " << transactions.size() << " " << users.size() << " " << /*known_transactions.size() << */endl;

  int valid_transations = 0;
  int fraudulent_transactions = 0;
  const int nDepth=6;
  int transaction_depth[nDepth] = {0}; // new-user, known-transaction, friend-of-friend, ...
  double transaction_times[nDepth] = {0.};
  double transaction_max_time[nDepth] = {0.};

  counter=0;
  while(!feof(stream) /*&&counter<10000*/) {
    counter++;
    if(counter%100000==0) cout << counter << endl;
    if(!readLine(stream, "%20[^,], %i, %i, %f", time,  f, t, p)) return 0;

    user* user_from = get_user(f, users);
    user* user_to = get_user(t, users);

    watch.Start();
    int depth=0;
    if(!user_to) {
      depth=5;
    }
    else if(!user_from){
      depth=5;
    }    
    else if( user_from->friends.find(user_to) != user_from->friends.end() ){
      depth=1;
    }
    else {
      //build friend of friends
      for(user* u : user_from->friends){
	if( u->friends.find(user_to) != u->friends.end() ) {
	  depth=2;
	  break;
	}
      }
      if(depth==0){
	if(user_from->build_network(user_to->friends)) depth=3;
	if(depth==0){
	  //final fucking test
	  if(user_to->build_network(user_from->network)) depth=4;
	}
	user_from->network.clear();
	user_to->network.clear();
      }      
    }
    watch.Stop();
    
    double time=watch.RealTime();
    transaction_times[depth]+=time;
    if(time>transaction_max_time[depth]) transaction_max_time[depth]=time;

    transaction_depth[depth]++;
    if(depth==0||depth==5) fraudulent_transactions++;
    else {
      valid_transations++;
      if(update_friends) user_from->add_friend(user_to);//do we want to do this?
    }
    if(depth==5&&add_new_users) {
      if(user_to==0){
	user_to = get_user(t, users, true);
	//cout << user_to << " " << user_from << " " << f << endl;
      }
      if(user_from==0){
	user_from = get_user(f, users, true);
	//cout << user_to << " " << user_from << " " << t << endl;
      }
      if(update_friends) user_to->add_friend(user_from);
    }

  }
  cout << "valid, warning, all unique: " << valid_transations << ", " << fraudulent_transactions << /*", " << known_transactions.size() << */endl;
  //  cout << "Transaction Depth: " << transaction_depth[0] << " " << transaction_depth[1] << " " << transaction_depth[2] << " " << transaction_depth[3] << endl;
  for(int i = 0; i != nDepth; ++i){
    cout << "Transaction_Depth: " << i << " " << transaction_depth[i] << " ave time: " << transaction_times[i]/transaction_depth[i] << " max time: " << transaction_max_time[i] << endl;
  }

}
