#include "treasury_errors.mligo"
#include "treasury_interface.mligo"
#include "treasury_functions.mligo"
#include "entrypoints/update_multisig_address.mligo"
#include "entrypoints/withdraw.mligo"
#include "entrypoints/deposit.mligo"


let main (action, store : parameter * storage) : return =
match action with
| Withdraw p -> withdraw p store
| Deposit p -> deposit p store
| UpdateMultisig p -> update_multisig_address p store
