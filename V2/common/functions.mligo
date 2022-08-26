#if !COMMON_HELPERS
#define COMMON_HELPERS

[@inline]
let is_a_nat (i : int) : nat option = is_nat i

[@inline]
let mutez_to_natural (a: tez) : nat =  a / 1mutez

[@inline]
let natural_to_mutez (a: nat): tez = a * 1mutez

[@inline]
let maybe (n : nat) : nat option =
  if n = 0n
  then (None : nat option)
  else Some n

let maybe_swap (n : nat) (swap : swap_info) : swap_info option =
  if n = 0n then
    (None : swap_info option)
  else (Some {swap with token_amount = n})

[@inline] let calculate_price (start_time, duration, starting_price, token_price : timestamp * int * nat * nat) : nat =
  match is_a_nat ((start_time + duration) - (Tezos.get_now ())) with
  | None -> token_price
  | Some t -> t * abs (starting_price - token_price)/ abs duration + token_price

[@inline] let assert_with_code (condition : bool) (code : nat) : unit =
  if (not condition) then failwith(code)
  else ()

[@inline]
let token_transfer (token_address: address) (txs : transfer list) : operation =
    let token_contract: token_contract_transfer contract =
    match (Tezos.get_entrypoint_opt "%transfer" token_address : token_contract_transfer contract option) with
    | None -> (failwith error_TOKEN_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT : token_contract_transfer contract)
    | Some contract -> contract in
    let transfers = List.map (fun (tx : transfer) -> tx.from_, List.map (fun  (dst : transfer_destination) -> (dst.to_, (dst.token_id, dst.amount))) tx.txs) txs in
    Tezos.transaction transfers 0mutez token_contract

[@inline]
let xtz_transfer (to_ : address) (amount_ : tez) : operation =
    let to_contract : unit contract =
        match (Tezos.get_contract_opt to_ : unit contract option) with
        | None -> (failwith error_INVALID_TO_ADDRESS : unit contract)
        | Some c -> c in
    Tezos.transaction () amount_ to_contract







[@inline]
let fa12_transfer (fa12_address : address) (from_ : address) (to_ : address) (value : nat) : operation =
  let fa12_contract : fa12_contract_transfer contract =
    match (Tezos.get_entrypoint_opt "%transfer" fa12_address : fa12_contract_transfer contract option) with
    | None -> (failwith(error_FA12_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT) : fa12_contract_transfer contract)
    | Some contract -> contract in
    let transfer = {address_from = from_; address_to = to_; value = value} in
    Tezos.transaction transfer 0mutez fa12_contract

[@inline]
let handout_op (ops : operation list) (value : nat) (symbol : token_symbol) (fa12_address : address) (from_ : address) (to_ : address) : operation list =
  if value > 0n then
      let ops =
        if symbol = "XTZ" then
          xtz_transfer to_ (natural_to_mutez value) :: ops
        else
          fa12_transfer fa12_address from_ to_ value :: ops in
      ops
  else
    ops


(* used to transfer management fees to treasury contract *)
let handout_fee_op (ops : operation list) (value : nat) (symbol : token_symbol) (fa12_address : address) (from_ : address) (to_ : address) : operation list =
  if value > 0n then
      match (Tezos.get_entrypoint_opt "%deposit" to_ : deposit_param contract option) with
      | None -> (failwith("wrong treasury contract") : operation list)
      | Some contr -> 
        let deposit = 
        {
          token = symbol;
          fa12_address = fa12_address;
          token_amount = value;
        } in
        let ops = 
          if symbol = "XTZ" then
            Tezos.transaction deposit (natural_to_mutez value) contr :: ops
          else
            let ops = fa12_transfer fa12_address from_ to_ value :: ops in
            let ops = Tezos.transaction deposit 0tez contr :: ops in
            ops in
        ops
  else
    ops









#endif
