#if !FA2_ERRORS
#define FA2_ERRORS

(** One of the specified `token_id`s is not defined within the FA2 contract *)
let fa2_token_undefined = "FA2_TOKEN_UNDEFINED"
(**
A token owner does not have sufficient balance to transfer tokens from
owner's account
*)
let fa2_insufficient_balance = "FA2_INSUFFICIENT_BALANCE"
(** A transfer failed because of `operator_transfer_policy == No_transfer` *)
let fa2_tx_denied = "FA2_TX_DENIED"
(**
A transfer failed because `operator_transfer_policy == Owner_transfer` and it is
initiated not by the token owner
*)
let fa2_not_owner = "FA2_NOT_OWNER"
(**
A transfer failed because `operator_transfer_policy == Owner_or_operator_transfer`
and it is initiated neither by the token owner nor a permitted operator
 *)
let fa2_not_operator = "FA2_NOT_OPERATOR"
(**
`update_operators` entrypoint is invoked and `operator_transfer_policy` is
`No_transfer` or `Owner_transfer`
*)
let fa2_operators_not_supported = "FA2_OPERATORS_UNSUPPORTED"
(**
Receiver hook is invoked and failed. This error MUST be raised by the hook
implementation
 *)
let fa2_receiver_hook_failed = "FA2_RECEIVER_HOOK_FAILED"
(**
Sender hook is invoked and failed. This error MUST be raised by the hook
implementation
 *)
let fa2_sender_hook_failed = "FA2_SENDER_HOOK_FAILED"
(**
Receiver hook is required by the permission behavior, but is not implemented by
a receiver contract
 *)
let fa2_receiver_hook_undefined = "FA2_RECEIVER_HOOK_UNDEFINED"
(**
Sender hook is required by the permission behavior, but is not implemented by
a sender contract
 *)
let fa2_sender_hook_undefined = "FA2_SENDER_HOOK_UNDEFINED"

[@inline] let error_ONLY_ADMIN_CAN_CALL_THIS_ENTRYPOINT = 1n
[@inline] let error_ONLY_PROXY_CAN_CALL_THIS_ENTRYPOINT = 2n
[@inline] let error_INVALID_TO_ADDRESS = 3n
[@inline] let error_ROYALTIES_TOO_HIGH = 4n
[@inline] let error_ONLY_ISSUER_CAN_CALL_THIS_ENTRYPOINT = 5n
[@inline] let error_ADDRESS_ALREADY_PROXY = 6n
[@inline] let error_ADDRESS_NOT_PROXY = 7n
[@inline] let error_FA2_CONTRACT_IS_PAUSED = 8n
[@inline] let error_ONLY_MANAGER_CONTRACT_CAN_CALL = 9n
[@inline] let error_NO_SET_BURN_PAUSE_ENTRYPOINT = 10n
[@inline] let error_NO_UPDATE_PROXY_ENTRYPOINT = 11n
[@inline] let error_FA2_BURN_IS_PAUSED = 12n
[@inline] let error_UNAUTHORIZED_CONTRACT_ADDRESS = 13n
[@inline] let error_TOKEN_METADATA_ITEM_DOES_NOT_EXIST = 14n



#endif
