[@view] let get_balance_view ((owner, token_id), store : (address * token_id) * nft_storage) : nat =
    let balance = Big_map.find_opt (owner, token_id) store.ledger in
    match balance with 
    | None -> 0n
    | Some n -> n
      