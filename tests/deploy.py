from env import Env, ALICE_PK, ALICE_KEY, admin, alice_pytezos, MarketplaceStorage


SHELL = "https://rpc.tzkt.io/ghostnet/"


send_conf = dict(min_confirmations=3)

print("Deploying contract...")

atf_addr = "KT1WvFhGYgsdYCAkRnJWYtCLNa2jvZGXDJh8"
atf = alice_pytezos.contract(atf_addr)
# atf = Env(SHELL).deploy_atf()
eurl_addr = "KT1RVK54ne4gFfqyMwGD6zZk4crFkf1TD1kn"
eurl = alice_pytezos.contract(eurl_addr)
action_addr = "KT1UsKzmijVUpf51oa9XKhznGxUPKL5iFua6"
action = alice_pytezos.contract(action_addr)
# action = Env(SHELL).deploy_action()
# swap = Env(SHELL).deploy_swap(token_in=eurl.address,
#                               token_out=atf.address, treasury=admin, admin=admin)


param_metadata = {
    "uri": "tezos-storage:content".encode().hex(),
    "name": "ATF".encode().hex(),
    "symbol": "ATF".encode().hex(),
    "decimals": "5".encode().hex(),
    "shouldPreferSymbol": "true".encode().hex(),
    "thumbnailUri": "".encode().hex(),
}
# atf.setTokenMetadata(param_metadata).send(**send_conf)
multisig_addr = atf.storage["multisig"]()
multisig = alice_pytezos.using(
    shell=SHELL, key=ALICE_KEY).contract(multisig_addr)

marketplace_storage = MarketplaceStorage(multisig=ALICE_PK)

marketplace_storage.atf_address = atf.address
marketplace_storage.ap_address = action.address
marketplace_storage.eurl_address = eurl.address

marketplace = Env(SHELL).deploy_marketplace(marketplace_storage)
# nft = Env(SHELL).deploy_nft(marketplace=marketplace.address,
#                             multisig=multisig.address)
nft_addr = "KT1MoEUVGUVxmHC7YmyrzcPtoWDFXrQpVZLw"
nft = alice_pytezos.contract(nft_addr)
# multisig.addAuthorizedContract(marketplace.address).send(**send_conf)
# multisig.addAuthorizedContract(nft.address).send(**send_conf)
marketplace.addCollection(nft.address).send(**send_conf)
marketplace.updateAdmin(admin).send(**send_conf)

# mint_param = {
#     "token_id": 0,
#     "token_metadata": {},
#     "amount_": 1,
#     "owner": "tz1TaKUpdcuFRKWpMVeDP2eQcme4nxc8Jx8u",
# }

# nft.mint(mint_param).send(**send_conf)
# mint_param["token_id"] = 1
# nft.mint(mint_param).send(**send_conf)
# mint_param["token_id"] = 2
# nft.mint(mint_param).send(**send_conf)


print("\natf_addr = " + atf.address + '"')
print("\naction_addr = " + action.address + '"')
print("\neurl_addr = " + eurl_addr + '"')
# print("\nswap_addr = " + swap.address + '"')
print("\nmarketplace_addr = " + marketplace.address + '"')
print("\nnft_addr = " + nft.address + '"')
print("multisig_addr = " + multisig_addr + '"')
