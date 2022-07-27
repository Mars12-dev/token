let mint (param, storage : nft_mint_param * nft_token_storage) : nft_token_storage =
  if storage.paused then 
    (failwith (error_FA2_CONTRACT_IS_PAUSED) : nft_token_storage) 
  else if Set.mem Tezos.sender storage.proxy = false then
    failwith error_ONLY_PROXY_CAN_CALL_THIS_ENTRYPOINT
  else
    (* MINT TOKEN *)
    let {
        token_id;
        token_metadata;
        amount_;
        owner;
      } = param in
    let _check_if_token_already_exists = match Big_map.find_opt (owner, token_id) storage.ledger with
      | Some _v -> failwith "token already exists"
      | None -> ()
    in
    let new_ledger = Big_map.update (owner, token_id) (Some amount_) storage.ledger in

    (* ADD METADATA URL *)
    let metadata_url = 
      Option.unopt (Map.find_opt "" token_metadata) in
    let url_length = Bytes.length metadata_url in
    let metadata_url = Bytes.sub 6n (abs (url_length - 6n)) metadata_url in
    let token_metadata = Map.update "" (Some metadata_url) token_metadata in
    let nft_metadata = {
      token_id = token_id ;
      token_info = token_metadata ;
    } in
    let new_token_metadata = Big_map.update
      token_id
      (Some nft_metadata)
      storage.token_metadata
    in
    { storage with ledger = new_ledger ; token_metadata = new_token_metadata }