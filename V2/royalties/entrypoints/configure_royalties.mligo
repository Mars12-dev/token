let configure_royalties (param : config_royalties_param) (store : storage) : return =
    if store.paused then
        (failwith(error_CONTRACT_IS_PAUSED) : return)
    else if Set.mem (Tezos.get_sender ()) store.proxy = false then
        (failwith(error_ONLY_PROXY_CAN_CALL_THIS_ENTRYPOINT) : return)
    else if param.royalties > 2500n then
        (failwith error_ROYALTIES_TOO_HIGH : return)
    else
        let royalties_key = (param.token_origin, param.token_id) in
        match Big_map.find_opt royalties_key store.royalties with
            | None -> 
            let royalties_info = {
              issuer = (Tezos.get_source ());
              royalties = param.royalties;
            } in
            ([] : operation list), {store with royalties = Big_map.update royalties_key (Some royalties_info) store.royalties}
            | Some r -> 
            if r.issuer <> (Tezos.get_source ()) then
                (failwith error_ONLY_ISSUER_CAN_CALL_THIS_ENTRYPOINT : return)
            else 
                let new_royalties_info = { r with royalties = param.royalties} in
                ([] : operation list), {store with royalties = Big_map.update royalties_key (Some new_royalties_info) store.royalties}