(**
Retrieve the balances for the specified tokens and owners
@return callback operation
*)
let get_balance (p, (ledger, metadata) : balance_of_param * (ledger * token_metadata_storage)) : operation =
  let to_balance = fun (r : balance_of_request) ->
    let _token = match Big_map.find_opt r.token_id metadata with
      | None -> (failwith fa2_token_undefined : unit)
      | Some _token -> () in
    let owner = Big_map.find_opt (r.owner, r.token_id) ledger in
    match owner with 
    | None -> {request = r; balance = 0n}
    | Some o ->
      let bal = o in
      { request = r; balance = bal; }
  in
  let responses = List.map to_balance p.requests in
  Tezos.transaction responses 0mutez p.callback