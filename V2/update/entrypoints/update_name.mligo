let update_name (param : update_name_param) (store: storage) : return =
    if Bytes.length param.new_name > 30n || Bytes.length param.new_name < 1n then
        (failwith error_NAME_MUST_BE_BETWEEN_1_AND_30_CHARACTERS : return)
    else
        let balance_of_request = {
          token_id = param.token_id;
          owner = Tezos.sender;
        } in
        match (Tezos.call_view "get_balance_view" balance_of_request param.nft_address : nat option) with
          | None -> (failwith error_VIEW_RETURNED_AN_ERROR : return)
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