let update_metadata_with_function (param : update_metadata_with_function_param) (storage : storage) : return =
  let { token_id = token_id ;
        metadata_updater = metadata_updater } = param in
  if (not Set.mem (Tezos.get_sender ()) storage.proxy) then
    failwith error_UNAUTHORIZED_CONTRACT_ADDRESS
  else
    match Big_map.find_opt token_id storage.token_metadata with
    | None -> (failwith error_TOKEN_METADATA_ITEM_DOES_NOT_EXIST : return)
    | Some token_metadata_entry ->
      let new_token_metadata_entry = {
        token_id = token_id;
        token_info = metadata_updater token_metadata_entry.token_info;
      } in
      let new_token_metadata = Big_map.update token_id (Some new_token_metadata_entry) storage.token_metadata in
      ([] : operation list), { storage with token_metadata = new_token_metadata }
