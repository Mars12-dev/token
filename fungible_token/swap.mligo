#include "marketplace_interface.mligo"


let fa12_transfer (fa12_address : address) (from_ : address) (to_ : address) (value : nat) : operation =
  let fa12_contract : fa12_contract_transfer contract =
    match (Tezos.get_entrypoint_opt "%transfer" fa12_address : fa12_contract_transfer contract option) with
    | None -> (failwith(error_FA12_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT) : fa12_contract_transfer contract)
    | Some contract -> contract in
    let transfer = {address_from = from_; address_to = to_; value = value} in
    Tezos.transaction transfer 0mutez fa12_contract

let set_pause (param : bool) (store : storage) : return =
  if Tezos.sender <> store.admin then
       (failwith(error_CALLER_IS_NOT_ADMIN) : return)
  else
    ([] : operation list), {store with paused = param}

let set_token_in (param : address) (store : storage) : return =
  if Tezos.sender <> store.admin then
       (failwith(error_CALLER_IS_NOT_ADMIN) : return)
  else
    ([] : operation list), {store with token_in_address = param}

let set_token_out (param : address) (store : storage) : return =
  if Tezos.sender <> store.admin then
       (failwith(error_CALLER_IS_NOT_ADMIN) : return)
  else
    ([] : operation list), {store with token_out_address = param}

let set_token_price (param : nat) (store : storage) : return =
  if Tezos.sender <> store.admin then
       (failwith(error_CALLER_IS_NOT_ADMIN) : return)
  else
    ([] : operation list), {store with token_price = param}


let buy(param : buy_param) (store : storage) : return =
  if store.paused then
     (failwith(error_SWAP_IS_PAUSED) : return)
 else
  let ops = ([] : operation list) in  
  let ops = fa12_transfer store.token_in_address Tezos.sender  store.treasury  param.amount :: ops in
  let ops = fa12_transfer store.token_out_address Tezos.self_addres Tezos.sender param.amount/store.token_price :: ops in

(ops, store)

let main (action, store : parameter * storage) : return =
 match action with
 | SetPause p -> set_pause p store
 | SetTokenIn p -> set_token_in p store
 | SetTokenOut p -> set_token_Out p store
 |Buy p -> buy p store


