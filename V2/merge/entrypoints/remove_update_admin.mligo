let remove_update_admin (param: remove_update_admin_param) (store: storage) : return =
    if (Tezos.get_sender ()) <> store.multisig then
        let func () =
          match (Tezos.get_entrypoint_opt "%removeUpdateAdmin" sender_address : address contract option) with
          | None -> (failwith("no removeUpdateAdmin entrypoint") : operation list)
          | Some remove_update_admin_entrypoint -> [Tezos.transaction param 0mutez remove_update_admin_entrypoint] in
      (prepare_multisig "removeUpdateAdmin" param func store), store
    else
    ([] : operation list), {store with updates_admins = Set.remove param store.update_admins}