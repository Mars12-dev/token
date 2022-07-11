from dataclasses import dataclass
import json
from pytezos import pytezos
from pytezos import ContractInterface
from pytezos.contract.result import OperationResult


class Keys:
    def __init__(self, shell="http://localhost:20000"):
        self.ALICE_KEY = "edsk3EQB2zJvvGrMKzkUxhgERsy6qdDDw19TQyFWkYNUmGSxXiYm7Q"
        self.ALICE_PK = "tz1Yigc57GHQixFwDEVzj5N1znSCU3aq15td"
        self.BOB_KEY = "edsk4YDWx5QixxHtEfp5gKuYDd1AZLFqQhmquFgz64mDXghYYzW6T9"
        self.BOB_PK = "tz1RTrkJszz7MgNdeEvRLaek8CCrcvhTZTsg"
        self.SHELL = shell

        # docker shell
        # self.SHELL = "http://tz:20000"

        self.alice_using_params = dict(shell=self.SHELL, key=self.ALICE_KEY)
        self.alice_pytezos = pytezos.using(**self.alice_using_params)

        self.bob_using_params = dict(shell=self.SHELL, key=self.BOB_KEY)
        self.bob_pytezos = pytezos.using(**self.bob_using_params)


default_keys = Keys()


@dataclass
class MultisigStorage:
    authorized_contracts: str = default_keys.ALICE_PK
    admins: str = default_keys.ALICE_PK


ALICE_PK = default_keys.ALICE_PK
BOB_PK = default_keys.BOB_PK

alice_pytezos = default_keys.alice_pytezos
bob_pytezos = default_keys.bob_pytezos

send_conf = dict(min_confirmations=1)


class Env:
    def __init__(self, shell=default_keys.SHELL):
        self.alice_using_params = Keys(shell=shell).alice_using_params

    def deploy_multisig(self):
        with open("../michelson/multisig.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()

        multisig = ContractInterface.from_michelson(
            michelson).using(**self.alice_using_params)
        init_storage = MultisigStorage()

        storage = {
            "admins": {init_storage.admins},
            "n_calls": {},
            "threshold": 1,
            "duration": 3600,
            "authorized_contracts": {init_storage.authorized_contracts},
        }
        opg = multisig.originate(initial_storage=storage).send(**send_conf)
        multisig_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        multisig = pytezos.using(
            **self.alice_using_params).contract(multisig_addr)

        return multisig

    def deploy_atf(self):

        total_supply = 1_000_000_000 * 10 ** 5

        with open("../michelson/atf.tz", "r", encoding="UTF8") as file:
            michelson = file.read()

        atf = ContractInterface.from_michelson(michelson).using(
            **self.alice_using_params
        )

        # multisig = self.deploy_multisig()
        multisig_addr = "KT1KEmfsdhbbG89MtyG2EEbDv7LGZkUL3X5P"
        multisig = pytezos.using(**self.alice_using_params).contract(multisig_addr)

        storage = {
            "paused": False,
            "burn_paused": False,
            "ledger": {ALICE_PK: total_supply},
            "allowances": {},
            "total_supply": total_supply,
            "metadata": {
                "": "tezos-storage:content".encode().hex(),
                "content": json.dumps({
                    "name": "ATF",
                    "authors": ["atfMI <hello@atfmi.com>"],
                    "version": "1.0.0",
                    "homepage": "https://atfmi.com/",
                    "interfaces": ["TZIP-007", "TZIP-016"],
                    "symbol": "atf",
                    "icon": " ",
                    "decimals": "5",
                    "shouldPreferSymbol": "true"
                }).encode().hex()
            },
            "token_metadata": {},
            "multisig": multisig.address,
        }
        opg = atf.originate(initial_storage=storage).send(**send_conf)
        atf_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        multisig.addAuthorizedContract(atf_addr).send(**send_conf)
        atf = alice_pytezos.using(
            **self.alice_using_params).contract(atf_addr)

        return atf
