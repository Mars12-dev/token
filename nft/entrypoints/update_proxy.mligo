let update_proxy (action, storage : update_proxy_param * nft_token_storage) : operation list * nft_token_storage =
  let sender_address = Tezos.self_address in
  if Tezos.sender <> storage.multisig then
        let func () =
      match (Tezos.get_entrypoint_opt "%updateProxy" sender_address : update_proxy_param contract option) with
        | None -> (failwith("no updateProxy entrypoint") : operation list)
        | Some update_proxy_entrypoint ->
          [Tezos.transaction action 0mutez update_proxy_entrypoint]
      in
      (prepare_multisig "updateProxy" action func storage), storage
  else
  match action with
  | Add_proxy p -> 
  if Set.mem p storage.proxy then
    (failwith(error_ADDRESS_ALREADY_PROXY) : operation list * nft_token_storage)
  else
    ([] : operation list), { storage with proxy = Set.add p storage.proxy }
  | Remove_proxy p ->
  if Set.mem p storage.proxy = false then
    (failwith(error_ADDRESS_NOT_PROXY) : operation list * nft_token_storage)
  else
    ([] : operation list), { storage with proxy = Set.remove p storage.proxy }