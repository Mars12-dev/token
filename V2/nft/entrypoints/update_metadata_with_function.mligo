let update_metadata_with_function (param : update_metadata_with_function_param) (storage : nft_token_storage) : nft_token_storage =
  let { token_id = token_id ;
        metadata_updater = metadata_updater } = param in
  if (not Set.mem Tezos.sender storage.contracts) then
    failwith error_UNAUTHORIZED_CONTRACT_ADDRESS
  else
    match Big_map.find_opt token_id storage.token_metadata with
    | None -> (failwith error_TOKEN_METADATA_ITEM_DOES_NOT_EXIST : nft_token_storage)
    | Some token_metadata_entry ->
      let new_token_metadata_entry = {
        token_id = token_id;
        token_info = metadata_updater token_metadata_entry.token_info;
      } in
      let new_token_metadata = Big_map.update token_id (Some new_token_metadata_entry) storage.token_metadata in
      { storage with token_metadata = new_token_metadata }
