#if !MULTISIG_INTERFACE
#define MULTISIG_INTERFACE

type entrypoint_signature =
[@layout:comb]
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

type self_admin_param =
| Add_admin of address
| Remove_admin of address
| Set_threshold of nat
| Set_duration of nat
| Add_authorized_contract of address

type parameter =
| CallMultisig of call_param
//| SelfAdmin of self_admin_param
| AddAdmin of address
| RemoveAdmin of address
| SetThreshold of nat
| SetDuration of nat
| AddAuthorizedContract of address

#endif