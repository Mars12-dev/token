#include "../common/const.mligo"
#include "../common/interface.mligo"
#include "../common/fucntions.mligo"
#include "update_errors.mligo"
#include "update_interface.mligo"
#include "update_functions.mligo"
#include "entrypoints/add_update_admin.mligo"
#include "entrypoints/batch_remove_update_attribute.mligo"
#include "entrypoints/batch_update_attribute.mligo"
#include "entrypoints/batch_update_description.mligo"
#include "entrypoints/batch_update_name.mligo"
#include "entrypoints/merge_asset_avatar.mligo"
#include "entrypoints/remove_update_admin.mligo"
#include "entrypoints/set_ipfs_hashes.mligo"
#include "entrypoints/update_metadata.mligo"
#include "entrypoints/update_name.mligo"




let main (action, store : parameter * storage) : return =
match action with
| AddUpdateAdmin p -> add_update_admin p store
| BatchRemoveUpdateAttribute p -> batch_remove_update_attribute p store
| BatchUpdateAttribute p -> batch_update_attribute p store
| BatchUpdateDescription p -> batch_update_description p store
| BatchUpdateName p -> batch_update_name p store
| MergeAssetToAvatar p -> merge_asset_avatar p store
| RemoveUpdateAdmin  p -> remove_update_admin p store
| SetIpfsHashes p -> set_ipfs_hashes p store
| UpdateMetadata p -> update_metadata p store
| SetPause p -> set_pause p store
| BatchUpdateAttribute p -> batch_update_attribute p store

