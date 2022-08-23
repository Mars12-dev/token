let update_name (param : update_name_param) (store: storage) : return =
    if store.name_pause = true then
      (failwith "Update name is paused" : return)
    else if Bytes.length param.new_name > 30n || Bytes.length param.new_name < 1n then
        (failwith "Name must be between 1 and 30 characters" : return)
    else
        let balance_of_request = {
          token_id = param.token_id;
          owner = Tezos.sender;
        } in
        match (Tezos.call_view "get_balance_view" balance_of_request param.nft_address : nat option) with
          | None -> (failwith "View returned an error" : return)
          | Some user_balance ->
            if user_balance = 0n then
              (failwith "You do not own this token" : return)
            else
              let metadata_updater (token_metadata : token_metadata): token_metadata =
                Big_map.update "name" (Some param.new_name) token_metadata
              in
              let update_param = {
                token_id = param.token_id;
                metadata_updater = metadata_updater;
              } in
              let update_metadata_op = update_metadata_with_function_call param.nft_address update_param in
              ([update_metadata_op], store)