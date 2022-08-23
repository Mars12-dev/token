let withdraw (param : withdraw_param) (store : storage) : return =
    if (Tezos.get_sender ()) = store.multisig then
        let ops = ([] : operation list) in
        let (ops, new_ledger) = 
            List.fold (fun ((ops, l), dst : (operation list * ledger) * destination) -> 
                let token = 
                    match Big_map.find_opt param.token l with
                    | None -> (failwith(error_NO_TOKEN_FOUND) : token_info)
                    | Some token -> token in
                let fa12_address = token.fa12_address in
                let new_amount =
                    match is_a_nat (token.token_amount - dst.token_amount) with
                    | None -> (failwith(error_NOT_ENOUGH_TOKEN_BALANCE) : nat)
                    | Some n -> n in
                let new_ledger = Big_map.update param.token (Some {token with token_amount = new_amount}) l in
                let ops = 
                    if param.token = "XTZ" then
                        xtz_transfer dst.to_ (natural_to_mutez dst.token_amount) :: ops
                    else
                        fa12_transfer fa12_address (Tezos.get_self_address ()) dst.to_ dst.token_amount :: ops in
                ops, new_ledger
                ) param.withdraw_destination (ops, store.ledger) in
            ops, {store with ledger = new_ledger}
    else
        let sender_address = (Tezos.get_self_address ()) in
        let func () = 
          match (Tezos.get_entrypoint_opt "%withdraw" sender_address : withdraw_param contract option) with
            | None -> (failwith("no withdraw entrypoint") : operation list)
            | Some withdraw_entrypoint ->
              [Tezos.transaction param 0mutez withdraw_entrypoint]
          in
        (prepare_multisig "withdraw" param func store), store 