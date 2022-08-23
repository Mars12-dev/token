let set_pause (param : bool) (store : storage) : return =
  if (Tezos.get_sender ()) <> store.multisig then
    let sender_address = (Tezos.get_self_address ()) in
    let func () =
      match (Tezos.get_entrypoint_opt "%setPause" sender_address : bool contract option) with
      | None -> (failwith("no setPause entrypoint") : operation list)
      | Some set_pause_entrypoint -> [Tezos.transaction param 0mutez set_pause_entrypoint] in
      (prepare_multisig "setPause" param func store), store
    else
        ([] : operation list), { store with paused = param }