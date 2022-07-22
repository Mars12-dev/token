#if !SWAP_INTERFACE 
#define SWAP_INTERFACE 

type buy_param = 
[@layout:comb] 
{ 
  address_to : address;
  amount: nat;
} 

type storage = 
[@layout:comb] 
{ 
  token_in_address : address; 
  token_out_address : address; 
  token_price : nat; 
} 

type parameter = 
| Buy of buy_param
type return = operation list * storage 

#endif 