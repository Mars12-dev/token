from dataclasses import dataclass
from pytezos import ContractInterface, pytezos
from pytezos.contract.result import OperationResult

ALICE_PK = "tz1iYCR11SMJcpAH3egtDjZRQgLgKX6agU7s"
ALICE_KEY = "edsk3G87qnDZhR74qYDFAC6nE17XxWkvPJtWpLw4vfeZ3otEWwwskV"

# sandbox shell:
# SHELL = "http://localhost:20000"

# Hangzhounet shell:
# SHELL = "https://hangzhounet.smartpy.io/"

# Ithacanet shell:
SHELL = "https://rpc.ithaca.tzstats.com"

# Mainnet shell:
# SHELL = "https://rpc.tzstats.com"


_using_params = dict(shell=SHELL, key=ALICE_KEY)
pytezos = pytezos.using(**_using_params)
send_conf = dict(min_confirmations=1)


@dataclass
class FA2Storage:
    multisig: str
    proxy: str = ALICE_PK


@dataclass
class FA12Storage:
    admin: str


@dataclass
class MultisigStorage:
    authorized_contracts: str = ALICE_PK
    admins: str = ALICE_PK


@dataclass
class CrowdsaleStorage:
    max_mint_per_transaction: int
    paused: bool
    default_metadata: bytes


class Env:
    def __init__(self, using_params=None):
        self.using_params = using_params or _using_params

    def deploy_multisig(self, init_storage: MultisigStorage):
        with open("michelson/multisig.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()

        multisig = ContractInterface.from_michelson(
            michelson).using(**self.using_params)

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
        multisig = pytezos.using(**self.using_params).contract(multisig_addr)

        return multisig

    def deploy_fa12(self, init_storage: FA12Storage):
        with open("michelson/fa12.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        fa12 = ContractInterface.from_michelson(
            michelson).using(**self.using_params)
        storage = {
            "tokens": {},
            "allowances": {},
            "total_supply": 0,
            "metadata": {},
            "token_metadata": {},
            "paused": False,
            "admin": init_storage.admin
        }
        opg = fa12.originate(initial_storage=storage).send(**send_conf)
        fa12_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        fa12 = pytezos.using(**self.using_params).contract(fa12_addr)

        return fa12

    def deploy_nft(self, init_storage: FA2Storage):
        with open("michelson/nft.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()

        fa2 = ContractInterface.from_michelson(
            michelson).using(**self.using_params)
        storage = {
            "multisig": init_storage.multisig,
            "ledger": {},
            "operators": {},
            "metadata": {"metadata": {}, "token_defs": []},
            "token_metadata": {},
            "proxy": {ALICE_PK},
            "paused": False,
        }
        opg = fa2.originate(initial_storage=storage).send(**send_conf)
        fa2_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        fa2 = pytezos.using(**self.using_params).contract(fa2_addr)

        return fa2

    def deploy_crowdsale(self, init_storage: CrowdsaleStorage):
        print("deploying multisig")
        multisig = self.deploy_multisig(MultisigStorage)
        print("deploying collection")
        collection = self.deploy_nft(FA2Storage(multisig=multisig.address))
        with open("michelson/crowdsale.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        crowdsale = ContractInterface.from_michelson(
            michelson).using(**self.using_params)
        crowdsale_init_storage = {
            "multisig": multisig.address,
            "max_mint_per_transaction": init_storage.max_mint_per_transaction,
            "max_mint_per_user": 0,
            "tokens_sold": 0,
            "whitelist": {},
            "next_token_id": 0,
            "minted_per_user": {},
            "price_per_token": 0,
            "is_presale": True,
            "number_of_users_in_sale": 0,
            "total_to_mint": 0,
            "start_time": py(Tezos.get_now ())(),
            "end_time": py(Tezos.get_now ())(),
            "sale_size": 0,
            "sale_currency": {"xtz": None},
            "collection": collection.address,
            "available_metadata": [],
            "paused": init_storage.paused,
            "default_metadata": {"": init_storage.default_metadata},
            "earnings": 0
        }
        print("deploying crowdsale")
        opg = crowdsale.originate(
            initial_storage=crowdsale_init_storage).send(**send_conf)

        crowdsale_address = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        crowdsale = pytezos.using(
            **self.using_params).contract(crowdsale_address)
        print("adding crowdsale to multisig")
        multisig.addAuthorizedContract(crowdsale_address).send(**send_conf)
        print("adding collection to multisig")
        multisig.addAuthorizedContract(collection.address).send(**send_conf)
        print("adding crowdsale as collection proxy")
        collection.updateProxy(
            {"add_proxy": crowdsale_address}).send(**send_conf)

        return crowdsale
