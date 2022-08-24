let merge_asset_avatar (param : merge_asset_avatar_param) (store: storage) (operations : operation list) : return =
   let balance_of_request_avatar = {
          token_id = param.avatar_id;
          owner = Tezos.sender;
        } in
        let user_balance_avatar =
        match (Tezos.call_view "get_balance_view" balance_of_request_avatar param.avatar_address : nat option) with
          | None -> (failwith "View returned an error" : return)
          | Some user_balance -> user_balance in
         let user_balance_asset =
              match (Tezos.call_view "get_balance_view" balance_of_request param.asset_address : nat option) with
                | None -> (failwith "View returned an error" : return)
                | Some user_balance -> user_balance in
          if user_balance_avatar = 0n || user_balance_asset = 0n then
              (failwith error_NOT_AVATAR_OR_ASSET_TOKEN : return)
          else
              let burn_nft_param = {
              token_id = param.asset_id;
              from_ = Tezos.sender;
              amount = 1n;
              } in
              let ops = ([]:: operation list) in 
              let ops = token_burn burn_nft_param :: ops in
             
              let nft_type_asset =
               match (Tezos.call_view "get_nft_type" ( ) param.asset_address : string option) with
                | None -> (failwith error_VIEW_RETURNED_AN_ERROR : return)
                | Some nft_type -> nft_type in 

              let metadata_updater (token_metadata : token_metadata): token_metadata =
                Big_map.update nft_type_asset (Some Bytes.pack("True")) token_metadata
              in
              let update_param = {
                token_id = param.avatar_id;
                metadata_updater = metadata_updater;
              } in
              let  ops = update_metadata_with_function_call param.avatar_address update_param ::ops in
              (ops, store)
             

               





                     






    token_burn  nft_burn_param, nft_address in 
    get_nft_type

    
type merge_asset_to_avatar =
[@layout:comb]
{
  asset_address : address;
  avatar_address : address;
  assset_id: nat;
  avatar_id : nat;
}