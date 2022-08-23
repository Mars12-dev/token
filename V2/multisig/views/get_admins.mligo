[@view]let get_admins (_, store : unit * storage) : address set =
    if (not Set.mem (Tezos.get_sender ()) store.authorized_contracts) then
        (failwith(error_ONLY_LISTED_CONTRACTS_CAN_CALL) : address set)
    else
        store.admins