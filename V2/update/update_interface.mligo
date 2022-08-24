#if !MERGE_INTERFACE
#define MERGE_INTERFACE

#include "../common/interface.mligo"

type update_attribute_param =
[@layout:comb]
{ nft_address: address;
  type_: string;
  key: string;
  token_id: nat;
  value: string;
}
type batch_update_attribute_param = update_attribute_param list

type remove_attribute_param =
[@layout:comb]
{ nft_address: address;
  key: string;
  token_id: nat;
}
type batch_remove_attribute_param = remove_attribute_param list

type attributes_from_param_param =
{
  a: string;
  b: string;
  c: string;
  d: string;
  e: string;
  f: string;
  g: string;
  h: string;
}
type update_param_inner =
{
  artifactUri: bytes;
  attributes: attributes_from_param_param;
  displayUri: bytes;
  formats: bytes;
  thumbnailUri: bytes;
}
type update_param =
{ nft_address: address;
  metadata: update_param_inner;
  token_id: token_id;
}

type set_ipfs_hashes_param = 
{ nft_address: address;
  ipfs_hashes: string;
}
type add_update_admin_param = address
type remove_update_admin_param = address

type merge_asset_avatar_param =
[@layout:comb]
{
  asset_address : address;
  avatar_address : address;
  asset_id: nat;
  avatar_id : nat;
}

type update_name_param =
[@layout:comb]
{ nft_address: address;
  token_id: token_id;
  new_name: bytes;
}
type batch_update_name_param = update_name_param list

type update_description_param =
[@layout:comb]
{ nft_address: address;
  token_id: token_id;
  new_description: bytes;
}
type batch_update_description_param = update_description_param list



(* storage types *)
type storage =
[@layout:comb]
{
  paused: bool;
  multisig : address;
  update_admins: address set;
  ipfs_hashes: (address, string) big_map;
}

type return = operation list * storage

type parameter =
| AddUpdateAdmin of add_update_admin_param
| BatchRemoveUpdateAttribute of batch_remove_attribute_param 
| BatchUpdateDescription of batch_update_description_param
| BatchUpdateName of batch_update_name_param
| MergeAssetToAvatar of merge_asset_avatar_param
| RemoveUpdateAdmin of  remove_update_admin_param
| SetIpfsHashes  of set_ipfs_hashes_param
| UpdateMetadata of update_param
| BatchUpdateAttribute of batch_update_attribute_param
| SetPause of bool








#endif

