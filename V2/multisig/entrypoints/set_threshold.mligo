let set_threshold (param : nat) (store : storage) : return =
    if (Tezos.get_sender ()) <> (Tezos.get_self_address ()) then
        let sender_address = (Tezos.get_self_address ()) in
        let func () = 
            match (Tezos.get_entrypoint_opt "%setThreshold" sender_address : nat contract option) with
            | None -> (failwith("no setThreshold entrypoint") : operation list)
            | Some set_threshold_entrypoint -> [Tezos.transaction param 0mutez set_threshold_entrypoint] in
        (prepare_multisig "setThreshold" param func), store 
    else if param = 0n then
        (failwith(error_THRESHOLD_CAN_NOT_BE_ZERO) : return)
    else if param > Set.size store.admins then
        (failwith(error_THRESHOLD_TOO_HIGH) : return)
    else
        ([] : operation list), { store with threshold = param }