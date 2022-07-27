#if !MARKETPLACE_FUNCTIONS
#define MARKETPLACE_FUNCTIONS

[@inline]
let mutez_to_natural (a: tez) : nat =  a / 1mutez

[@inline]
let natural_to_mutez (a: nat): tez = a * 1mutez

[@inline] let assert_with_code (condition : bool) (code : nat) : unit =
  if (not condition) then failwith(code)
  else ()

[@inline] let calculate_price (start_time, duration, starting_price, token_price : timestamp * int * nat * nat) : nat =
  match is_nat ((start_time + duration) - (Tezos.get_now ())) with
  | None -> token_price
  | Some t -> t * abs (starting_price - token_price)/ abs duration + token_price

[@inline] let convert_tokens (input_token : token_symbol) (input_amount : nat) (output_token : token_symbol) (store : storage) : nat =
  if input_token = output_token then
    input_amount
  else
  (* 
    The harbinger normalizer contract converts from all currencies only to USD
    we have to handle different cases differently:
    1: conversion fits the direct conversion cases of harbinger (XTZ-USD, ETH-USD, etc)
    2: conversion is the opposite of direct conversion cases of harbinger (USD-XTZ, USD-ETH, etc)
    3: conversion is between two currencies different than USD (XTZ-ETH, ETH-XTZ, etc)
 *)
    let (first_pair, first_ordered, second_pair) =
      if output_token = "USD" then
      (* case 1 *)
        match Big_map.find_opt (input_token, output_token) store.available_pairs with
        | None ->  (failwith(error_NO_AVAILABLE_CONVERSION_RATE) : string * bool * string)
        | Some pair -> (pair, true, "")
      else if input_token = "USD" then
      (* case 2 *)
        match Big_map.find_opt (output_token, input_token) store.available_pairs with
        | None -> (failwith(error_NO_AVAILABLE_CONVERSION_RATE) : string * bool * string)
        | Some pair -> (pair, false, "")
      else
      (* case 3 *)
        let first = 
          match Big_map.find_opt (input_token, "USD") store.available_pairs with
          | None -> (failwith(error_NO_AVAILABLE_CONVERSION_RATE) : string)
          | Some pair -> pair in
        let second = 
          match Big_map.find_opt (output_token, "USD") store.available_pairs with
          | None -> (failwith(error_NO_AVAILABLE_CONVERSION_RATE) : string)
          | Some pair -> pair in
        (first, true, second) in

    (* convert according to the different 5 cases *)
    let output_amount =
      let mu = 1_000_000n in
      if second_pair = "" then
      (* cases 1 & 2 *)
        let (last_time, conversion_rate) =
          match (Tezos.call_view "getPrice" first_pair store.oracle : (timestamp * nat) option) with
          | None -> (failwith(error_ORACLE_FAILED_TO_SUPPLY_CONVERSION_RATE) : timestamp * nat)
          | Some (tm, cr) -> (tm, cr) in
        if last_time < (Tezos.get_now ()) - store.oracle_tolerance then
          (failwith error_ORACLE_NOT_RESPONDING : nat)
        else if first_ordered then
        (* case 1 *)
          input_amount * conversion_rate / mu
        else
        (* case 2 *)
          input_amount * mu / conversion_rate
      else
      (* case 3 *)
        let (last_time, first_conversion_rate) =
          match (Tezos.call_view "getPrice" first_pair store.oracle : (timestamp * nat) option) with
          | None -> (failwith(error_ORACLE_FAILED_TO_SUPPLY_CONVERSION_RATE) : timestamp * nat)
          | Some (tm, cr) -> (tm, cr) in
        if last_time < (Tezos.get_now ()) - store.oracle_tolerance then
          (failwith error_ORACLE_NOT_RESPONDING : nat)
        else
        let (last_time, second_conversion_rate) =
          match (Tezos.call_view "getPrice" second_pair store.oracle : (timestamp * nat) option) with
          | None -> (failwith(error_ORACLE_FAILED_TO_SUPPLY_CONVERSION_RATE) : timestamp * nat)
          | Some (tm, cr) -> (tm, cr) in
        if last_time < (Tezos.get_now ()) - store.oracle_tolerance then
          (failwith error_ORACLE_NOT_RESPONDING : nat)
        else
          input_amount * first_conversion_rate / second_conversion_rate in
    output_amount

[@inline]
let token_transfer (token_address: address) (txs : transfer list) : operation =
    let token_contract: token_contract_transfer contract =
    match (Tezos.get_entrypoint_opt "%transfer" token_address : token_contract_transfer contract option) with
    | None -> (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT : token_contract_transfer contract)
    | Some contract -> contract in
    let transfers = List.map (fun (tx : transfer) -> tx.from_, List.map (fun  (dst : transfer_destination) -> (dst.to_, (dst.token_id, dst.amount))) tx.txs) txs in
    Tezos.transaction transfers 0mutez token_contract

[@inline]
let xtz_transfer (to_ : address) (amount_ : tez) : operation =
    let to_contract : unit contract =
        match (Tezos.get_contract_opt to_ : unit contract option) with
        | None -> (failwith error_INVALID_TO_ADDRESS : unit contract)
        | Some c -> c in
    Tezos.transaction () amount_ to_contract

[@inline]
let fa12_transfer (fa12_address : address) (from_ : address) (to_ : address) (value : nat) : operation =
  let fa12_contract : fa12_contract_transfer contract =
    match (Tezos.get_entrypoint_opt "%transfer" fa12_address : fa12_contract_transfer contract option) with
    | None -> (failwith(error_FA12_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT) : fa12_contract_transfer contract)
    | Some contract -> contract in
    let transfer = {address_from = from_; address_to = to_; value = value} in
    Tezos.transaction transfer 0mutez fa12_contract

[@inline]
let fa_transfer (ops : operation list) (value : nat) (symbol : token_symbol) (from_ : address) (to_ : address) (store : storage) : operation list =
  let fun_token = 
      match Big_map.find_opt symbol store.allowed_tokens with
      | None -> (failwith(error_TOKEN_SYMBOL_UNLISTED) : fun_token)
      | Some fun_token -> fun_token in
    if fun_token.fa_type = "fa1.2" then
      fa12_transfer fun_token.fa_address from_ to_ value :: ops
    else if fun_token.fa_type = "fa2" then
      token_transfer 
        fun_token.fa_address 
          [
            {
              from_ = from_;
              txs =
                [{
                  to_ = to_;
                  token_id = 0n;
                  amount = value;
                }]
            }
          ] :: ops
    else 
      (failwith(error_NO_VALID_TRANSFER_FOR_TOKEN) : operation list)

[@inline]
let payment_transfer (ops : operation list) (value : nat) (symbol : token_symbol) (from_ : address) (to_ : address) (store : storage) : operation list =
  if value > 0n then
    if symbol = "XTZ" then
      xtz_transfer to_ (natural_to_mutez value) :: ops
    else
      fa_transfer ops value symbol from_ to_ store
  else ops

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
            source_contract = (Tezos.get_self_address ());
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
  if (Tezos.get_sender ()) <> store.multisig then
    let sender_address = (Tezos.get_self_address ()) in
    let func () =
      match (Tezos.get_entrypoint_opt "%setPause" sender_address : bool contract option) with
      | None -> (failwith("no setPause entrypoint") : operation list)
      | Some set_pause_entrypoint -> [Tezos.transaction param 0mutez set_pause_entrypoint] in
    (prepare_multisig "setPause" param func store), store
  else
    ([] : operation list), {store with paused = param}

let update_fee (param : update_fee_param) (store : storage) : return =
    if (Tezos.get_sender ()) <> store.multisig then
      let sender_address = (Tezos.get_self_address ()) in
      let func () =
        match (Tezos.get_entrypoint_opt "%updateFee" sender_address : update_fee_param contract option) with
          | None -> (failwith("no updateFee entrypoint") : operation list)
          | Some update_fee_entrypoint ->
            [Tezos.transaction param 0mutez update_fee_entrypoint]
        in
        (prepare_multisig "updateFee" param func store), store
    else
        ([] : operation list), { store with management_fee_rate = param }

let add_collection (param : add_collection_param) (store : storage) : return =
    if (Tezos.get_sender ()) <> store.multisig then
        let sender_address = (Tezos.get_self_address ()) in
        let func () =
            match (Tezos.get_entrypoint_opt "%addCollection" sender_address : add_collection_param contract option) with
            | None -> (failwith("no addCollection entrypoint") : operation list)
            | Some add_collection_entrypoint -> [Tezos.transaction param 0mutez add_collection_entrypoint] in
        (prepare_multisig "addCollection" param func store), store
    else
        let collections = Set.add param store.collections in
        ([] : operation list), {store with collections = collections}

let remove_collection (param : remove_collection_param) (store : storage) : return =
    if (Tezos.get_sender ()) <> store.multisig then
        let sender_address = (Tezos.get_self_address ()) in
        let func () =
            match (Tezos.get_entrypoint_opt "%removeCollection" sender_address : remove_collection_param contract option) with
            | None -> (failwith("no removeCollection entrypoint") : operation list)
            | Some remove_collection_entrypoint -> [Tezos.transaction param 0mutez remove_collection_entrypoint] in
        (prepare_multisig "removeCollection" param func store), store
    else
        let collections = Set.remove param store.collections in
        ([] : operation list), {store with collections = collections}

let update_royalties (param : update_royalties_param) (store : storage) : return =
    if (Tezos.get_sender ()) <> store.multisig then
      let sender_address = (Tezos.get_self_address ()) in
      let func () =
        match (Tezos.get_entrypoint_opt "%updateRoyalties" sender_address : update_royalties_param contract option) with
          | None -> (failwith("no updateRoyalties entrypoint") : operation list)
          | Some update_royalties_entrypoint ->
            [Tezos.transaction param 0mutez update_royalties_entrypoint]
        in
        (prepare_multisig "updateRoyalties" param func store), store
    else
        ([] : operation list), { store with royalties_rate = param }

let update_royalties_address (param : update_royalties_address_param) (store : storage) : return =
    if (Tezos.get_sender ()) <> store.multisig then
      let sender_address = (Tezos.get_self_address ()) in
      let func () =
        match (Tezos.get_entrypoint_opt "%updateRoyaltiesAddress" sender_address : update_royalties_address_param contract option) with
          | None -> (failwith("no updateRoyaltiesAddress entrypoint") : operation list)
          | Some update_royalties_address_entrypoint ->
            [Tezos.transaction param 0mutez update_royalties_address_entrypoint]
        in
        (prepare_multisig "updateRoyaltiesAddress" param func store), store
    else
        ([] : operation list), { store with royalties_address = param }

let update_treasury_address (param : update_treasury_address_param) (store : storage) : return =
    if (Tezos.get_sender ()) <> store.multisig then
      let sender_address = (Tezos.get_self_address ()) in
      let func () =
        match (Tezos.get_entrypoint_opt "%updateTreasuryAddress" sender_address : update_treasury_address_param contract option) with
          | None -> (failwith("no updateTreasuryAddress entrypoint") : operation list)
          | Some update_treasury_address_entrypoint ->
            [Tezos.transaction param 0mutez update_treasury_address_entrypoint]
        in
        (prepare_multisig "updateTreasuryAddress" param func store), store
    else
        ([] : operation list), { store with treasury = param }

let update_oracle_address (param : address) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.multisig then
    let sender_address = (Tezos.get_self_address ()) in
    let func () =
      match (Tezos.get_entrypoint_opt "%updateOracleAddress" sender_address : address contract option) with
        | None -> (failwith("no updateOracleAddress entrypoint") : operation list)
        | Some update_oracle_entrypoint ->
          [Tezos.transaction param 0mutez update_oracle_entrypoint]
      in
      (prepare_multisig "updateOracleAddress" param func store), store
  else
    ([] : operation list), { store with oracle = param }

let update_allowed_tokens (param : update_allowed_tokens_param) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.multisig then
    let sender_address = (Tezos.get_self_address ()) in
    let func () =
      match (Tezos.get_entrypoint_opt "%updateAllowedTokens" sender_address : update_allowed_tokens_param contract option) with
        | None -> (failwith("no updateAllowedTokens entrypoint") : operation list)
        | Some update_allowed_tokens_entrypoint ->
          [Tezos.transaction param 0mutez update_allowed_tokens_entrypoint]
      in
      (prepare_multisig "updateAllowedTokens" param func store), store
  else
    match param.direction with
    | Remove_token ->
      let new_allowed_tokens = Big_map.update param.token_symbol (None : fun_token option) store.allowed_tokens in
      let new_available_pairs = Big_map.update (param.token_symbol, "USD") (None : string option) store.available_pairs in
      ([] : operation list), {store with allowed_tokens = new_allowed_tokens; available_pairs = new_available_pairs}
    | Add_token p ->
      let fun_token = 
        {
          fa_address = p.fa_address; 
          token_symbol = param.token_symbol;
          fa_type = p.fa_type;
        } in
      if Big_map.mem param.token_symbol store.allowed_tokens then
        (failwith(error_TOKEN_SYMBOL_LISTED) : return)
      else if Big_map.mem (param.token_symbol, "USD") store.available_pairs then
        (failwith(error_PAIR_ALREADY_EXISTS) : return)
      else
        let new_allowed_tokens = Big_map.update param.token_symbol (Some fun_token) store.allowed_tokens in
        let pair = param.token_symbol ^ "-USD" in
        let new_available_pairs = Big_map.update (param.token_symbol, "USD") (Some pair) store.available_pairs in
        ([] : operation list), {store with allowed_tokens = new_allowed_tokens; available_pairs = new_available_pairs}

let set_oracle_tolerance (param : set_oracle_tolerance_param) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.multisig then
    let sender_address = (Tezos.get_self_address ()) in
    let func () =
      match (Tezos.get_entrypoint_opt "%setOracleTolerance" sender_address : set_oracle_tolerance_param contract option) with
        | None -> (failwith("no setOracleTolerance entrypoint") : operation list)
        | Some set_oracle_tolerance_entrypoint ->
          [Tezos.transaction param 0mutez set_oracle_tolerance_entrypoint]
      in
      (prepare_multisig "setOracleTolerance" param func store), store
  else
    ([] : operation list), { store with oracle_tolerance = param }

let update_multisig (param : update_multisig_param) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.multisig then
    let sender_address = (Tezos.get_self_address ()) in
    let func () =
      match (Tezos.get_entrypoint_opt "%updateMultisig" sender_address : update_multisig_param contract option) with
        | None -> (failwith("no updateMultisig entrypoint") : operation list)
        | Some update_multisig_entrypoint ->
          [Tezos.transaction param 0mutez update_multisig_entrypoint]
      in
      (prepare_multisig "updateMultisig" param func store), store
  else
    ([] : operation list), { store with multisig = param }

#endif