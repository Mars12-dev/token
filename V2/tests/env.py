from dataclasses import dataclass
import json
from pytezos import pytezos
from pytezos import ContractInterface
from pytezos.contract.result import OperationResult


class Keys:
    def __init__(self, shell="https://rpc.tzkt.io/ghostnet/"):
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
admin = "tz1TaKUpdcuFRKWpMVeDP2eQcme4nxc8Jx8u"


@dataclass
class MultisigStorage:
    authorized_contracts: str = default_keys.ALICE_PK
    admins: str = admin


@ dataclass
class MarketplaceStorage:
    admin: str
    treasury: str = default_keys.ALICE_PK
    nft_address: str = default_keys.ALICE_PK
    royalties_address: str = default_keys.ALICE_PK
    oracle: str = default_keys.ALICE_PK
    xtz_address: str = default_keys.ALICE_PK
    usd_address: str = default_keys.ALICE_PK
    atf_address: str = default_keys.ALICE_PK
    ap_address: str = default_keys.ALICE_PK
    eurl_address: str = default_keys.ALICE_PK
    oracle_tolerance: int = 900


ALICE_PK = default_keys.ALICE_PK
ALICE_KEY = default_keys.ALICE_KEY
BOB_PK = default_keys.BOB_PK

alice_pytezos = default_keys.alice_pytezos
bob_pytezos = default_keys.bob_pytezos

send_conf = dict(min_confirmations=3)


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
            "admins": {init_storage.admins, ALICE_PK},
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

        total_supply = 2 * 10 ** 6 * 10 ** 5

        with open("../michelson/atf.tz", "r", encoding="UTF8") as file:
            michelson = file.read()

        atf = ContractInterface.from_michelson(michelson).using(
            **self.alice_using_params
        )

        multisig = self.deploy_multisig()
        # multisig_addr = "KT1KEmfsdhbbG89MtyG2EEbDv7LGZkUL3X5P"
        # multisig = pytezos.using(
        #     **self.alice_using_params).contract(multisig_addr)

        storage = {
            "paused": False,
            "burn_paused": False,
            "ledger": {admin: total_supply // 2, ALICE_PK: total_supply // 2},
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
        multisig.removeAdmin(ALICE_PK)
        atf = alice_pytezos.using(
            **self.alice_using_params).contract(atf_addr)

        return atf

    def deploy_action(self):
        total_supply = 10 ** 6 * 10 ** 5

        with open("../michelson/action.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        action = ContractInterface.from_michelson(
            michelson).using(**self.alice_using_params)
        multisig = self.deploy_multisig()
        storage = {
            "paused": False,
            "burn_paused": False,
            "ledger": {admin: total_supply},
            "allowances": {},
            "total_supply": total_supply,
            "metadata": {
                "": "tezos-storage:content".encode().hex(),
                "content": json.dumps({
                    "name": "ACT",
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

        opg = action.originate(initial_storage=storage).send(**send_conf)
        action_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        multisig.addAuthorizedContract(action_addr).send(**send_conf)
        multisig.removeAdmin(ALICE_PK)
        action = alice_pytezos.using(
            **self.alice_using_params).contract(action_addr)

        return action

    def deploy_swap(self, token_in: str, token_out: str, treasury: str, admin: str):
        with open("../michelson/swap.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        swap = ContractInterface.from_michelson(
            michelson).using(**self.alice_using_params)
        storage = {
            "token_in_address": token_in,
            "token_out_address": token_out,
            "treasury": treasury,
            "token_price": 1000000,
            "admin": admin,
            "paused": False,
            "currency": "XTZ",
            "factor_decimals": 1000000,
        }

        opg = swap.originate(initial_storage=storage).send(**send_conf)
        swap_addr = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        swap = alice_pytezos.using(
            **self.alice_using_params).contract(swap_addr)

        return swap

    def deploy_nft(self, nft_type: str, marketplace: str = ALICE_PK, multisig: str = ALICE_PK):
        with open("../michelson/nft.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        nft = ContractInterface.from_michelson(
            michelson).using(**self.alice_using_params)
        storage = {
            "ledger": {},
            "operators": {},
            "metadata": {},
            "token_metadata": {},
            "proxy": {marketplace},
            "paused": False,
            "burn_paused": False,
            "multisig": multisig,
            "nft_type": nft_type,
        }
        opg = nft.originate(initial_storage=storage).send(**send_conf)
        nft_addr = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        nft = alice_pytezos.contract(nft_addr)

        return nft

    def deploy_marketplace(self, init_storage: MarketplaceStorage):
        with open("../michelson/marketplace.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        marketplace = ContractInterface.from_michelson(
            michelson).using(**self.alice_using_params)
        storage = {
            "nft_address": ALICE_PK,
            "royalties_address": ALICE_PK,
            "next_swap_id": 0,
            "next_token_id": 0,
            "tokens": {},
            "counter_offers": {},
            "swaps": {},
            "offers": {},
            "management_fee_rate": 300,
            "paused": False,
            "allowed_tokens": {
                "XTZ": {
                    "token_symbol": "XTZ",
                    "fa12_address": init_storage.xtz_address,
                },
                "USD": {
                    "token_symbol": "USD",
                    "fa12_address": init_storage.usd_address,
                },
                "ATF": {
                    "token_symbol": "ATF",
                    "fa12_address": init_storage.atf_address,
                },
                "AP": {
                    "token_symbol": "AP",
                    "fa12_address": init_storage.ap_address,
                },
                "EURL": {
                    "token_symbol": "EURL",
                    "fa12_address": init_storage.eurl_address,
                },
            },
            "available_pairs": {
                ("XTZ", "USD"): "XTZ-USD",
            },
            "single_tokens": ["XTZ", "ATF", "AP"],
            "oracle": init_storage.oracle,
            "treasury": init_storage.treasury,
            "admin": init_storage.admin,
        }

        opg = marketplace.originate(initial_storage=storage).send(**send_conf)
        marketplace_addr = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        marketplace = alice_pytezos.contract(marketplace_addr)

        return marketplace

    def deploy_update(self, multisig: str = ALICE_PK, admin: str = ALICE_PK):
        with open("../michelson/update.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        update = ContractInterface.from_michelson(
            michelson).using(**self.alice_using_params)
        storage = {
            "paused": False,
            "multisig": multisig,
            "update_admins": {admin},
            "ipfs_hashes": {},
        }
        opg = update.originate(initial_storage=storage).send(**send_conf)
        update_addr = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        update = alice_pytezos.contract(update_addr)

        return update
