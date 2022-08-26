#include "../common/functions.mligo"

// [@inline]
// let prepare_multisig (type p) (entrypoint_name: string) (param: p) (func: unit -> operation list) (store : storage) : operation list =
//     match (Tezos.get_entrypoint_opt "%callMultisig" store.multisig : call_param contract option ) with
//     | None -> (failwith("no call entrypoint") : operation list)
//     | Some contract ->
//         let packed = Bytes.pack param in
//         let param_hash = Crypto.sha256 packed in
//         let entrypoint_signature =
//           {
//             name = entrypoint_name;
//             params = param_hash;
//             source_contract = (Tezos.get_self_address ());
//           }
//         in
//         let call_param =
//         {
//           entrypoint_signature = entrypoint_signature;
//           callback = func;
//         }
//         in
//         let set_storage = Tezos.transaction call_param 0mutez contract in
//         [set_storage]

[@inline]
let token_mint (metadata : nft_mint_param) (store : storage) : operation =
    let token_mint_entrypoint: nft_mint_param contract =
      match (Tezos.get_entrypoint_opt "%mint" store.nft_address : nft_mint_param contract option) with
      | None -> (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_MINT_ENTRYPOINT : nft_mint_param contract)
      | Some contract -> contract in
    Tezos.transaction metadata 0mutez token_mint_entrypoint

[@inline] let find_royalties (origin : address) (token_id : token_id) (store : storage) : royalties_info =
  if origin <> store.nft_address then
    {
      issuer = (Tezos.get_self_address ());
      royalties = 0n;
    }
  else
    match (Tezos.call_view "get_royalties" token_id store.royalties_address : royalties_info option) with
    | None -> (failwith("no royalties") : royalties_info)
    | Some r -> r 

[@inline]
let config_royalties (param : config_royalties_param) (store : storage) : operation =
    let config_royalties_entrypoint : config_royalties_param contract =
      match (Tezos.get_entrypoint_opt "%configRoyalties" store.royalties_address : config_royalties_param contract option) with
      | None -> (failwith(error_ROYALTIES_CONTRACT_MUST_HAVE_A_ROYALTIES_MINT_ENTRYPOINT) : config_royalties_param contract)
      | Some contract -> contract in
    Tezos.transaction param 0mutez config_royalties_entrypoint

let convert_tokens (input_token : token_symbol) (input_amount : nat) (output_token : token_symbol) (store : storage) : nat =
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
        let _, conversion_rate =
          match (Tezos.call_view "getPrice" first_pair store.oracle : (timestamp * nat) option) with
          | None -> (failwith(error_ORACLE_FAILED_TO_SUPPLY_CONVERSION_RATE) : timestamp * nat)
          | Some value -> value in
          if first_ordered then
          (* case 1 *)
            input_amount * conversion_rate / mu
          else
          (* case 2 *)
            input_amount * mu / conversion_rate
      else
      (* case 3 *)
        let _, first_conversion_rate =
          match (Tezos.call_view "getPrice" first_pair store.oracle : (timestamp * nat) option) with
          | None -> (failwith(error_ORACLE_FAILED_TO_SUPPLY_CONVERSION_RATE) : timestamp * nat)
          | Some value -> value in
        let _, second_conversion_rate =
          match (Tezos.call_view "getPrice" second_pair store.oracle : (timestamp * nat) option) with
          | None -> (failwith(error_ORACLE_FAILED_TO_SUPPLY_CONVERSION_RATE) : timestamp * nat)
          | Some value -> value in
          input_amount * first_conversion_rate / second_conversion_rate in
    output_amount

let find_fa12 (symbol : token_symbol) (store : storage) : address =
  let addr = match Big_map.find_opt symbol store.allowed_tokens with
  | None -> (failwith(error_TOKEN_INDEX_UNLISTED) : address)
  | Some token -> token.fa12_address in
  addr

let update_fee (param : update_fee_param) (store : storage) : return =
    if (Tezos.get_sender ()) <> store.admin then
      (failwith("not admin"))
    // if (Tezos.get_sender ()) <> store.multisig then
    //   let sender_address = (Tezos.get_self_address ()) in
    //   let func () =
    //     match (Tezos.get_entrypoint_opt "%updateFee" sender_address : update_fee_param contract option) with
    //       | None -> (failwith("no updateFee entrypoint") : operation list)
    //       | Some update_fee_entrypoint ->
    //         [Tezos.transaction param 0mutez update_fee_entrypoint]
    //     in
    //     (prepare_multisig "updateFee" param func store), store
    else
        ([] : operation list), { store with management_fee_rate = param }

let update_nft_address (param : update_nft_address_param) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.admin then
    (failwith("not admin"))
    // let sender_address = (Tezos.get_self_address ()) in
    // let func () =
    //   match (Tezos.get_entrypoint_opt "%updateNftAddress" sender_address : update_nft_address_param contract option) with
    //     | None -> (failwith("no updateNftAddress entrypoint") : operation list)
    //     | Some update_nft_entrypoint ->
    //       [Tezos.transaction param 0mutez update_nft_entrypoint]
    //   in
    //   (prepare_multisig "updateNftAddress" param func store), store
  else
    ([] : operation list), { store with nft_address = param }

let update_royalties_address (param : update_royalties_address_param) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.admin then
      (failwith("not admin"))
  // if (Tezos.get_sender ()) <> store.multisig then
  //   let sender_address = (Tezos.get_self_address ()) in
  //   let func () =
  //     match (Tezos.get_entrypoint_opt "%updateRoyaltiesAddress" sender_address : update_royalties_address_param contract option) with
  //       | None -> (failwith("no updateRoyaltiesAddress entrypoint") : operation list)
  //       | Some update_royalties_entrypoint ->
  //         [Tezos.transaction param 0mutez update_royalties_entrypoint]
  //     in
  //     (prepare_multisig "updateNftAddress" param func store), store
  else
    ([] : operation list), { store with royalties_address = param }

let update_oracle_address (param : address) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.admin then
      (failwith("not admin"))
  // if (Tezos.get_sender ()) <> store.multisig then
  //   let sender_address = (Tezos.get_self_address ()) in
  //   let func () =
  //     match (Tezos.get_entrypoint_opt "%updateOracleAddress" sender_address : address contract option) with
  //       | None -> (failwith("no updateOracleAddress entrypoint") : operation list)
  //       | Some update_oracle_entrypoint ->
  //         [Tezos.transaction param 0mutez update_oracle_entrypoint]
  //     in
  //     (prepare_multisig "updateOracleAddress" param func store), store
  else
    ([] : operation list), { store with oracle = param }


let update_allowed_tokens (param : update_allowed_tokens_param) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.admin then
      (failwith("not admin"))
  // if (Tezos.get_sender ()) <> store.multisig then
  //   let sender_address = (Tezos.get_self_address ()) in
  //   let func () =
  //     match (Tezos.get_entrypoint_opt "%updateAllowedTokens" sender_address : update_allowed_tokens_param contract option) with
  //       | None -> (failwith("no updateAllowedTokens entrypoint") : operation list)
  //       | Some update_allowed_tokens_entrypoint ->
  //         [Tezos.transaction param 0mutez update_allowed_tokens_entrypoint]
  //     in
  //     (prepare_multisig "updateAllowedTokens" param func store), store
  else
    match param.direction with
    | Remove_token ->
      let new_allowed_tokens = Big_map.update param.token_symbol (None : fun_token option) store.allowed_tokens in
      let new_available_pairs = Big_map.update (param.token_symbol, "USD") (None : string option) store.available_pairs in
      ([] : operation list), {store with allowed_tokens = new_allowed_tokens; available_pairs = new_available_pairs}
    | Add_token fa12_address ->
      let fun_token = 
        {
          fa12_address = fa12_address; 
          token_symbol = param.token_symbol
        } in
      if Big_map.mem param.token_symbol store.allowed_tokens then
        (failwith(error_TOKEN_INDEX_LISTED) : return)
      else if Big_map.mem (param.token_symbol, "USD") store.available_pairs then
        (failwith(error_PAIR_ALREADY_EXISTS) : return)
      else
        let new_allowed_tokens = Big_map.update param.token_symbol (Some fun_token) store.allowed_tokens in
        let pair = param.token_symbol ^ "-USD" in
        let new_available_pairs = Big_map.update (param.token_symbol, "USD") (Some pair) store.available_pairs in
        ([] : operation list), {store with allowed_tokens = new_allowed_tokens; available_pairs = new_available_pairs}