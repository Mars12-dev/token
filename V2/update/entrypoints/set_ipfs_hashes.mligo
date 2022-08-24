let set_ipfs_hashes (param : set_ipfs_hashes_param) (store: storage) : return =
  if (Tezos.get_sender ()) <> store.multisig then
    let sender_address = (Tezos.get_self_address ()) in
    let func () =
      match (Tezos.get_entrypoint_opt "%setIpfsHashes" sender_address : set_ipfs_hashes_param contract option) with
      | None -> (failwith error_NO_SET_IPFS_HASHES_ENTRYPOINT : operation list)
      | Some set_ipfs_hashes_entrypoint -> [Tezos.transaction param 0mutez set_ipfs_hashes_entrypoint] in
    (prepare_multisig "setIpfsHashes" param func store), store
  else
    let new_ipfs_hashes = Big_map.update (param.nft_address) (Some param.ipfs_hashes) store.ipfs_hashes in
    ([] : operation list), { store with ipfs_hashes = new_ipfs_hashes }