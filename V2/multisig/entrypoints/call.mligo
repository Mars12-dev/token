let call (param : call_param) (store : storage) : return =
    let admins = store.admins in
    if (not Set.mem (Tezos.get_source ()) admins) then
        (failwith(error_NOT_AN_ADMIN) : return)
    else if (not Set.mem (Tezos.get_sender ()) store.authorized_contracts) && (Tezos.get_sender ()) <> (Tezos.get_self_address ()) then
        (failwith(error_ONLY_LISTED_CONTRACTS_CAN_CALL) : return)
    else if param.entrypoint_signature.source_contract <> (Tezos.get_sender ()) then 
        (failwith(error_SIGNATURE_SOURCE_NOT_AUTHORIZED) : return)
    else
        let (new_set, new_deadline) =
            match Big_map.find_opt param.entrypoint_signature store.n_calls with
            | None -> Set.literal [(Tezos.get_source ())], (Tezos.get_now ()) + store.duration 
            | Some (existing_set, deadline) -> 
            if (Tezos.get_now ()) >= deadline || Set.size existing_set >= store.threshold then
                Set.literal [(Tezos.get_source ())], (Tezos.get_now ()) + store.duration
            else if Set.mem (Tezos.get_source ()) existing_set then
                (failwith(error_ALREADY_VOTED) : address set * timestamp)
            else
                Set.add (Tezos.get_source ()) existing_set, deadline in
        if Set.size new_set >= store.threshold then
            let ops = param.callback unit in
            let new_store = { store with n_calls = Big_map.update param.entrypoint_signature (None : (address set * timestamp) option) store.n_calls } in
            ops, new_store
        else
            let new_n_calls = Big_map.update param.entrypoint_signature (Some (new_set, new_deadline)) store.n_calls in
            ([] : operation list), { store with n_calls = new_n_calls }