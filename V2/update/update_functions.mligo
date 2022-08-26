
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
  let sender_address = (Tezos.get_self_address ()) in
  if (Tezos.get_sender ()) <> store.multisig then
        let func () =
          match (Tezos.get_entrypoint_opt "%setPause" sender_address : bool contract option) with
          | None -> (failwith("no setPause entrypoint") : operation list)
          | Some set_pause_entrypoint -> [Tezos.transaction param 0mutez set_pause_entrypoint] in
      (prepare_multisig "setPause" param func store), store
    else
    ([] : operation list), {store with paused = param}

let update_multisig_address (param : address) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.multisig then
    let sender_address = (Tezos.get_self_address ()) in
    let func () =
      match (Tezos.get_entrypoint_opt "%updateMultisigAddress" sender_address : address contract option) with
        | None -> (failwith("no updateMultisigAddress entrypoint") : operation list)
        | Some update_mutisig_entrypoint ->
          [Tezos.transaction param 0mutez update_mutisig_entrypoint]
      in
      (prepare_multisig "updateMultisigAddress" param func store), store
  else
    ([] : operation list), { store with multisig = param }

[@inline]
let token_burn (metadata : nft_burn_param) (nft_address : address) : operation =
    let token_burn_entrypoint: nft_burn_param contract =
      match (Tezos.get_entrypoint_opt "%burn" nft_address : nft_burn_param contract option) with
      | None -> (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_BURN_ENTRYPOINT : nft_burn_param contract)
      | Some contract -> contract in
    Tezos.transaction metadata 0mutez token_burn_entrypoint

[@inline]
let update_metadata_with_function_call (token_address : address) (param : update_metadata_with_function_param) : operation =
  match (Tezos.get_entrypoint_opt "%updateMetadataWithFunction" token_address : update_metadata_with_function_param contract option) with
  | None -> (failwith error_NFT_CONTRACT_MUST_HAVE_AN_UPDATE_METADATA_WITH_FUNCTION_ENTRYPOINT : operation)
  | Some update_metadata_with_function_entrypoint -> Tezos.transaction param 0mutez update_metadata_with_function_entrypoint

[@inline]
let attributes_from_param (param : attributes_from_param_param) : (string, (string option * string)) map =
  Map.literal [
    ("campaign", ((None : string option), param.a));
    ("Chest", ((None : string option), param.b));
    ("Eyebrows", ((None : string option), param.c));
    ("Eyes", ((None : string option), param.d));
    ("Mouth", ((None : string option), param.e));
    ("Legs", ((None : string option), param.f));
    ("Feet", ((None : string option), param.g));
    ("level", ((Some "Number"), param.h));
  ]