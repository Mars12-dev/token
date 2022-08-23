let update_name (param : update_name_param) (store: storage) : return =
  if store.name_pause = true then
    (failwith "Update name is paused" : return)
  else
    if Tezos.amount <> store.name_price then
      (failwith error_INVALID_AMOUNT : return)
    else
      let _revealed = match Big_map.find_opt param.token_id store.token_id_to_metadata_id with
        | None -> (failwith "Token is not revealed" : nat)
        | Some r -> r
      in
      if Bytes.length param.new_name > 30n || Bytes.length param.new_name < 1n then
        (failwith "Name must be between 1 and 30 characters" : return)
      else
        let balance_of_request = {
          token_id = param.token_id;
          owner = Tezos.sender;
        } in
        match (Tezos.call_view "balance_of_view" balance_of_request store.nft_address : nat option) with
          | None -> (failwith "View returned an error" : return)
          | Some user_balance ->
            if user_balance <> 1n then
              (failwith "You do not own this token" : return)
            else
              let metadata_updater (token_metadata : token_metadata): token_metadata =
                Big_map.update "name" (Some param.new_name) token_metadata
              in
              let update_param = {
                token_id = param.token_id;
                metadata_updater = metadata_updater;
              } in
              let update_metadata_op = update_metadata_with_function_call store.nft_address update_param in
              ([update_metadata_op], store)

let batch_update_name (param : batch_update_name_param) (store: storage) : return =
  let _require_admin = require_admin store in

  let update_single (acc, name_entry : operation list * update_name_param) : operation list =
    let metadata_updater (token_metadata : token_metadata): token_metadata =
      Big_map.update "name" (Some name_entry.new_name) token_metadata
      in
      let update_param = {
        token_id = name_entry.token_id;
        metadata_updater = metadata_updater;
      } in
      let update_metadata_op = update_metadata_with_function_call store.nft_address update_param in
      update_metadata_op :: acc
  in
  let ops = List.fold update_single param ([] : operation list) in
  (ops, store)

let batch_update_description (param : batch_update_description_param) (store: storage) : return =
  let _require_admin = require_admin store in

  let update_single (acc, name_entry : operation list * update_description_param) : operation list =
    let metadata_updater (token_metadata : token_metadata): token_metadata =
      Big_map.update "description" (Some name_entry.new_description) token_metadata
      in
      let update_param = {
        token_id = name_entry.token_id;
        metadata_updater = metadata_updater;
      } in
      let update_metadata_op = update_metadata_with_function_call store.nft_address update_param in
      update_metadata_op :: acc
  in
  let ops = List.fold update_single param ([] : operation list) in
  (ops, store)

let set_name_list (param : set_name_list_param) (store: storage) : return =
  let _require_admin = require_admin store in
  let add_name (acc, el: name_list * (nat * bytes)) : name_list = Big_map.update el.0 (Some el.1) acc in
  let new_name_list = Map.fold add_name param store.name_list in
  ([] : operation list), { store with name_list = new_name_list }

let batch_update_name (param : batch_update_name_param) (store: storage) : return =
  let _require_admin = require_admin store in

  let update_single (acc, name_entry : operation list * update_name_param) : operation list =
    let metadata_updater (token_metadata : token_metadata): token_metadata =
      Big_map.update "name" (Some name_entry.new_name) token_metadata
      in
      let update_param = {
        token_id = name_entry.token_id;
        metadata_updater = metadata_updater;
      } in
      let update_metadata_op = update_metadata_with_function_call store.nft_address update_param in
      update_metadata_op :: acc
  in
  let ops = List.fold update_single param ([] : operation list) in
  (ops, store)

let set_ipfs_hashes (param : set_ipfs_hashes_param) (store: storage) : return =
  if Tezos.sender <> store.multisig then
    let sender_address = Tezos.self_address in
    let func () =
      match (Tezos.get_entrypoint_opt "%setIpfsHashes" sender_address : set_ipfs_hashes_param contract option) with
      | None -> (failwith("no setIpfsHashes entrypoint") : operation list)
      | Some set_ipfs_hashes_entrypoint -> [Tezos.transaction param 0mutez set_ipfs_hashes_entrypoint] in
    (prepare_multisig "setIpfsHashes" param func store), store
  else
    ([] : operation list), { store with ipfs_hashes = param }
