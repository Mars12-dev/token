let set_duration (param : nat) (store : storage) : return =
    if (Tezos.get_sender ()) <> (Tezos.get_self_address ()) then
        let sender_address = (Tezos.get_self_address ()) in
        let func () = 
            match (Tezos.get_entrypoint_opt "%setDuration" sender_address : nat contract option) with
            | None -> (failwith("no setDuration entrypoint") : operation list)
            | Some set_duration_entrypoint -> [Tezos.transaction param 0mutez set_duration_entrypoint] in
      (prepare_multisig "setDuration" param func), store 
    else if param = 0n then
        (failwith(error_DURATION_CANNOT_BE_ZERO) : return)
    else
        ([] : operation list), { store with duration = int param }