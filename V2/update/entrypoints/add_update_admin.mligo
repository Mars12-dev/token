let add_update_admin (param: add_update_admin_param) (store: storage) : return =
    if (Tezos.get_sender ()) <> store.multisig then
        let sender_address = Tezos.get_self_address () in
        let func () =
          match (Tezos.get_entrypoint_opt "%addUpdateAdmin" sender_address : address contract option) with
          | None -> (failwith error_NO_ADDUPDATE_ADMIN_ENTRYPOINT : operation list)
          | Some add_update_admin_entrypoint -> [Tezos.transaction param 0mutez add_update_admin_entrypoint] in
      (prepare_multisig "addUpdateAdmin" param func store), store
    else
    ([] : operation list), {store with update_admins = Set.add param store.update_admins}
