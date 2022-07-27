#if !COMMON_INTERFACE
#define COMMON_INTERFACE

type token_symbol = string

type metadata_url = string

type fun_token =
[@layout:comb]
{
  token_symbol : token_symbol;
  fa_address : address;
  fa_type : string;
}

type token_id = nat

type token_origin = address

(* NFT Types *)

(* range of nft tokens *)
type token_def =
[@layout:comb]
{
  from_ : nat;
  to_ : nat;
}

type token_metadata = (string, bytes) map

type token_metadata_item = 
[@layout:comb]
{
  token_id: token_id;
  token_info: token_metadata;
}

(*
One of the options to make token metadata discoverable is to declare
`token_metadata : token_metadata_storage` field inside the FA2 contract storage
*)
type token_metadata_storage = (token_id, token_metadata_item) big_map

type nft_meta = (string, bytes) big_map

type token_storage = 
[@layout:comb]
{
  token_defs : token_def set;
  metadata : nft_meta;
}

type ledger_key = address * token_id

type ledger_amount = nat

type ledger = (ledger_key, ledger_amount) big_map

(**
(owner, operator, token_id) -> unit
To be part of FA2 storage to manage permitted operators
*)
type operator_storage = ((address * (address * token_id)), unit) big_map

type nft_storage = 
[@layout:comb]
{
  ledger : ledger;
  operators : operator_storage;
  metadata : nft_meta;
  token_metadata : token_metadata_storage;
  proxy : address set;
  paused : bool;
  multisig : address;
}

(*     *)


type offer_id =
[@layout:comb]
{
  token_id : token_id;
  buyer : address;
  token_origin : token_origin;
}

type counter_offer_id = 
[@layout:comb]
{
  token_id : token_id;
  buyer : address;
  seller : address;
  token_origin : token_origin;
}

type token_key = 
[@layout:comb]
{
  token_id : token_id;
  origin : token_origin;
}

type transfer_destination =
[@layout:comb]
{
  to_ : address;
  token_id : token_id;
  amount : nat;
}

type transfer =
[@layout:comb]
{
  from_ : address;
  txs : transfer_destination list;
}

type swap_id = nat

type royalties_amount = nat

type royalties_info = 
[@layout:comb]
{
  issuer: address;
  royalties: royalties_amount;
}

type entrypoint_signature =
{
    name : string;
    params : bytes;
    source_contract : address;
}

type call_param =
[@layout:comb]
{
    entrypoint_signature : entrypoint_signature;
    callback : unit -> operation list;
}

type update_royalties_param = nat

type update_fee_param =  nat 

type update_admin_param = 
| Remove of address 
| Add of address

type update_proxy_param = 
[@layout:comb]
| Add_proxy of address
| Remove_proxy of address

type update_nft_address_param = address 

type update_royalties_address_param = address

type update_multisig_address_param = address

type nft_mint_param = 
[@layout:comb] 
{ 
  token_id: nat; 
  token_metadata: (string, bytes) map; 
  amount_ : nat;
  owner : address;
} 

type config_royalties_param = 
[@layout:comb]
{
  token_id : token_id;
  token_origin : token_origin;
  royalties : nat;
}

type configure_collection_royalties_param =
[@layout:comb]
{
  nft_address : token_origin;
  first_id : token_id;
  last_id : token_id;
  royalties : nat;
}

type add_token_param =
{
  fa_address : address;
  fa_type : string;
}

type update_token_direction =
| Add_token of add_token_param
| Remove_token of unit

type update_allowed_tokens_param = 
[@layout:comb]
{
  token_symbol : token_symbol;
  direction : update_token_direction;
}

type collect_auction_param = swap_id

type collect_marketplace_param = 
[@layout:comb]
{
  swap_id : swap_id;
  token_amount : nat;
  token_symbol : token_symbol;
  amount_ft : nat; 
}

type swap_royalties_param = 
[@layout:comb] 
{ 
  token_id : token_id; 
  swap_id : swap_id; 
  token_amount : nat; 
} 

type token_contract_transfer = (address * (address * (token_id * nat)) list) list 

type fa12_contract_transfer =
[@layout:comb]
{
  [@annot:from] address_from : address;
  [@annot:to] address_to : address;
  value : nat 
}

type deposit_param =
[@layout:comb]
{
    token : token_symbol;
    fa12_address : address;
    token_amount : nat;
}

type nft_update_metadata_param =
[@layout:comb]
{
  token_id : token_id;
  metadata : (string, bytes) map;
}

type set_oracle_tolerance_param = int

type update_multisig_param = address

type update_treasury_address_param = address

type admin_param = 
| Set_pause of bool
| Update_fee of update_fee_param
| Update_nft_address of update_nft_address_param
| Update_royalties_address of update_royalties_address_param
| Update_oracle_address of address
| Update_allowed_tokens of update_allowed_tokens_param

#endif