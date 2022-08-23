#include "multisig_errors.mligo"
#include "multisig_interface.mligo"
#include "multisig_functions.mligo"
#include "entrypoints/call.mligo"
#include "entrypoints/add_admin.mligo"
#include "entrypoints/remove_admin.mligo"
#include "entrypoints/set_threshold.mligo"
#include "entrypoints/set_duration.mligo"
#include "entrypoints/add_authorized_contract.mligo"
#include "entrypoints/remove_authorized_contract.mligo"
#include "views/get_admins.mligo"


let main (action, store : parameter * storage) : return =
match action with
| CallMultisig p -> call p store
| AddAdmin p -> add_admin p store
| RemoveAdmin p -> remove_admin p store
| SetThreshold p -> set_threshold p store
| SetDuration p -> set_duration p store
| AddAuthorizedContract p -> add_authorized_contract p store
| RemoveAuthorizedContract p -> remove_authorized_contract p store
