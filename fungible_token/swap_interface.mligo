#if !SWAP_INTERFACE 
#define SWAP_INTERFACE 

type buy_param = 
[@layout:comb] 
{ 
  address_to : address;
  amount: nat;
} 

type fa12_contract_transfer =
[@layout:comb]
  { [@annot:from] address_from : address;
    [@annot:to] address_to : address;
    value : nat }

type storage = 
[@layout:comb] 
{ 
  token_in_address : address; 
  token_out_address : address; 
  treasury : address; 
  token_price : nat; 
  admin : address;
  paused : bool;
} 

type parameter = 
| SetPause of bool
| SetTokenIn of address
| SetTokenOut of address
| SetTreasury of address
| Buy of buy_param

type return = operation list * storage 

#endif 