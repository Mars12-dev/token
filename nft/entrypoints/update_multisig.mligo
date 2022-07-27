let update_multisig_address (param : update_multisig_address_param) (store : nft_token_storage) : operation list * nft_token_storage =
    if Tezos.sender = store.multisig then
        ([] : operation list), { store with multisig = param }
    else
        let sender_address = Tezos.self_address in
        let func () = 
            match (Tezos.get_entrypoint_opt "%updateMultisig" sender_address : update_multisig_address_param contract option) with
            | None -> (failwith("no updateMultisig entrypoint") : operation list)
            | Some update_multisig_entrypoint ->
                [Tezos.transaction param 0mutez update_multisig_entrypoint]
            in
        (prepare_multisig "update_multisig" param func store), store