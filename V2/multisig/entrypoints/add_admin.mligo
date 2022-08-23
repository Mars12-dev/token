let add_admin (param : address) (store : storage) : return =
    if (Tezos.get_sender ()) <> (Tezos.get_self_address ()) then
        let sender_address = (Tezos.get_self_address ()) in
        let func () = 
            match (Tezos.get_entrypoint_opt "%addAdmin" sender_address : address contract option) with
            | None -> (failwith("no addAdmin entrypoint") : operation list)
            | Some add_admin_entrypoint -> [Tezos.transaction param 0mutez add_admin_entrypoint] in
        (prepare_multisig "addAdmin" param func), store 
    else 
        ([] : operation list), { store with admins = Set.add param store.admins }