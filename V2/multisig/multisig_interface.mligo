type entrypoint_signature =
{
    name : string;
    params : bytes;
    source_contract : address;
}

type storage =
{
    n_calls : (entrypoint_signature, (address set * timestamp)) big_map;
    threshold : nat;
    admins : address set;
    duration : int;
    authorized_contracts : address set;
}

type return = operation list * storage

type call_param =
[@layout:comb]
{
    entrypoint_signature : entrypoint_signature;
    callback : unit -> operation list;
}

type parameter =
| CallMultisig of call_param
| AddAdmin of address
| RemoveAdmin of address
| SetThreshold of nat
| SetDuration of nat
| AddAuthorizedContract of address
| RemoveAuthorizedContract of address