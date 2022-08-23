let configure_collection_royalties (param : configure_collection_royalties_param) (store : storage) : return =
  if store.paused then
        (failwith(error_CONTRACT_IS_PAUSED) : return)
    else if (not Set.mem (Tezos.get_sender ()) store.proxy) then
        (failwith(error_ONLY_PROXY_CAN_CALL_THIS_ENTRYPOINT) : return)
    else if param.royalties > 2500n then
        (failwith error_ROYALTIES_TOO_HIGH : return)
    else 
      let assign_royalties =
      {
        token_origin = param.nft_address;
        current_id = param.first_id;
        last_id = param.last_id;
        issuer = (Tezos.get_source ());
        royalties = param.royalties;
        royalties_map = store.royalties;
      } in
      let new_royalties =  assign assign_royalties in
      ([] : operation list), { store with royalties = new_royalties }