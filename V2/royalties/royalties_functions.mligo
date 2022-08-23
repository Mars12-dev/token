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


let rec assign (param : assign_param) : royalties_map =
  if param.current_id = param.last_id then
    param.royalties_map
  else
    let new_entry = 
      {
        issuer = param.issuer;
        royalties = param.royalties;
      } in
    let royalties_map =
      match Big_map.find_opt (param.token_origin, param.current_id) param.royalties_map with
      | Some _ -> (failwith("token already has royalties") : royalties_map)
      | None ->
        Big_map.update (param.token_origin, param.current_id) (Some new_entry) param.royalties_map in
    let current_id = param.current_id + 1n in
    assign {param with current_id = current_id; royalties_map = royalties_map} 