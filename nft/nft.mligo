(**
Implementation of the FA2 interface for the NFT contract supporting multiple
types of NFTs. Each NFT type is represented by the range of token IDs - `token_def`.
 *)

#include "../common/interface.mligo"
#include "./fa2_errors.mligo"
#include "./fa2_interface.mligo"
#include "./fa2_operator_lib.mligo"


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


let set_pause (param : bool) (store : storage) : return =
  let sender_address = Tezos.get_self_address () in
  if (Tezos.get_sender ()) <> store.multisig then
        let func () =
      match (Tezos.get_entrypoint_opt "%setPause" sender_address : bool contract option) with
        | None -> (failwith("no setPause entrypoint") : operation list)
        | Some set_pause_entrypoint ->
          [Tezos.transaction param 0mutez set_pause_entrypoint]
      in
      (prepare_multisig "setPause" param func store), store
    else
    ([] : operation list), {store with paused = param}

(**
Retrieve the balances for the specified tokens and owners
@return callback operation
*)
let get_balance (p, (ledger, metadata) : balance_of_param * (ledger * token_metadata_storage)) : operation =
  let to_balance = fun (r : balance_of_request) ->
    let _token = match Big_map.find_opt r.token_id metadata with
      | None -> (failwith fa2_token_undefined : unit)
      | Some _token -> () in
    match Big_map.find_opt (r.owner, r.token_id) ledger with 
    | None -> { request = r; balance = 0n; }
    | Some o ->
      let bal = o in
      { request = r; balance = bal; }
  in
  let responses = List.map to_balance p.requests in
  Tezos.transaction responses 0mutez p.callback

(**
Update leger balances according to the specified transfers. Fails if any of the
permissions or constraints are violated.
@param txs transfers to be applied to the ledger
@param validate_op function that validates of the tokens from the particular owner can be transferred.
 *)
let transfer (txs, validate_op, ops_storage, ledger
    : (transfer list) * operator_validator * operator_storage * ledger) : ledger =
    (* process individual transfer *)
    let make_transfer = (fun (l, tx : ledger * transfer) ->
      List.fold
        (fun (ll, dst : ledger * transfer_destination) ->
            let tokens = Big_map.find_opt (tx.from_, dst.token_id) ll in
            match tokens with
            | None -> (failwith fa2_token_undefined : ledger)
            | Some t ->
              if t < dst.amount
              then (failwith fa2_insufficient_balance : ledger)
              else
                let new_to_amount = match Big_map.find_opt (dst.to_, dst.token_id) ll with
                | Some a -> a + dst.amount
                | None -> dst.amount in
                let new_from_amount = abs (t - dst.amount) in
                let _u = validate_op (tx.from_, (Tezos.get_sender ()), dst.token_id, ops_storage) in
                let new_ledger = Big_map.update (dst.to_, dst.token_id) (Some new_to_amount) ll in
                let new_ledger = 
                  if dst.amount = 0n then 
                    ll
                  else 
                    Big_map.update (tx.from_, dst.token_id) (Some new_from_amount) new_ledger in
                new_ledger
        ) tx.txs l
    )
    in

    List.fold make_transfer txs ledger

(** Finds a definition of the token type (token_id range) associated with the provided token id *)
let find_token_def (tid, token_defs : token_id * (token_def set)) : token_def =
  let tdef = Set.fold (fun (res, d : (token_def option) * token_def) ->
    match res with
    | Some _r -> res
    | None ->
      if tid >= d.from_ && tid < d.to_
      then  Some d
      else (None : token_def option)
  ) token_defs (None : token_def option)
  in
  match tdef with
  | None -> (failwith fa2_token_undefined : token_def)
  | Some d -> d

let update_multisig_address (param : update_multisig_address_param) (store : storage) : return =
    if (Tezos.get_sender ()) = store.multisig then
        ([] : operation list), { store with multisig = param }
    else
        let sender_address = Tezos.get_self_address () in
        let func () = 
            match (Tezos.get_entrypoint_opt "%updateMultisig" sender_address : update_multisig_address_param contract option) with
            | None -> (failwith("no updateMultisig entrypoint") : operation list)
            | Some update_multisig_entrypoint ->
                [Tezos.transaction param 0mutez update_multisig_entrypoint]
            in
        (prepare_multisig "update_multisig" param func store), store

let update_proxy (action, storage : update_proxy_param * storage) : return =
  let sender_address = Tezos.get_self_address () in
  if (Tezos.get_sender ()) <> storage.multisig then
        let func () =
      match (Tezos.get_entrypoint_opt "%updateProxy" sender_address : update_proxy_param contract option) with
        | None -> (failwith("no updateProxy entrypoint") : operation list)
        | Some update_proxy_entrypoint ->
          [Tezos.transaction action 0mutez update_proxy_entrypoint]
      in
      (prepare_multisig "updateProxy" action func storage), storage
  else
  match action with
  | Add_proxy p -> 
  if Set.mem p storage.proxy then
    (failwith(error_ADDRESS_ALREADY_PROXY) : return)
  else
    ([] : operation list), { storage with proxy = Set.add p storage.proxy }
  | Remove_proxy p ->
  if Set.mem p storage.proxy = false then
    (failwith(error_ADDRESS_NOT_PROXY) : return)
  else
    ([] : operation list), { storage with proxy = Set.remove p storage.proxy }

let mint (param, storage : nft_mint_param * storage) : return =
  if storage.paused then 
    (failwith (error_FA2_CONTRACT_IS_PAUSED) : return) 
  else if (Tezos.get_sender ()) <> storage.multisig then
  let sender_address = Tezos.get_self_address () in
        let func () =
      match (Tezos.get_entrypoint_opt "%mint" sender_address : nft_mint_param contract option) with
        | None -> (failwith("no mint entrypoint") : operation list)
        | Some mint_entrypoint ->
          [Tezos.transaction param 0mutez mint_entrypoint]
      in
      (prepare_multisig "mint" param func storage), storage
  else
    (* MINT TOKEN *)
    let { token_id;
          token_metadata;
          amount_;
          owner;
        } = param in
    let _check_if_token_already_exists = match Big_map.find_opt (owner, token_id) storage.ledger with
      | Some _v -> failwith "token aleardy exists"
      | None -> ()
    in
    let new_ledger = Big_map.update (owner, token_id) (Some amount_) storage.ledger in

    (* ADD METADATA URL *)
    let nft_metadata = {
      token_id = token_id ;
      token_info = token_metadata ;
    } in
    let new_token_metadata = Big_map.update
      token_id
      (Some nft_metadata)
      storage.token_metadata
    in
    ([] : operation list), { storage with ledger = new_ledger ; token_metadata = new_token_metadata }

let update_metadata (param : nft_update_metadata_param) (store : storage) : return =
  if store.paused then 
    (failwith (error_FA2_CONTRACT_IS_PAUSED) : return) 
  else if not Set.mem (Tezos.get_sender ()) store.proxy then
    failwith error_ONLY_PROXY_CAN_CALL_THIS_ENTRYPOINT
  else
    let { token_id; metadata } = param in
    let nft_metadata = 
      {
        token_id = token_id;
        token_info = metadata;
      } in
    let new_token_metadata =
      Big_map.update token_id (Some nft_metadata) store.token_metadata in
    ([] : operation list), { store with token_metadata = new_token_metadata }


let main (param, storage : fa2_entry_points * storage) : return =
  match param with
  | UpdateProxy action ->
      update_proxy (action, storage)
  | Mint param -> mint (param, storage)
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
  | UpdateMultisig p -> update_multisig_address p storage
  | UpdateMetadata p -> update_metadata p storage
