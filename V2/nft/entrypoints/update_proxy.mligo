let update_proxy (action, storage : update_proxy_param * storage) : operation list * storage =
  if (Tezos.get_sender ()) <> storage.manager then
    (failwith(error_ONLY_MANAGER_CONTRACT_CAN_CALL) : operation list * storage)
  else
    match action with
    | Add_proxy p -> 
    if Set.mem p storage.proxy then
      (failwith(error_ADDRESS_ALREADY_PROXY) : operation list * storage)
    else
      ([] : operation list), { storage with proxy = Set.add p storage.proxy }
    | Remove_proxy p ->
    if Set.mem p storage.proxy = false then
      (failwith(error_ADDRESS_NOT_PROXY) : operation list * storage)
    else
      ([] : operation list), { storage with proxy = Set.remove p storage.proxy }