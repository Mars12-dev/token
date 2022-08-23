#include "royalties_errors.mligo"
#include "royalties_interface.mligo"
#include "royalties_functions.mligo"
#include "entrypoints/update_multisig_address.mligo"
#include "entrypoints/set_pause.mligo"
#include "entrypoints/update_proxy.mligo"
#include "entrypoints/configure_royalties.mligo"
#include "entrypoints/configure_collection_royalties.mligo"
#include "views/get_royalties.mligo"


let main (action, store : parameter * storage) : return =
match action with
| UpdateProxy p -> update_proxy p store
| ConfigRoyalties p -> configure_royalties p store
| ConfigCollectionRoyalties p -> configure_collection_royalties p store
| UpdateMultisig p -> update_multisig_address p store
| SetPause p -> set_pause p store
