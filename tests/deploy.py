from env import Keys, Env

default_keys = Keys("https://ithacanet.ecadinfra.com/")

ALICE_PK = default_keys.ALICE_PK
BOB_PK = default_keys.BOB_PK
SHELL = default_keys.SHELL

alice_pytezos = default_keys.alice_pytezos
bob_pytezos = default_keys.bob_pytezos

send_conf = dict(min_confirmations=1)

print("Deploying contract...")

atf = Env(SHELL).deploy_atf()

param_metadata = {
    "uri": "tezos-storage:content".encode().hex(),
    "name": "ATF".encode().hex(),
    "symbol": "ATF".encode().hex(),
    "decimals": "5".encode().hex(),
    "shouldPreferSymbol": "true".encode().hex(),
    "thumbnailUri": "".encode().hex(),
}
atf.setTokenMetadata(param_metadata).send(**send_conf)

print("\natf_addr = " + atf.address + '"')
print("multisig_addr = " + atf.storage["multisig"]() + '"')
