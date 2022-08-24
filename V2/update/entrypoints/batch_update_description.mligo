
let batch_update_description (param : batch_update_description_param) (store: storage) : return =
  if (not Set.mem (Tezos.get_sender ()) store.update_admins) then
    failwith error_UNAUTHORIZED_ADMIN_ADDRESS
  else 
  let update_single (acc, name_entry : operation list * update_description_param) : operation list =
    let metadata_updater (token_metadata : token_metadata): token_metadata =
      Map.update "description" (Some name_entry.new_description) token_metadata
      in
      let update_param = {
        token_id = name_entry.token_id;
        metadata_updater = metadata_updater;
      } in
      let update_metadata_op = update_metadata_with_function_call name_entry.nft_address update_param in
      update_metadata_op :: acc
  in
  let ops = List.fold update_single param ([] : operation list) in
  (ops, store)




