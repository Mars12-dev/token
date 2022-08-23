from dataclasses import dataclass
import unittest
from pytezos import ContractInterface, pytezos
from pytezos.contract.result import OperationResult
from pytezos.rpc.errors import MichelsonError
from data import normalizer_data


# sandbox
ALICE_KEY = "edsk3EQB2zJvvGrMKzkUxhgERsy6qdDDw19TQyFWkYNUmGSxXiYm7Q"
ALICE_PK = "tz1Yigc57GHQixFwDEVzj5N1znSCU3aq15td"
BOB_PK = "tz1RTrkJszz7MgNdeEvRLaek8CCrcvhTZTsg"
BOB_KEY = "edsk4YDWx5QixxHtEfp5gKuYDd1AZLFqQhmquFgz64mDXghYYzW6T9"
CHARLIE_PK = "tz1iYCR11SMJcpAH3egtDjZRQgLgKX6agU7s"
CHARLIE_KEY = "edsk3G87qnDZhR74qYDFAC6nE17XxWkvPJtWpLw4vfeZ3otEWwwskV"

SHELL = "http://localhost:8732"
# SHELL = "https://hangzhounet.api.tez.ie"

_using_params = dict(shell=SHELL, key=ALICE_KEY)
pytezos = pytezos.using(**_using_params)

bob_using_params = dict(shell=SHELL, key=BOB_KEY)
bob_pytezos = pytezos.using(**bob_using_params)

charlie_using_params = dict(shell=SHELL, key=CHARLIE_KEY)
charlie_pytezos = pytezos.using(**charlie_using_params)

send_conf = dict(min_confirmations=1)


@dataclass
class FA2Storage:
    multisig: str
    proxy: str = ALICE_PK


@dataclass
class RoyaltiesStorage:
    multisig: str
    proxy: str = ALICE_PK


@dataclass
class TreasuryStorage:
    multisig: str = ALICE_PK


@dataclass
class MarketplaceStorage:
    multisig: str
    treasury: str
    nft_address: str = ALICE_PK
    royalties_address: str = ALICE_PK
    oracle: str = ALICE_PK
    xtz_address: str = ALICE_PK
    usd_address: str = ALICE_PK


@dataclass
class AuctionStorage:
    multisig: str
    treasury: str
    nft_address: str = ALICE_PK
    royalties_address: str = ALICE_PK
    oracle: str = ALICE_PK
    xtz_address: str = ALICE_PK
    usd_address: str = ALICE_PK


@dataclass
class BlindAuctionStorage:
    multisig: str
    treasury: str
    nft_address: str = ALICE_PK
    royalties_address: str = ALICE_PK
    oracle: str = ALICE_PK
    xtz_address: str = ALICE_PK
    usd_address: str = ALICE_PK


@dataclass
class FA12Storage:
    admin: str


@dataclass
class NormalizerStorage:
    oracleContract: str = "KT19yapgDLPR3CuvK32xJHgxNJigyNxjSr4y"


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
        with open("../michelson/multisig.tz", encoding="UTF-8") as mich_file:
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

    def deploy_treasury(self, init_storage: TreasuryStorage):
        with open("../michelson/treasury.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        treasury = ContractInterface.from_michelson(
            michelson).using(**self.using_params)

        storage = {
            "multisig": init_storage.multisig,
            "ledger": {},
        }
        opg = treasury.originate(initial_storage=storage).send(**send_conf)
        treasury_addr = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        treasury = pytezos.using(**self.using_params).contract(treasury_addr)

        return treasury

    def deploy_nft(self, init_storage: FA2Storage):
        with open("../michelson/nft.tz", encoding="UTF-8") as mich_file:
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

    def deploy_royalties(self, init_storage: RoyaltiesStorage):
        with open("../michelson/royalties.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()

        royalties = ContractInterface.from_michelson(michelson).using(
            **self.using_params
        )
        storage = {
            "multisig": init_storage.multisig,
            "proxy": init_storage.proxy,
            "royalties": {},
            "paused": False,
        }
        opg = royalties.originate(initial_storage=storage).send(**send_conf)
        royalties_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        royalties = pytezos.using(**self.using_params).contract(royalties_addr)

        return royalties

    def deploy_fa12(self, init_storage: FA12Storage):
        with open("../michelson/fa12.tz", encoding="UTF-8") as mich_file:
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

    def deploy_normalizer(self):
        with open("../michelson/normalizer.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        normalizer = ContractInterface.from_michelson(michelson).using(
            **self.using_params
        )
        storage = normalizer_data
        opg = normalizer.originate(initial_storage=storage).send(**send_conf)
        normalizer_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        normalizer = pytezos.using(
            **self.using_params).contract(normalizer_addr)

        return normalizer

    def deploy_marketplace(self, init_storage: MarketplaceStorage):

        with open("../michelson/marketplace.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        marketplace = ContractInterface.from_michelson(michelson).using(
            **self.using_params
        )
        storage = {
            "multisig": init_storage.multisig,
            "treasury": init_storage.treasury,
            "nft_address": init_storage.nft_address,
            "royalties_address": init_storage.royalties_address,
            "next_token_id": 0,
            "next_swap_id": 0,
            "tokens": {},
            "swaps": {},
            "offers": {},
            "counter_offers": {},
            "management_fee_rate": 250,
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
            },
            "available_pairs": {
                ("XTZ", "USD"): "XTZ-USD",
            },
            "oracle": init_storage.oracle,
        }
        opg = marketplace.originate(initial_storage=storage).send(**send_conf)
        marketplace_address = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        marketplace = pytezos.using(
            **self.using_params).contract(marketplace_address)
        return marketplace

    def deploy_auction(self, init_storage: AuctionStorage):
        with open("../michelson/auction.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()

        auction = ContractInterface.from_michelson(
            michelson).using(**self.using_params)
        storage = {
            "nft_address": init_storage.nft_address,
            "royalties_address": init_storage.royalties_address,
            "swaps": {},
            "next_swap_id": 0,
            "management_fee_rate": 250,
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
            },
            "available_pairs": {
                ("XTZ", "USD"): "XTZ-USD",
            },
            "oracle": init_storage.oracle,
            "multisig": init_storage.multisig,
            "treasury": init_storage.treasury,
        }
        opg = auction.originate(initial_storage=storage).send(**send_conf)
        auction_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        auction = pytezos.using(**self.using_params).contract(auction_addr)

        return auction

    def deploy_blind_auction(self, init_storage: BlindAuctionStorage):
        with open("../michelson/blind_auction.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()

        blind_auction = ContractInterface.from_michelson(michelson).using(
            **self.using_params
        )
        storage = {
            "nft_address": init_storage.nft_address,
            "royalties_address": init_storage.royalties_address,
            "swaps": {},
            "bids": {},
            "next_swap_id": 0,
            "next_bid_id": 0,
            "management_fee_rate": 250,
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
            },
            "available_pairs": {
                ("XTZ", "USD"): "XTZ-USD",
            },
            "oracle": init_storage.oracle,
            "multisig": init_storage.multisig,
            "treasury": init_storage.treasury,
        }
        opg = blind_auction.originate(
            initial_storage=storage).send(**send_conf)
        blind_auction_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        blind_auction = pytezos.using(
            **self.using_params).contract(blind_auction_addr)

        return blind_auction

    def deploy_crowdsale(self, init_storage: CrowdsaleStorage):
        multisig = self.deploy_multisig(MultisigStorage)
        collection = self.deploy_nft(FA2Storage(multisig=multisig.address))
        with open("../michelson/crowdsale.tz", encoding="UTF-8") as mich_file:
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
            "start_time": pytezos.now(),
            "end_time": pytezos.now(),
            "sale_size": 0,
            "sale_currency": {"xtz": None},
            "collection": collection.address,
            "available_metadata": [],
            "paused": init_storage.paused,
            "default_metadata": {"": init_storage.default_metadata},
            "earnings": 0,
        }
        opg = crowdsale.originate(
            initial_storage=crowdsale_init_storage).send(**send_conf)

        crowdsale_address = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        crowdsale = pytezos.using(
            **self.using_params).contract(crowdsale_address)
        multisig.addAuthorizedContract(crowdsale_address).send(**send_conf)
        multisig.addAuthorizedContract(collection.address).send(**send_conf)
        collection.updateProxy(
            {"add_proxy": crowdsale_address}).send(**send_conf)

        return crowdsale

    def deploy_app(self):
        fa12_init_storage = FA12Storage(ALICE_PK)
        oracle = self.deploy_normalizer()
        usd_fa12 = self.deploy_fa12(fa12_init_storage)
        multisig = self.deploy_multisig(MultisigStorage)
        treasury_init_storage = TreasuryStorage()
        treasury_init_storage.multisig = multisig.address
        treasury = self.deploy_treasury(treasury_init_storage)
        marketplace_init_storage = MarketplaceStorage(
            multisig=multisig.address, treasury=treasury.address, oracle=oracle.address, usd_address=usd_fa12.address)
        marketplace = self.deploy_marketplace(marketplace_init_storage)
        auction = self.deploy_auction(marketplace_init_storage)
        blind_auction = self.deploy_blind_auction(marketplace_init_storage)
        nft_init_storage = FA2Storage(
            multisig=multisig.address, proxy=[marketplace.address])
        royalties_init_storage = RoyaltiesStorage(
            multisig=multisig.address, proxy=[marketplace.address])
        royalties_contr = self.deploy_royalties(royalties_init_storage)
        nft = self.deploy_nft(nft_init_storage)
        multisig.addAuthorizedContract(marketplace.address).send(**send_conf)
        multisig.addAuthorizedContract(auction.address).send(**send_conf)
        multisig.addAuthorizedContract(blind_auction.address).send(**send_conf)
        multisig.addAuthorizedContract(treasury.address).send(**send_conf)
        multisig.addAuthorizedContract(nft.address).send(**send_conf)
        multisig.addAuthorizedContract(
            royalties_contr.address).send(**send_conf)
        marketplace.updateNftAddress(nft.address).send(**send_conf)
        marketplace.updateRoyaltiesAddress(
            royalties_contr.address).send(**send_conf)
        auction.updateNftAddress(nft.address).send(**send_conf)
        auction.updateRoyaltiesAddress(
            royalties_contr.address).send(**send_conf)
        blind_auction.updateNftAddress(nft.address).send(**send_conf)
        blind_auction.updateRoyaltiesAddress(
            royalties_contr.address).send(**send_conf)

        return marketplace, auction, blind_auction, multisig, nft, royalties_contr, treasury, oracle, usd_fa12


# class TestEnv(unittest.TestCase):
#     marketplace, auction, blind_auction, multisig, nft, royalties_contr, treasury, oracle, usd_fa12 = Env().deploy_app()
#     print("marketplace address:")
#     print(marketplace.address)
#     print("auction address:")
#     print(auction.address)
#     print("blind_auction address:")
#     print(blind_auction.address)
#     print("multisig address:")
#     print(multisig.address)
#     print("nft address:")
#     print(nft.address)
#     print("royalties address:")
#     print(royalties_contr.address)
#     print("treasury address:")
#     print(treasury.address)
#     print("oracle address:")
#     print(oracle.address)
#     print("usd_fa12 address:")
#     print(usd_fa12.address)
