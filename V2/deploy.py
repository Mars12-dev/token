
from pytezos import ContractInterface, pytezos
from pytezos.contract.result import OperationResult


ALICE_KEY = "edsk3EQB2zJvvGrMKzkUxhgERsy6qdDDw19TQyFWkYNUmGSxXiYm7Q"
ALICE_PK = "tz1Yigc57GHQixFwDEVzj5N1znSCU3aq15td"
SHELL = "https://rpc.ghostnet.teztnets.xyz/"
# SHELL = "http://localhost:8732"

using_params = dict(shell=SHELL, key=ALICE_KEY)
pytezos = pytezos.using(**using_params)
send_conf = dict(min_confirmations=3)


def deploy_multisig():
    with open("michelson/multisig.tz", encoding="UTF-8") as mich_file:
        michelson = mich_file.read()

    multisig = ContractInterface.from_michelson(
        michelson).using(**using_params)

    storage = {
        "admins": {ALICE_PK},
        "n_calls": {},
        "threshold": 1,
        "duration": 3600,
        "authorized_contracts": [],
    }
    opg = multisig.originate(initial_storage=storage).send(**send_conf)
    multisig_addr = OperationResult.from_operation_group(opg.opg_result)[
        0
    ].originated_contracts[0]
    multisig = pytezos.using(**using_params).contract(multisig_addr)

    return multisig


def deploy_collection(royalties: str, multisig: str):
    with open("michelson/collection.tz", encoding="UTF-8") as mich_file:
        michelson = mich_file.read()

    collection = ContractInterface.from_michelson(
        michelson).using(**using_params)

    storage = {
        "next_collection_id": 0,
        "royalties": royalties,
        "collections": {},
        "multisig": multisig,
    }
    opg = collection.originate(initial_storage=storage).send(**send_conf)
    collection_addr = OperationResult.from_operation_group(opg.opg_result)[
        0
    ].originated_contracts[0]
    collection = pytezos.using(**using_params).contract(collection_addr)

    return collection


def deploy_royalties(multisig: str):
    with open("michelson/royalties.tz", encoding="UTF-8") as mich_file:
        michelson = mich_file.read()

    royalties = ContractInterface.from_michelson(michelson).using(
        **using_params
    )
    storage = {
        "multisig": multisig,
        "proxy": [],
        "royalties": {},
        "paused": False,
    }
    opg = royalties.originate(initial_storage=storage).send(**send_conf)
    royalties_addr = OperationResult.from_operation_group(opg.opg_result)[
        0
    ].originated_contracts[0]
    royalties = pytezos.using(**using_params).contract(royalties_addr)

    return royalties


multisig = deploy_multisig()
royalties = deploy_royalties(multisig.address)
collection = deploy_collection(royalties.address, multisig.address)
multisig.addAuthorizedContract(royalties.address).send(**send_conf)
multisig.addAuthorizedContract(collection.address).send(**send_conf)
royalties.updateProxy({"add_proxy": collection.address}).send(**send_conf)
collection.addCollection({
    "nft_deployment": {"new": None},
    "tokens_to_mint": [],
    "royalties": 300,
}).send(**send_conf)


print(f"royalties address: {royalties.address}")
print(f"multisig address: {multisig.address}")
print(f"collection address: {collection.address}")
