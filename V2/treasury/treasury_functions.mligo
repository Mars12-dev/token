[@inline] 
let is_a_nat (i : int) : nat option = is_nat i 

[@inline] 
let mutez_to_natural (a: tez) : nat =  a / 1mutez 

[@inline] 
let natural_to_mutez (a: nat): tez = a * 1mutez 

[@inline] 
let xtz_transfer (to_ : address) (amount_ : tez) : operation = 
    let to_contract : unit contract = 
        match (Tezos.get_contract_opt to_ : unit contract option) with 
        | None -> (failwith error_INVALID_TO_ADDRESS : unit contract) 
        | Some c -> c in 
    Tezos.transaction () amount_ to_contract 

type fa12_contract_transfer =
[@layout:comb]
  { [@annot:from] address_from : address;
    [@annot:to] address_to : address;
    value : nat }

[@inline]
let fa12_transfer (fa12_address : address) (from_ : address) (to_ : address) (value : nat) : operation = 
  let fa12_contract : fa12_contract_transfer contract = 
    match (Tezos.get_entrypoint_opt "%transfer" fa12_address : fa12_contract_transfer contract option) with
    | None -> (failwith(error_FA12_CONTRACT_MUST_HAVE_A_TRANSFER_ENTRYPOINT) : fa12_contract_transfer contract)
    | Some contract -> contract in
    let transfer = {address_from = from_; address_to = to_; value = value} in
    Tezos.transaction transfer 0mutez fa12_contract


[@inline]
let prepare_multisig (type p) (entrypoint_name: string) (param: p) (func: unit -> operation list) (store : storage) : operation list =
    match (Tezos.get_entrypoint_opt "%callMultisig" store.multisig : call_param contract option ) with
    | None -> (failwith("no call entrypoint") : operation list)
    | Some contract ->
        let packed = Bytes.pack param in
        let param_hash = Crypto.sha256 packed in
        let entrypoint_signature =
          {
            name = entrypoint_name;
            params = param_hash;
            source_contract = (Tezos.get_self_address ());
          }
        in
        let call_param =
        {
          entrypoint_signature = entrypoint_signature;
          callback = func;
        }
        in
        let set_storage = Tezos.transaction call_param 0mutez contract in
        [set_storage]