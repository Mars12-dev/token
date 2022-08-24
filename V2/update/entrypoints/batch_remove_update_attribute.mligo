
let batch_remove_update_attribute (param : batch_remove_attribute_param) (store: storage) : return =
  if (Tezos.get_sender ()) <> store.multisig then
    let sender_address = (Tezos.get_self_address ()) in
    let func () =
      match (Tezos.get_entrypoint_opt "%batchRemoveAttribute" sender_address : batch_remove_attribute_param contract option) with
      | None -> (failwith error_NO_BATCH_REMOVE_ATTRIBUTE_ENTRYPOINT: operation list)
      | Some batch_remove_attribute_entrypoint -> [Tezos.transaction param 0mutez batch_remove_attribute_entrypoint] in
    (prepare_multisig "batchRemoveAttribute" param func store), store
  else
    let remove_single (acc, attribute_item : operation list * remove_attribute_param) : operation list =
      let metadata_updater (token_metadata : token_metadata): token_metadata =
        let attributes =
          match Map.find_opt "attributes" token_metadata with
          | Some attributes -> attributes
          | None -> (failwith "Attributes does not exist" : bytes)
        in
        let unpacked_attributes =
          match (Bytes.unpack attributes : (string, (string option * string)) map option) with
          | Some unpacked_attributes -> unpacked_attributes
          | None -> (failwith error_COULD_NOT_UNPACK_ATTRIBUTES : (string, (string option * string)) map)
        in
        let new_attributes = Map.remove attribute_item.key unpacked_attributes
        in
        Map.update "attributes" (Some (Bytes.pack new_attributes)) token_metadata
      in
      let update_params = {
        token_id = attribute_item.token_id;
        metadata_updater = metadata_updater;
      } in
      let update_metadata_op = update_metadata_with_function_call attribute_item.nft_address update_params in
      update_metadata_op :: acc
    in
    let ops = List.fold remove_single param ([] : operation list) in
    (ops, store)


