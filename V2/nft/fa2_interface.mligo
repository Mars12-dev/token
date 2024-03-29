#if !FA2_INTERFACE
#define FA2_INTERFACE

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

type balance_of_request =
[@layout:comb]
{
  owner : address;
  token_id : token_id;
}

type balance_of_response =
[@layout:comb]
{
  request : balance_of_request;
  balance : nat;
}

type balance_of_param =
[@layout:comb]
{
  requests : balance_of_request list;
  callback : (balance_of_response list) contract;
}

type operator_param =
[@layout:comb]
{
  owner : address;
  operator : address;
  token_id: token_id;
}

type update_operator =
[@layout:comb]
  | Add_operator of operator_param
  | Remove_operator of operator_param



(**
Optional type to define view entry point to expose token_metadata on chain or
as an external view
 *)
type token_metadata_param =
[@layout:comb]
{
  token_ids : token_id list;
  handler : (token_metadata list) -> unit;
}

type update_multisig_address_param = address




type fa2_entry_points =
  | UpdateProxy of update_proxy_param
  | Mint of nft_mint_param
  | Burn of nft_burn_param
  | Transfer of transfer list
  | Balance_of of balance_of_param
  | Update_operators of update_operator list
  | SetPause of bool
  | SetBurnPause of bool
  | UpdateMultisig of update_multisig_address_param
  | UpdateTokenMetadata of nft_update_metadata_param
  | UpdateContractMetadata of bytes
  | UpdateMetadataWithFunction  of update_metadata_with_function_param






(*
 TZIP-16 contract metadata storage field type.
 The contract storage MUST have a field
 `metadata : contract_metadata`
*)
type contract_metadata = (string, bytes) big_map

(* FA2 hooks interface *)

type transfer_destination_descriptor =
[@layout:comb]
{
  to_ : address option;
  token_id : token_id;
  amount : nat;
}

type transfer_descriptor =
[@layout:comb]
{
  from_ : address option;
  txs : transfer_destination_descriptor list
}

type transfer_descriptor_param =
[@layout:comb]
{
  batch : transfer_descriptor list;
  operator : address;
}



(*
Entrypoints for sender/receiver hooks
type fa2_token_receiver =
  ...
  | Tokens_received of transfer_descriptor_param
type fa2_token_sender =
  ...
  | Tokens_sent of transfer_descriptor_param
*)

#endif
