
[@inline]
let token_burn (metadata : nft_burn_param) (store : storage) : operation =
    let token_mint_entrypoint: nft_burn_param contract =
      match (Tezos.get_entrypoint_opt "%burn" store.nft_address : nft_burn_param contract option) with
      | None -> (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_MINT_ENTRYPOINT : nft_burn_param contract)
      | Some contract -> contract in
    Tezos.transaction metadata 0mutez token_burn_entrypoint

[@inline]
let update_metadata_with_function_call (token_address : address) (param : update_metadata_with_function_param) : operation =
  match (Tezos.get_entrypoint_opt "%updateMetadataWithFunction" token_address : update_metadata_with_function_param contract option) with
  | None -> (failwith error_NFT_CONTRACT_MUST_HAVE_AN_UPDATE_METADATA_WITH_FUNCTION_ENTRYPOINT : operation)
  | Some update_metadata_with_function_entrypoint -> Tezos.transaction param 0mutez update_metadata_with_function_entrypoint
