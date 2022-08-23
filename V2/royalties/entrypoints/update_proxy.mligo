let update_proxy (param : update_proxy_param) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.multisig then
    let sender_address = (Tezos.get_self_address ()) in
    let func () =
      match (Tezos.get_entrypoint_opt "%updateProxy" sender_address : update_proxy_param contract option) with
      | None -> (failwith("no updateProxy entrypoint") : operation list)
      | Some update_proxy_entrypoint -> [Tezos.transaction param 0mutez update_proxy_entrypoint] in
      (prepare_multisig "updateProxy" param func store), store
  else
    match param with
    | Add_proxy p -> 
    if Set.mem p store.proxy then
      (failwith(error_ADDRESS_ALREADY_PROXY) : return)
    else
      ([] : operation list), { store with proxy = Set.add p store.proxy }
    | Remove_proxy p ->
    if Set.mem p store.proxy = false then
      (failwith(error_ADDRESS_NOT_PROXY) : return)
    else
      ([] : operation list), { store with proxy = Set.remove p store.proxy }