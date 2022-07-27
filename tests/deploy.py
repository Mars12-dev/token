from env import Env, ALICE_PK, ALICE_KEY, admin, alice_pytezos, MarketplaceStorage


SHELL = "https://rpc.ghostnet.teztnets.xyz/"


send_conf = dict(min_confirmations=3)

print("Deploying contract...")

atf_addr = "KT1LqLtQsGy96SQwRERhYP4XuukF9L2tEpNT"
atf = alice_pytezos.contract(atf_addr)
eurl_addr = "KT1RVK54ne4gFfqyMwGD6zZk4crFkf1TD1kn"
eurl = alice_pytezos.contract(eurl_addr)
action_addr = "KT1Nngvd6ouvEj6aFegQ37U9Kukr4mAYEXRK"
action = alice_pytezos.contract(action_addr)
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
atf.setTokenMetadata(param_metadata).send(**send_conf)
multisig_addr = atf.storage["multisig"]()
multisig = alice_pytezos.using(
    shell=SHELL, key=ALICE_KEY).contract(multisig_addr)

marketplace_storage = MarketplaceStorage(multisig=ALICE_PK)

marketplace_storage.atf_address = atf_addr

marketplace = Env(SHELL).deploy_marketplace(marketplace_storage)
nft = Env(SHELL).deploy_nft(marketplace=marketplace.address,
                            multisig=multisig.address)
multisig.addAuthorizedContract(marketplace.address).send(**send_conf)
multisig.addAuthorizedContract(nft.address).send(**send_conf)
marketplace.addCollection(nft.address).send(**send_conf)
marketplace.updateAdmin(admin).send(**send_conf)

mint_param = {
    "token_id": 0,
    "token_metadata": {},
    "amount_": 1,
    "owner": "tz1TaKUpdcuFRKWpMVeDP2eQcme4nxc8Jx8u",
}

nft.mint(mint_param).send(**send_conf)
mint_param["token_id"] = 1
nft.mint(mint_param).send(**send_conf)
mint_param["token_id"] = 2
nft.mint(mint_param).send(**send_conf)


print("\natf_addr = " + atf.address + '"')
print("\naction_addr = " + action.address + '"')
print("\neurl_addr = " + eurl_addr + '"')
# print("\nswap_addr = " + swap.address + '"')
print("\nmarketplace_addr = " + marketplace.address + '"')
print("\nnft_addr = " + nft.address + '"')
print("multisig_addr = " + multisig_addr + '"')
