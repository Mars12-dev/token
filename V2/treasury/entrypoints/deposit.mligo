let deposit (param : deposit_param) (store : storage) : return =
    let token = param.token in
    if token = "XTZ" && param.token_amount <> mutez_to_natural (Tezos.get_amount ()) then
        (failwith(error_AMOUNT_SENT_NOT_EQUAL_TO_XTZ_AMOUNT) : return)
    else
        let new_token_info = match Big_map.find_opt token store.ledger with
        | None -> 
        {
            token_amount = param.token_amount;
            fa12_address = param.fa12_address;
        }
        | Some token_info -> 
        if token_info.fa12_address <> param.fa12_address then
            (failwith(error_WRONG_TOKEN_ADDRESS) : token_info)
        else
            { 
                token_info with 
                token_amount = token_info.token_amount + param.token_amount 
            } in
        let new_ledger = Big_map.update token (Some new_token_info) store.ledger in
        ([] : operation list), { store with ledger = new_ledger }