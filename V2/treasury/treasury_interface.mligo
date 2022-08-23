type entrypoint_signature =
{
    name : string;
    params : bytes;
    source_contract : address;
}

type call_param =
[@layout:comb]
{
    entrypoint_signature : entrypoint_signature;
    callback : unit -> operation list;
}

type token = string
type token_amount = nat

type token_info = 
{
    fa12_address : address;
    token_amount : token_amount;
}

type ledger = (token, token_info) big_map

type storage = 
[@layout:comb]
{
    ledger : ledger;
    multisig : address;
}

type destination = 
[@layoout:comb]
{
    token_amount: token_amount; 
    to_ : address
}

type withdraw_param =
{
    token : token;
    withdraw_destination: destination list;
}

type deposit_param =
[@layout:comb]
{
    token : token;
    fa12_address : address;
    token_amount : token_amount;
}

type add_admin_param = address

type remove_admin_param = address

type update_multisig_address_param = address

type parameter =
| Withdraw of withdraw_param
| Deposit of deposit_param
| UpdateMultisig of update_multisig_address_param

type return = operation list * storage