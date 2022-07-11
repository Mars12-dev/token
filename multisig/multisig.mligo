#include "multisig_errors.mligo"
#include "multisig_interface.mligo"
#include "multisig_functions.mligo"

let call (param : call_param) (store : storage) : return =
    let admins = store.admins in
    if (not Set.mem Tezos.source admins) then
        (failwith(error_NOT_AN_ADMIN) : return)
    else if (not Set.mem Tezos.sender store.authorized_contracts) && Tezos.sender <> Tezos.self_address then
        (failwith(error_ONLY_LISTED_CONTRACTS_CAN_CALL) : return)
    else if param.entrypoint_signature.source_contract <> Tezos.sender then 
        (failwith(error_SIGNATURE_SOURCE_NOT_AUTHORIZED) : return)
    else
        let (new_set, new_deadline) =
            match Big_map.find_opt param.entrypoint_signature store.n_calls with
            | None -> Set.literal [Tezos.source], Tezos.now + store.duration 
            | Some (existing_set, deadline) -> 
            if Tezos.now >= deadline || Set.size existing_set >= store.threshold then
                Set.literal [Tezos.source], Tezos.now + store.duration
            else if Set.mem Tezos.source existing_set then
                (failwith(error_ALREADY_VOTED) : address set * timestamp)
            else
                Set.add Tezos.source existing_set, deadline in
        if Set.size new_set >= store.threshold then
            let ops = param.callback unit in
            let new_store = { store with n_calls = Big_map.update param.entrypoint_signature (None : (address set * timestamp) option) store.n_calls } in
            ops, new_store
        else
            let new_n_calls = Big_map.update param.entrypoint_signature (Some (new_set, new_deadline)) store.n_calls in
            ([] : operation list), { store with n_calls = new_n_calls }


let add_admin (param : address) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        let sender_address = Tezos.self_address in
        let func () = 
            match (Tezos.get_entrypoint_opt "%addAdmin" sender_address : address contract option) with
            | None -> (failwith("no addAdmin entrypoint") : operation list)
            | Some add_admin_entrypoint -> [Tezos.transaction param 0mutez add_admin_entrypoint] in
        (prepare_multisig "addAdmin" param func), store 
    else 
        ([] : operation list), { store with admins = Set.add param store.admins }

let remove_admin (param : address) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        let sender_address = Tezos.self_address in
        let func () = 
            match (Tezos.get_entrypoint_opt "%removeAdmin" sender_address : address contract option) with
            | None -> (failwith("no removeAdmin entrypoint") : operation list)
            | Some remove_admin_entrypoint -> [Tezos.transaction param 0mutez remove_admin_entrypoint] in
        (prepare_multisig "removeAdmin" param func), store 
    else if Set.size store.admins = 1n then
        (failwith(error_ADMIN_SET_CANNOT_BE_EMPTY) : return)
    else if Set.size store.admins = store.threshold then
        (failwith(error_ADMIN_SET_MUST_BE_LARGER_THAN_THRESHOLD) : return)
    else
        ([] : operation list), { store with admins = Set.remove param store.admins }

let set_threshold (param : nat) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        let sender_address = Tezos.self_address in
        let func () = 
            match (Tezos.get_entrypoint_opt "%setThreshold" sender_address : nat contract option) with
            | None -> (failwith("no setThreshold entrypoint") : operation list)
            | Some set_threshold_entrypoint -> [Tezos.transaction param 0mutez set_threshold_entrypoint] in
        (prepare_multisig "setThreshold" param func), store 
    else if param = 0n then
        (failwith(error_THRESHOLD_CAN_NOT_BE_ZERO) : return)
    else if param > Set.size store.admins then
        (failwith(error_THRESHOLD_TOO_HIGH) : return)
    else
        ([] : operation list), { store with threshold = param }

let set_duration (param : nat) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        let sender_address = Tezos.self_address in
        let func () = 
            match (Tezos.get_entrypoint_opt "%setDuration" sender_address : nat contract option) with
            | None -> (failwith("no setDuration entrypoint") : operation list)
            | Some set_duration_entrypoint -> [Tezos.transaction param 0mutez set_duration_entrypoint] in
      (prepare_multisig "setDuration" param func), store 
    else if param = 0n then
        (failwith(error_DURATION_CANNOT_BE_ZERO) : return)
    else
        ([] : operation list), { store with duration = int param }

let add_authorized_contract (param : address) (store : storage) : return =
    if Tezos.sender <> Tezos.self_address then
        let sender_address = Tezos.self_address in
        let func () = 
            match (Tezos.get_entrypoint_opt "%addAuthorizedContract" sender_address : address contract option) with
            | None -> (failwith("no addAuthorizedContract entrypoint") : operation list)
            | Some add_authorized_contract_entrypoint -> [Tezos.transaction param 0mutez add_authorized_contract_entrypoint] in
        (prepare_multisig "addAuthorizedContract" param func), store 
    else
        let new_authorized_contract = Set.add param store.authorized_contracts in
        ([] : operation list), { store with authorized_contracts = new_authorized_contract }


let main (action, store : parameter * storage) : return =
match action with
| CallMultisig p -> call p store
| AddAdmin p -> add_admin p store
| RemoveAdmin p -> remove_admin p store
| SetThreshold p -> set_threshold p store
| SetDuration p -> set_duration p store
| AddAuthorizedContract p -> add_authorized_contract p store

