import json
from pytezos import pytezos

ADMIN_PKH = ''
ADMIN_SK = ''
ATF_ADDRESS = 'KT1Ha4yFVeyzw6KRAdkzq6TxDHB97KG4pZe8'
shell = "https://mainnet.api.tez.ie"


# shell = "https://ithacanet.ecadinfra.com/"

wallet_using_params = dict(shell=shell, key=ADMIN_SK)
wallet_pytezos = pytezos.using(**wallet_using_params)
send_conf = dict(min_confirmations=1)

contract = wallet_pytezos.using(**wallet_using_params).contract(ATF_ADDRESS)


IPFS_LINK = " "

new_metadata = json.dumps({
    "name": "ATF",
    "authors": ["ATF <hello@ATF.com>"],
    "version": "1.0.0",
    "homepage": "https://ATF.com/",
    "interfaces": ["TZIP-007", "TZIP-016"],
    "symbol": "ATF",
    "icon": IPFS_LINK,
    "decimals": "5",
    "shouldPreferSymbol": "true"
}).encode()
contract.setMetadata(new_metadata.hex()).send(**send_conf)

param_metadata = {
    "uri": "tezos-storage:content".encode().hex(),
    "name": "ATF".encode().hex(),
    "symbol": "ATF".encode().hex(),
    "decimals": "5".encode().hex(),
    "shouldPreferSymbol": "true".encode().hex(),
    "thumbnailUri": IPFS_LINK.encode().hex(),
}
contract.setTokenMetadata(param_metadata).send(**send_conf)

print("done")


