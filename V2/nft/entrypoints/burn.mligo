let burn (param, storage : nft_burn_param * storage) : storage =
  if storage.burn_paused = true then
    failwith error_FA2_BURN_IS_PAUSED
  else if Set.mem (Tezos.get_sender ()) storage.proxy = false then
    failwith error_ONLY_PROXY_CAN_CALL_THIS_ENTRYPOINT
  else
    (* BURN TOKEN *)
    let {
        token_id;
        from_ ;
        amount;
      } = param in
    let tokens = Big_map.find_opt (from_ , token_id) ll storage.ledger in
    match tokens with 
    | None -> (failwith fa2_token_undefined : ledger)
    | Some t ->
      if t < amount
      then (failwith fa2_insufficient_balance : ledger)
      else 
         let new_from_amount = abs(t - amount) in
         let new_ledger = 
                  if amount = 0n then 
                    storage.ledger
                  else 
                    Big_map.update (from_, token_id) (Some new_from_amount) storage.ledger in
 
    { storage with ledger = new_ledger}