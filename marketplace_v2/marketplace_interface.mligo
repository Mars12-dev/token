#if !MARKETPLACE_INTERFACE 
#define MARKETPLACE_INTERFACE 

type offer_id =
[@layout:comb]
{
  buyer : address;
  token_id : token_id;
  token_origin : address;
}

type counter_offer_id =
[@layout:comb]
{
  buyer : address;
  seller : address;
  token_id : token_id;
  token_origin : address;
}

type token_key =
[@layout:comb]
{
  token_id : token_id;
  token_origin : address;
}

type counter_offer =
{
    start_time : timestamp;
    end_time : timestamp;
    token_symbol: token_symbol;
    ft_amount : nat;
    seller : address;
}

type offer_info = 
[@layout:comb] 
{ 
    value : nat; 
    start_time: timestamp; 
    end_time : timestamp; 
    token_symbol : token_symbol;
} 


type swap_info = 
[@layout:comb] 
{ 
  owner : address; 
  token_id : token_id;
  token_origin : address;
  is_dutch : bool;
  is_reserved : bool;
  starting_price : nat;
  token_price : nat; 
  start_time : timestamp; 
  duration : int;
  end_time : timestamp; 
  recipient : address;
  ft_symbol : token_symbol;
  accepted_tokens : token_symbol set;
  is_multi_token : bool;
} 

type storage = 
[@layout:comb] 
{ 
  collections : address set; 
  royalties_address : address;
  next_swap_id : swap_id; 
  tokens : (token_key , swap_id) big_map;
  counter_offers : (counter_offer_id, counter_offer) big_map; 
  swaps : (swap_id, swap_info) big_map; 
  offers : (offer_id , offer_info) big_map; 
  royalties_rate : nat;
  management_fee_rate : nat; 
  paused : bool; 
  allowed_tokens : (token_symbol, fun_token) big_map;
  available_pairs : ((token_symbol * token_symbol), string) big_map;
  single_tokens : string set;
  oracle : address;
  admin : address;
  // multisig : address;
  treasury : address;
  oracle_tolerance : int;
} 

type recipient_type = 
| General of unit
| Reserved of address

type dutch_swap_param =
[@layout:comb]
{
  starting_price : nat;
  duration : nat;
}

type swap_type =
| Regular of unit
| Dutch of dutch_swap_param

type add_to_marketplace_param = 
[@layout:comb] 
{ 
  swap_type : swap_type;
  token_id : token_id;
  token_origin : address;
  token_price : nat; 
  start_time : timestamp; 
  end_time : timestamp; 
  recipient : recipient_type;
  token_symbol : token_symbol;
  accepted_tokens : token_symbol set;
  is_multi_token : bool;
} 

type remove_from_marketplace_param = swap_id

type collect_marketplace_param = 
[@layout:comb]
{
  swap_id : swap_id;
  token_symbol : token_symbol;
  amount_ft : nat;
  to_ : address;
}

type offer_param = 
[@layout:comb] 
{ 
    token_id : token_id;
    token_origin : address;
    start_time: timestamp; 
    end_time : timestamp; 
    token_symbol : token_symbol;
    ft_amount : nat;
} 

type counter_offer_param =
[@layout:comb]
{
  token_id : token_id;
  token_origin : address;
  buyer : address;
  start_time : timestamp;
  end_time : timestamp;
  token_symbol: token_symbol;
  ft_amount : nat;
}

type accept_counter_offer_param =
[@layout:comb]
{
  token_id : token_id;
  token_origin : address;
  seller : address;
}

type withdraw_counter_offer_param =
[@layout:comb]
{
  token_id : token_id;
  buyer : address;
  token_origin : address;
}

type withdraw_offer_param = 
[@layout:comb]
{
  token_id : token_id;
  token_origin : address;
}

type accept_offer_param = 
[@layout:comb] 
{ 
  buyer : address;
  token_id : token_id;
  token_origin : address;
} 

type update_times_param = 
[@layout:comb]
{ 
  start_time : timestamp; 
  end_time : timestamp 
}

type update_swap_actions =
| Update_price of nat
| Update_times of update_times_param
| Update_duration of nat
| Update_starting_price of nat
| Update_reserved_address of address

type update_swap_param =
[@layout:comb]
{
  swap_id : swap_id;
  action : update_swap_actions;
}

type add_collection_param = address

type remove_collection_param = address

type parameter = 
| SetPause of bool 
| UpdateFee of update_fee_param 
| UpdateRoyalties of update_royalties_param
| UpdateOracleAddress of address
| UpdateAllowedTokens of update_allowed_tokens_param
| AddCollection of add_collection_param
| RemoveCollection of remove_collection_param
| UpdateRoyaltiesAddress of update_royalties_address_param
| UpdateTreasuryAddress of update_treasury_address_param
| SetOracleTolerance of set_oracle_tolerance_param
| UpdateAdmin of address
// | UpdateMultisig of update_multisig_param
| AddToMarketplace of add_to_marketplace_param 
| RemoveFromMarketplace of remove_from_marketplace_param 
| Collect of collect_marketplace_param
| SendOffer of offer_param 
| UpdateOffer of offer_param
| WithdrawOffer of withdraw_offer_param 
| AcceptOffer of accept_offer_param
| MakeCounterOffer of counter_offer_param
| WithdrawCounterOffer of withdraw_counter_offer_param
| AcceptCounterOffer of accept_counter_offer_param
| UpdateSwap of update_swap_param
| AddSingleToken of string
| RemoveSingleToken of string

type return = operation list * storage 

#endif 
