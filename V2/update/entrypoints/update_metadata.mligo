let update_metadata (param : update_param) (store: storage) : return =
  if (not Set.mem (Tezos.get_sender ()) store.update_admins) then
    failwith error_UNAUTHORIZED_ADMIN_ADDRESS
  else 
  let metadata_updater (token_metadata : token_metadata): token_metadata =
     let new_token_metadata = Map.update "formats" (Some param.metadata.formats) token_metadata in
     let new_token_metadata = Map.update "artifactUri" (Some param.metadata.artifactUri) new_token_metadata in
     let new_token_metadata = Map.update "displayUri" (Some param.metadata.displayUri) new_token_metadata in
     let new_token_metadata = Map.update "thumbnailUri" (Some param.metadata.thumbnailUri) new_token_metadata in
     Map.update "attributes" (Some (Bytes.pack (attributes_from_param (param.metadata.attributes)))) new_token_metadata
    in
    let new_update_param = {
      token_id = param.token_id;
      metadata_updater = metadata_updater;
    } in
    let ops = ([] : operation list) in
    let update_metadata_op = update_metadata_with_function_call param.nft_address new_update_param in
    (update_metadata_op :: ops, store)

