#include "../common/interface.mligo"

type token_origin = address

type royalties_map = ((token_origin * token_id), royalties_info) big_map

type storage = 
[@layout:comb]
{
    proxy : address set;
    multisig : address;
    royalties : royalties_map;
    paused : bool;
}

type return = operation list * storage

type assign_param =
[@layout:comb]
{
  token_origin : token_origin;
  current_id : token_id;
  last_id : token_id;
  issuer : address;
  royalties : nat;
  royalties_map : royalties_map;
}

type parameter = 
| UpdateProxy of update_proxy_param
| ConfigRoyalties of config_royalties_param
| ConfigCollectionRoyalties of configure_collection_royalties_param
| SetPause of bool
| UpdateMultisig of update_multisig_address_param