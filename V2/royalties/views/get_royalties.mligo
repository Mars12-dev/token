[@view] let get_royalties ((token_origin, token_id), store : (token_origin * token_id) * storage) : royalties_info =
    match Big_map.find_opt (token_origin, token_id) store.royalties with
    | None -> {
              issuer = (Tezos.get_self_address ());
              royalties = 0n;
            }
    | Some r -> r 