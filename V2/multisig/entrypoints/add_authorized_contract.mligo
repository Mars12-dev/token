let add_authorized_contract (param : address) (store : storage) : return =
    if (Tezos.get_sender ()) <> (Tezos.get_self_address ()) then
        let sender_address = (Tezos.get_self_address ()) in
        let func () = 
            match (Tezos.get_entrypoint_opt "%addAuthorizedContract" sender_address : address contract option) with
            | None -> (failwith("no addAuthorizedContract entrypoint") : operation list)
            | Some add_authorized_contract_entrypoint -> [Tezos.transaction param 0mutez add_authorized_contract_entrypoint] in
        (prepare_multisig "addAuthorizedContract" param func), store 
    else
        let new_authorized_contract = Set.add param store.authorized_contracts in
        ([] : operation list), { store with authorized_contracts = new_authorized_contract }