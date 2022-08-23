(**
Update leger balances according to the specified transfers. Fails if any of the
permissions or constraints are violated.
@param txs transfers to be applied to the ledger
@param validate_op function that validates of the tokens from the particular owner can be transferred.
 *)
let transfer (txs, validate_op, ops_storage, ledger
    : (transfer list) * operator_validator * operator_storage * ledger) : ledger =
    (* process individual transfer *)
    let make_transfer = (fun (l, tx : ledger * transfer) ->
      List.fold
        (fun (ll, dst : ledger * transfer_destination) ->
            let tokens = Big_map.find_opt (tx.from_, dst.token_id) ll in
            match tokens with
            | None -> (failwith fa2_token_undefined : ledger)
            | Some t ->
              if t < dst.amount
              then (failwith fa2_insufficient_balance : ledger)
              else
                let new_to_amount = match Big_map.find_opt (dst.to_, dst.token_id) ll with
                | Some a -> a + dst.amount
                | None -> dst.amount in
                let new_from_amount = abs (t - dst.amount) in
                let _u = validate_op (tx.from_, (Tezos.get_sender ()), dst.token_id, ops_storage) in
                let new_ledger = Big_map.update (dst.to_, dst.token_id) (Some new_to_amount) ll in
                let new_ledger = 
                  if dst.amount = 0n then 
                    ll
                  else 
                    Big_map.update (tx.from_, dst.token_id) (Some new_from_amount) new_ledger in
                new_ledger
        ) tx.txs l
    )
    in

    List.fold make_transfer txs ledger