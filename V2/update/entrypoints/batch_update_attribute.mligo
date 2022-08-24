
let batch_update_attribute (param : batch_update_attribute_param) (store: storage) : return =
  if Tezos.sender <> store.multisig then
    let sender_address = Tezos.self_address in
    let func () =
      match (Tezos.get_entrypoint_opt "%batchUpdateAttribute" sender_address : batch_update_attribute_param contract option) with
      | None -> (failwith error_NO_BATCH_UPDATE_ATTRIBUTE_ENTRYPOINT : operation list)
      | Some batch_update_attribute_entrypoint -> [Tezos.transaction param 0mutez batch_update_attribute_entrypoint] in
    (prepare_multisig "batchUpdateAttribute" param func store), store
  else
    let update_single (acc, attribute_item : operation list * update_attribute_param) : operation list =
      let metadata_updater (token_metadata : token_metadata): token_metadata =

        let attributes =
          match Big_map.find_opt "attributes" token_metadata with
          | Some attributes -> attributes
          | None -> (failwith error_ATTRIBUTES_DOES_NOT_EXIST : bytes)
        in
        let unpacked_attributes =
          match (Bytes.unpack attributes : (string, (string option * string)) map option) with
          | Some unpacked_attributes -> unpacked_attributes
          | None -> (failwith error_COULD_NOT_UNPACK_ATTRIBUTES : (string, (string option * string)) map)
        in
        let new_attributes =
          if Bytes.length attribute_item.type_ > 0n then
            Map.update attribute_item.key (Some ((Some attribute_item.type_), attribute_item.value)) unpacked_attributes
          else
            Map.update attribute_item.key (Some ((None : string option), attribute_item.value)) unpacked_attributes
        in
        Big_map.update "attributes" (Some (Bytes.pack new_attributes)) token_metadata
      in

      let update_param = {
        token_id = attribute_item.token_id;
        metadata_updater = metadata_updater;
      } in
      let update_metadata_op = update_metadata_with_function_call param.nft_address update_param in
      update_metadata_op :: acc
    in
    let ops = List.fold update_single param ([] : operation list) in
    (ops, store)