from env import Env, ALICE_PK, ALICE_KEY, admin, alice_pytezos


SHELL = "https://rpc.ghostnet.teztnets.xyz/"


send_conf = dict(min_confirmations=1)

print("Deploying contract...")

atf_addr = "KT1LqLtQsGy96SQwRERhYP4XuukF9L2tEpNT"
atf = alice_pytezos.contract(atf_addr)
eurl_addr = "KT1RVK54ne4gFfqyMwGD6zZk4crFkf1TD1kn"
eurl = alice_pytezos.contract(eurl_addr)
action_addr = "KT1Nngvd6ouvEj6aFegQ37U9Kukr4mAYEXRK"
action = alice_pytezos.contract(action_addr)
swap = Env(SHELL).deploy_swap(token_in=eurl.address,
                              token_out=atf.address, treasury=admin, admin=admin)

param_metadata = {
    "uri": "tezos-storage:content".encode().hex(),
    "name": "ATF".encode().hex(),
    "symbol": "ATF".encode().hex(),
    "decimals": "5".encode().hex(),
    "shouldPreferSymbol": "true".encode().hex(),
    "thumbnailUri": "".encode().hex(),
}
atf.setTokenMetadata(param_metadata).send(**send_conf)
transfer = {
    "from": ALICE_PK,
    "to": swap.address,
    "value": 10 ** 6 * 10 ** 5
}
atf.transfer(transfer).send(**send_conf)
multisig_addr = atf.storage["multisig"]()
multisig = alice_pytezos.using(
    shell=SHELL, key=ALICE_KEY).contract(multisig_addr)


print("\natf_addr = " + atf.address + '"')
print("\naction_addr = " + action.address + '"')
print("\neurl_addr = " + eurl + '"')
print("\nswap_addr = " + swap.address + '"')
print("multisig_addr = " + atf.storage["multisig"]() + '"')
