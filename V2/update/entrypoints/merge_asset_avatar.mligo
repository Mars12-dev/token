let merge_asset_avatar (param : merge_asset_avatar_param) (store: storage) : return =
   let balance_of_request_avatar = {
          token_id = param.avatar_id;
          owner = (Tezos.get_sender ());
        } in
        let user_balance_avatar =
        match (Tezos.call_view "get_balance_view" balance_of_request_avatar param.avatar_address : nat option) with
          | None -> (failwith "View returned an error" : nat)
          | Some user_balance -> user_balance in
        let balance_of_request_asset = {
          token_id = param.asset_id;
          owner = (Tezos.get_sender ());
        } in
         let user_balance_asset =
              match (Tezos.call_view "get_balance_view" balance_of_request_asset param.asset_address : nat option) with
                | None -> (failwith "View returned an error" : nat)
                | Some user_balance -> user_balance in
          if user_balance_avatar = 0n || user_balance_asset = 0n then
              (failwith error_NOT_AVATAR_OR_ASSET_TOKEN : return)
          else
              let burn_nft_param = {
              token_id = param.asset_id;
              from_ = (Tezos.get_sender ());
              amount_ = 1n;
              } in
              let ops = ([] : operation list) in 
              let ops = token_burn burn_nft_param param.asset_address :: ops in
             
              let nft_type_asset =
               match (Tezos.call_view "get_nft_type" ( ) param.asset_address : string option) with
                | None -> (failwith error_VIEW_RETURNED_AN_ERROR : string)
                | Some nft_type -> nft_type in 

              let metadata_updater (token_metadata : token_metadata): token_metadata =
                Map.update nft_type_asset (Some (Bytes.pack ("True"))) token_metadata
              in
              let update_param = {
                token_id = param.avatar_id;
                metadata_updater = metadata_updater;
              } in
              let  ops = update_metadata_with_function_call param.avatar_address update_param ::ops in
              (ops, store)