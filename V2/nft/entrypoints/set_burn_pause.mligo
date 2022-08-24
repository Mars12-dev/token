let set_burn_pause (param : bool) (store : storage) : operation list * storage =
  let sender_address = (Tezos.get_self_address ()) in
  if (Tezos.get_sender ()) <> store.multisig then
        let func () =
      match (Tezos.get_entrypoint_opt "%setBurnPause" sender_address : bool contract option) with
        | None -> (failwith(error_NO_SET_BURN_PAUSE_ENTRYPOINT) : operation list)
        | Some set_pause_entrypoint ->
          [Tezos.transaction param 0mutez set_pause_entrypoint]
      in
      (prepare_multisig "setPause" param func store), store
    else
    ([] : operation list), {store with burn_paused = param}