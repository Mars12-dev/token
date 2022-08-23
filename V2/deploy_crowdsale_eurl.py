from deploy_crowdsale_env import Env, CrowdsaleStorage, pytezos, send_conf, ALICE_PK, FA12Storage

print("init")
init_storage = CrowdsaleStorage(max_mint_per_transaction=2,
                                paused=False, default_metadata=b"http://my_metadata")
print("deploying crodwsale")
crowdsale = Env().deploy_crowdsale(init_storage)
collection = crowdsale.storage["collection"]()
multisig = crowdsale.storage["multisig"]()

print("deploying eurl")
# testnet eurl: deploys an fa1.2 contract
eurl_contract = Env().deploy_fa12(FA12Storage(ALICE_PK))

print(f"crowdsale: {crowdsale.address}")
print(f"collection: {collection}")
print(f"multisig: {multisig}")
print(f"eurl contract address: {eurl_contract.address}")

# mainnet eurl: existing mainnet contract
# eurl_address = "KT1JBNFcB5tiycHNdYGYCtR3kk6JaJysUCi8"
# eurl_contract = pytezos.using(**Env().using_params).contract(eurl_address)

sale_params = {
    "is_presale": False,
    "metadata_list": [],
    "price_per_token": 2,
    "max_mint_per_user": 2,
    "sale_size": 50,
    "sale_currency": {"fa12": eurl_contract.address},
    "start_time": py(Tezos.get_now ())(),
    "end_time": py(Tezos.get_now ())() + 3600000,
}
print("Setting sale")
crowdsale.setSale(sale_params).send(**send_conf)


# whitelist `user` template:
# {
#     "user_address" : address,
#     "tokens_to_mint" : int,
# }
# user_list = [user1, user2, ...]

# crowdsale.addToWhitelist(user_list).send(**send_conf)

mint_params = {
    "tokens": 2,
    "owner": ALICE_PK,
    "amount_to_pay": 4,
}

print("Trying to mint for test purposes...")
print("minting eurl for Alice")
eurl_contract.mint({"address": ALICE_PK, "value": 4}).send(**send_conf)
print("minting eurl for user")
eurl_contract.mint({"address": "tz2NvmvAbt5qEEg7E1cauE47uR3Q5LxdMBJS",
                   "value": 1000000000}).send(**send_conf)
print("approving crowdsale to transfer eurl for Alice")
eurl_contract.approve({
    "spender": crowdsale.address,
    "value": 4}
).send(**send_conf)
print("minting 2 NFTs for Alice")
crowdsale.mintFromCrowdsale(mint_params).send(**send_conf)
print("Successfully deployed and minted !")
