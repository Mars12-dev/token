let update_contract_metadata (metadata_url : bytes) (store : storage) : operation list * storage =
  if store.paused then 
    (failwith (error_FA2_CONTRACT_IS_PAUSED) : return) 
  else if not Set.mem (Tezos.get_sender ()) store.proxy then
    failwith error_ONLY_PROXY_CAN_CALL_THIS_ENTRYPOINT
  else
    let metadata = Big_map.update "" (Some metadata_url) store.metadata in
    ([] : operation list), { store with metadata = metadata }