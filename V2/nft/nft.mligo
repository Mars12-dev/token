(**
Implementation of the FA2 interface for the NFT contract supporting multiple
types of NFTs. Each NFT type is represented by the range of token IDs - `token_def`.
 *)


#include "../common/interface.mligo"

type storage = nft_storage

type return = operation list * storage
[@inline]
let prepare_multisig (type p) (entrypoint_name: string) (param: p) (func: unit -> operation list) (store : storage) : operation list =
    match (Tezos.get_entrypoint_opt "%callMultisig" store.multisig : call_param contract option ) with
    | None -> (failwith("no call entrypoint") : operation list)
    | Some contract ->
        let packed = Bytes.pack param in
        let param_hash = Crypto.sha256 packed in
        let entrypoint_signature =
          {
            name = entrypoint_name;
            params = param_hash;
            source_contract = Tezos.get_self_address ();
          }
        in
        let call_param =
        {
          entrypoint_signature = entrypoint_signature;
          callback = func;
        }
        in
        let set_storage = Tezos.transaction call_param 0mutez contract in
        [set_storage]

#include "./fa2_errors.mligo"
#include "./fa2_interface.mligo"
#include "./fa2_operator_lib.mligo"
#include "entrypoints/balance_of.mligo"
#include "entrypoints/mint.mligo"
#include "entrypoints/burn.mligo"
#include "entrypoints/set_pause.mligo"
#include "entrypoints/set_burn_pause.mligo"
#include "entrypoints/transfer.mligo"
#include "entrypoints/update_contract_metadata.mligo"
#include "entrypoints/update_token_metadata.mligo"
#include "entrypoints/update_metadata_with_function.mligo"
#include "entrypoints/update_multisig_address.mligo"
#include "entrypoints/update_operators.mligo"
#include "entrypoints/update_proxy.mligo"


let main (param, storage : fa2_entry_points * storage) : return =
  match param with
  | UpdateProxy action ->
      update_proxy (action, storage)
  | Mint param ->
    (([] : operation list), mint (param, storage))
  | Burn param ->
    (([] : operation list), burn (param, storage))
  | Transfer txs ->
    if storage.paused then 
      (failwith (error_FA2_CONTRACT_IS_PAUSED) : return) 
    else 
      let new_ledger = transfer
        (txs, default_operator_validator, storage.operators, storage.ledger) in
      let new_storage = { storage with ledger = new_ledger; } in
      ([] : operation list), new_storage
  | Balance_of p ->
    let op = get_balance (p, (storage.ledger, storage.token_metadata)) in
    [op], storage
  | Update_operators updates ->
    let new_ops = fa2_update_operators (updates, storage.operators) in
    let new_storage = { storage with operators = new_ops; } in
    ([] : operation list), new_storage
  | SetPause p -> set_pause p storage 
  | SetBurnPause p -> set_burn_pause p storage 
  | UpdateMultisig p -> update_multisig_address p storage
  | UpdateTokenMetadata p -> update_token_metadata p storage
  | UpdateMetadataWithFunction p -> update_metadata_with_function p storage
  | UpdateContractMetadata p -> update_contract_metadata p storage
