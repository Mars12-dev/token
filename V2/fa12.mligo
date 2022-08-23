type transfer =
  [@layout:comb]
  { [@annot:from] address_from : address;
    [@annot:to] address_to : address;
    value : nat }

type approve =
  [@layout:comb]
  { spender : address;
    value : nat }

type mintOrBurn =
  [@layout:comb]
  { value : nat ;
    address : address }

type allowance_key =
  [@layout:comb]
  { owner : address;
    spender : address }

type getAllowance =
  [@layout:comb]
  { request : allowance_key;
    callback : nat contract }

type getBalance =
  [@layout:comb]
  { owner : address;
    callback : nat contract }

type get_admin_param = 
[@layout:comb]
{
    request : unit;
    callback : address contract;
}

type getTotalSupply =
  [@layout:comb]
  { request : unit ;
    callback : nat contract }

type tokens = (address, nat) big_map
type allowances = (allowance_key, nat) big_map

type token_metadata_entry = {
  token_id: nat;
  token_info: (string, bytes) map;
}
type storage =
  [@layout:comb]
  { tokens : tokens;
    allowances : allowances;
    admin : address;
    total_supply : nat;
    metadata: (string, bytes) big_map;
    token_metadata : (nat, token_metadata_entry) big_map;
    paused : bool;
  }

type parameter =
  | Transfer of transfer
  | Approve of approve
  | Mint of mintOrBurn
  | Burn of mintOrBurn
  | SetAdmin of address
  | SetPause of bool
  | GetAllowance of getAllowance
  | GetBalance of getBalance
  | GetTotalSupply of getTotalSupply
  | GetAdmin of get_admin_param

type return = operation list * storage

[@inline]
let maybe (n : nat) : nat option =
  if n = 0n
  then (None : nat option)
  else Some n

let transfer (param : transfer) (store : storage) : return =
    if store.paused then
        (failwith("contract paused") : return)
    else 
        let allowances = store.allowances in
        let tokens = store.tokens in
        let allowances =
          if (Tezos.get_sender ()) = param.address_from
          then allowances
          else
            let allowance_key = { owner = param.address_from ; spender = (Tezos.get_sender ()) } in
            let authorized_value =
              match Big_map.find_opt allowance_key allowances with
              | Some value -> value
              | None -> 0n in
            let authorized_value =
              match is_nat (authorized_value - param.value) with
              | None -> (failwith "NotEnoughAllowance" : nat)
              | Some authorized_value -> authorized_value in
            Big_map.update allowance_key (maybe authorized_value) allowances in
        let tokens =
          let from_balance =
            match Big_map.find_opt param.address_from tokens with
            | Some value -> value
            | None -> 0n in
          let from_balance =
            match is_nat (from_balance - param.value) with
            | None -> (failwith "NotEnoughBalance" : nat)
            | Some from_balance -> from_balance in
          Big_map.update param.address_from (maybe from_balance) tokens in
        let tokens =
          let to_balance =
            match Big_map.find_opt param.address_to tokens with
            | Some value -> value
            | None -> 0n in
          let to_balance = to_balance + param.value in
          Big_map.update param.address_to (maybe to_balance) tokens in
        (([] : operation list), { store with tokens = tokens; allowances = allowances })

let approve (param : approve) (store : storage) : return =
    if store.paused then
        (failwith("contract paused") : return)
    else
        let allowances = store.allowances in
        let allowance_key = { owner = (Tezos.get_sender ()) ; spender = param.spender } in
        let previous_value =
          match Big_map.find_opt allowance_key allowances with
          | Some value -> value
          | None -> 0n in
          if previous_value > 0n && param.value > 0n then 
            (failwith "UnsafeAllowanceChange")
          else 
            let allowances = Big_map.update allowance_key (maybe param.value) allowances in
            (([] : operation list), { store with allowances = allowances })
        

let mint (param : mintOrBurn) (store : storage) : return =
    if store.paused then
        (failwith("contract paused") : return)
    else if (Tezos.get_sender ()) <> store.admin
        then (failwith("OnlyAdmin") : return)
    else 
        let tokens = store.tokens in
        let old_balance =
          match Big_map.find_opt param.address tokens with
          | None -> 0n
          | Some bal -> bal in
        let new_balance = old_balance + param.value in
        let tokens = Big_map.update param.address (Some new_balance) store.tokens in
        let total_supply = store.total_supply + param.value in
        (([] : operation list), { store with tokens = tokens ; total_supply = total_supply })

let burn (param : mintOrBurn) (store : storage) : return =
    if store.paused then
        (failwith("contract paused") : return)
    else
        if (Tezos.get_sender ()) <> store.admin then
            (failwith("only admin") : return)
        else
            let tokens = store.tokens in
            let old_balance = 
                match Big_map.find_opt param.address tokens with
                | None -> (failwith("no balance for this address") : nat)
                | Some n -> n in
            let new_balance = 
                match is_nat (old_balance - param.value) with
                | None -> (failwith("cannot burn more than the target's balance") : nat)
                | Some b -> b in
            let tokens = Big_map.update param.address (maybe new_balance) store.tokens in
            let total_supply = abs (store.total_supply - param.value) in
            ([] : operation list), { store with tokens = tokens; total_supply = total_supply}

let set_admin (new_admin : address) (store : storage) : return =
    if (Tezos.get_sender ()) <> store.admin then
        (failwith("only admin") : return)
    else
        ([] : operation list), {store with admin = new_admin}

let set_pause (paused : bool) (store : storage) : return =
    if (Tezos.get_sender ()) <> store.admin then
        (failwith("only_admin") : return)
    else
        ([] : operation list), { store with paused = paused }

let get_admin (param : get_admin_param) (store : storage) : operation list = 
    let admin = store.admin in
    [Tezos.transaction admin 0mutez param.callback]

let getAllowance (param : getAllowance) (store : storage) : operation list =
    let value =
      match Big_map.find_opt param.request store.allowances with
      | Some value -> value
      | None -> 0n in
    [Tezos.transaction value 0mutez param.callback]

let getBalance (param : getBalance) (store : storage) : operation list =
    let value =
      match Big_map.find_opt param.owner store.tokens with
      | Some value -> value
      | None -> 0n in
    [Tezos.transaction value 0mutez param.callback]

let getTotalSupply (param : getTotalSupply) (store : storage) : operation list =
    let total = store.total_supply in
    [Tezos.transaction total 0mutez param.callback]

let main (param, store : parameter * storage) : return =
    if (Tezos.get_amount ()) <> 0mutez then 
        (failwith("DontSendTez") : return)
    else
        match param with
        | Transfer p -> transfer p store
        | Approve p -> approve p store
        | Mint p -> mint p store
        | Burn p -> burn p store
        | SetAdmin p -> set_admin p store
        | SetPause p -> set_pause p store
        | GetAllowance p -> (getAllowance p store, store)
        | GetBalance p -> (getBalance p store, store)
        | GetTotalSupply p -> (getTotalSupply p store, store)
        | GetAdmin p -> (get_admin p store, store)
