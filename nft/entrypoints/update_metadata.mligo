let update_metadata (param : nft_update_metadata_param) (store : nft_token_storage) : operation list * nft_token_storage =
  if store.paused then 
    (failwith (error_FA2_CONTRACT_IS_PAUSED) : return) 
  else if not Set.mem Tezos.sender store.proxy then
    failwith error_ONLY_PROXY_CAN_CALL_THIS_ENTRYPOINT
  else
    let { token_id; metadata } = param in
    let nft_metadata = 
      {
        token_id = token_id;
        metadata = metadata;
      } in
    let new_token_metadata =
      Big_map.update token_id (Some nft_metadata) store.token_metadata in
    ([] : operation list), { store with token_metadata = new_token_metadata }