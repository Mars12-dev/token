from env import Env


SHELL = "https://rpc.ghostnet.teztnets.xyz/"


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
