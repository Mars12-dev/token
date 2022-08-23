import hashlib
import json
from time import sleep
import unittest
from dataclasses import dataclass
from pytezos import ContractInterface, pytezos
from pytezos.contract.result import OperationResult
from pytezos.michelson.parse import michelson_to_micheline
from pytezos.michelson.types import MichelsonType
from pytezos.rpc.errors import MichelsonError
from data import normalizer_data


# sandbox
ALICE_KEY = "edsk3EQB2zJvvGrMKzkUxhgERsy6qdDDw19TQyFWkYNUmGSxXiYm7Q"
ALICE_PK = "tz1Yigc57GHQixFwDEVzj5N1znSCU3aq15td"
# CHARLIE_PK = "tz1iYCR11SMJcpAH3egtDjZRQgLgKX6agU7s"
# CHARLIE_KEY = "edsk3G87qnDZhR74qYDFAC6nE17XxWkvPJtWpLw4vfeZ3otEWwwskV"
BOB_PK = "tz1RTrkJszz7MgNdeEvRLaek8CCrcvhTZTsg"
BOB_KEY = "edsk4YDWx5QixxHtEfp5gKuYDd1AZLFqQhmquFgz64mDXghYYzW6T9"

# granadanet
# shell = "https://granadanet.api.tez.ie/"

SHELL = "http://localhost:20000"

_using_params = dict(shell=SHELL, key=ALICE_KEY)
pytezos = pytezos.using(**_using_params)

bob_using_params = dict(shell=SHELL, key=BOB_KEY)
bob_pytezos = pytezos.using(**bob_using_params)

# charlie_using_params = dict(shell=SHELL, key=CHARLIE_KEY)
# charlie_pytezos = pytezos.using(**charlie_using_params)

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
            "proxy": init_storage.proxy,
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

    def deploy_full_app(
        self,
        nft_init_storage: FA2Storage,
        royalties_init_storage: RoyaltiesStorage,
        marketplace_init_storage: MarketplaceStorage,
        blind_auction_init_storage: BlindAuctionStorage,
        fa12_init_storage: FA12Storage,
    ):
        normalizer = self.deploy_normalizer()
        treasury = self.deploy_treasury(TreasuryStorage)
        usd_fa12 = self.deploy_fa12(fa12_init_storage)
        multisig = self.deploy_multisig(MultisigStorage)
        blind_auction_init_storage.oracle = normalizer.address
        blind_auction_init_storage.usd_address = usd_fa12.address
        blind_auction_init_storage.treasury = treasury.address
        marketplace_init_storage.usd_address = usd_fa12.address
        marketplace = self.deploy_marketplace(marketplace_init_storage)
        blind_auction = self.deploy_blind_auction(blind_auction_init_storage)
        multisig.addAuthorizedContract(marketplace.address).send(**send_conf)
        multisig.addAuthorizedContract(blind_auction.address).send(**send_conf)
        nft_init_storage.proxy = [
            marketplace.address,
            blind_auction.address,
            ALICE_PK,
        ]
        royalties_init_storage.proxy = [
            marketplace.address,
            blind_auction.address,
        ]
        nft = self.deploy_nft(nft_init_storage)
        foreign_nft = self.deploy_nft(nft_init_storage)
        royalties_contr = self.deploy_royalties(royalties_init_storage)
        marketplace.updateNftAddress(nft.address).send(**send_conf)
        marketplace.updateRoyaltiesAddress(
            royalties_contr.address).send(**send_conf)
        blind_auction.updateNftAddress(nft.address).send(**send_conf)
        blind_auction.updateRoyaltiesAddress(
            royalties_contr.address).send(**send_conf)

        return nft, foreign_nft, royalties_contr, marketplace, blind_auction, normalizer, usd_fa12


def hash_price(reserved_price, secret):
    real_values = (reserved_price, secret)
    tuple_type = "(pair nat string)"
    _ty_hash_tuple = MichelsonType.match(michelson_to_micheline(tuple_type))
    tuple_bytes = _ty_hash_tuple.from_python_object(real_values).pack()
    reserved_price_hashed = hashlib.sha256(tuple_bytes).digest()
    return reserved_price_hashed


def hash_bid(value, secret):
    real_values = (value, secret)
    tuple_type = "(pair nat string)"
    _ty_hash_tuple = MichelsonType.match(michelson_to_micheline(tuple_type))
    tuple_bytes = _ty_hash_tuple.from_python_object(real_values).pack()
    bid_hashed = hashlib.sha256(tuple_bytes).digest()
    return bid_hashed


class TestBlindAuction(unittest.TestCase):
    def test_blind_bid(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        blind_auction_init_storage = BlindAuctionStorage(ALICE_PK, ALICE_PK)
        fa12_init_storage = FA12Storage(ALICE_PK)
        (
            nft,
            foreign_nft,
            _,
            marketplace,
            blind_auction,
            normalizer,
            usd_fa12
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            blind_auction_init_storage,
            fa12_init_storage
        )
        token_id = marketplace.storage["next_token_id"]()
        starting_price = 10 ** 6
        first_bid_price = starting_price + 10 ** 4
        first_bid_secret = "secret"
        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1

        token_id = marketplace.storage["next_token_id"]()
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": blind_auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)
        swap_id = blind_auction.storage["next_swap_id"]()
        period = 100
        blind_auction.startAuction(
            {
                "token_id": token_id,
                "start_time": pytezos.now() + 5,
                "period": period,
                "starting_price": starting_price,
                "reveal_time": 0,
                "reserved_price_hashed": b"",
                "adding_period": 0,
                "extra_duration": 0,
                "token_amount": 1,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)
        (value, secret) = first_bid_price, first_bid_secret
        first_hash = hash_bid(value, secret)
        bid_id = blind_auction.storage["next_bid_id"]()
        sleep(5)
        bob_pytezos.contract(blind_auction.address).bid(swap_id, first_hash).send(
            **send_conf
        )
        self.assertEqual(
            blind_auction.storage["bids"][
                {"swap_id": swap_id, "bidder": BOB_PK, "bid_id": bid_id}
            ](),
            first_hash,
        )
        second_value = value + 10 ** 4
        second_hash = hash_bid(second_value, secret)
        bid_id = blind_auction.storage["next_bid_id"]()
        bob_pytezos.contract(blind_auction.address).bid(swap_id, second_hash).send(
            **send_conf
        )
        self.assertEqual(
            second_hash,
            blind_auction.storage["bids"][
                {"swap_id": swap_id, "bidder": BOB_PK, "bid_id": bid_id}
            ]()
        )

        token_id = 1000
        foreign_nft.mint({"token_id": token_id, "token_metadata": {},
                         "amount_": 1}).send(**send_conf)
        foreign_nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": blind_auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = blind_auction.storage["next_swap_id"]()

        blind_auction.startAuction(
            {
                "token_id": token_id,
                "start_time": pytezos.now() + 5,
                "period": period,
                "starting_price": starting_price,
                "reveal_time": 0,
                "reserved_price_hashed": b"",
                "adding_period": 0,
                "extra_duration": 0,
                "token_amount": 1,
                "token_origin": foreign_nft.address,
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)

        bid_id = blind_auction.storage["next_bid_id"]()
        sleep(5)
        bob_pytezos.contract(blind_auction.address).bid(swap_id, first_hash).send(
            **send_conf
        )
        self.assertEqual(
            blind_auction.storage["bids"][
                {"swap_id": swap_id, "bidder": BOB_PK, "bid_id": bid_id}
            ](),
            first_hash
        )

    def test_reveal_blind_bid(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        blind_auction_init_storage = BlindAuctionStorage(ALICE_PK, ALICE_PK)
        fa12_init_storage = FA12Storage(ALICE_PK)
        (
            nft,
            _,
            _,
            marketplace,
            blind_auction,
            normalizer,
            usd_fa12
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            blind_auction_init_storage,
            fa12_init_storage
        )
        token_id = marketplace.storage["next_token_id"]()
        starting_price = 10 ** 6
        first_bid_price = starting_price + 10 ** 4
        first_bid_secret = "secret"
        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1

        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": blind_auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = blind_auction.storage["next_swap_id"]()
        start_time = pytezos.now() + 5

        with self.assertRaises(MichelsonError) as err:
            start_time = pytezos.now() + 100
            period = 100
            blind_auction.startAuction(
                {
                    "token_id": token_id,
                    "start_time": start_time,
                    "period": period,
                    "starting_price": starting_price,
                    "reveal_time": 50,
                    "reserved_price_hashed": b"",
                    "adding_period": 0,
                    "extra_duration": 0,
                    "token_amount": 1,
                    "token_origin": nft.address,
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)

            (value, secret) = first_bid_price, first_bid_secret
            first_hash = hash_bid(value, secret)
            bid_id = blind_auction.storage["next_bid_id"]()
            sleep(5)
            bob_pytezos.contract(blind_auction.address).bid(swap_id, first_hash).send(
                **send_conf
            )
            blind_auction.revealBids(
                {
                    "swap_id": swap_id,
                    "secret": secret,
                    "bid_id": bid_id,
                    "value": value,
                    "token_symbol": "XTZ"
                }
            ).with_amount(value).send(**send_conf)

            self.assertEqual(err.exception.args[0]["with"], {"int": "228"})

        with self.assertRaises(MichelsonError) as err:
            start_time = pytezos.now() + 5
            period = 10
            blind_auction.startAuction(
                {
                    "token_id": token_id,
                    "start_time": start_time,
                    "period": period,
                    "starting_price": starting_price,
                    "reveal_time": 0,
                    "reserved_price_hashed": b"",
                    "adding_period": 0,
                    "extra_duration": 0,
                    "token_amount": 1,
                    "token_origin": nft.address,
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)

            (value, secret) = first_bid_price, first_bid_secret
            first_hash = hash_bid(value, secret)
            bid_id = blind_auction.storage["next_bid_id"]()
            sleep(5)
            bob_pytezos.contract(blind_auction.address).bid(swap_id, first_hash).send(
                **send_conf
            )
            bob_pytezos.contract(blind_auction.address).revealBids(
                {
                    "swap_id": swap_id,
                    "secret": secret,
                    "bid_id": bid_id,
                    "value": value,
                    "token_symbol": "XTZ"
                }
            ).with_amount(value).send(**send_conf)

            self.assertEqual(err.exception.args[0]["with"], {"int": "228"})

        with self.assertRaises(MichelsonError) as err:
            start_time = pytezos.now() + 5
            period = 10
            blind_auction.startAuction(
                {
                    "token_id": token_id,
                    "start_time": start_time,
                    "period": period,
                    "starting_price": starting_price,
                    "reveal_time": 100,
                    "reserved_price_hashed": b"",
                    "adding_period": 0,
                    "extra_duration": 0,
                    "token_amount": 1,
                    "token_origin": nft.address,
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)

            (value, secret) = first_bid_price, first_bid_secret
            first_hash = hash_bid(value, secret)
            bid_id = blind_auction.storage["next_bid_id"]()
            sleep(5)
            bob_pytezos.contract(blind_auction.address).bid(swap_id, first_hash).send(
                **send_conf
            )
            sleep(10)
            bob_pytezos.contract(blind_auction.address).revealBids(
                {
                    "swap_id": swap_id,
                    "secret": secret,
                    "bid_id": bid_id,
                    "value": value,
                    "token_symbol": "XTZ"
                }
            ).send(**send_conf)

            self.assertEqual(err.exception.args[0]["with"], {"int": "229"})

        token_id = marketplace.storage["next_token_id"]()
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": blind_auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = blind_auction.storage["next_swap_id"]()
        start_time = pytezos.now() + 5
        period = 10
        blind_auction.startAuction(
            {
                "token_id": token_id,
                "start_time": start_time,
                "period": period,
                "starting_price": starting_price,
                "reveal_time": 100,
                "reserved_price_hashed": b"",
                "adding_period": 0,
                "extra_duration": 0,
                "token_amount": 1,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)
        (value, secret) = first_bid_price, first_bid_secret
        first_hash = hash_bid(value, secret)
        second_value = value + 10 ** 4
        second_hash = hash_bid(second_value, secret)
        bid_id = blind_auction.storage["next_bid_id"]()
        sleep(5)
        bob_pytezos.contract(blind_auction.address).bid(swap_id, first_hash).send(
            **send_conf
        )
        second_bid_id = blind_auction.storage["next_bid_id"]()
        bob_pytezos.contract(blind_auction.address).bid(swap_id, second_hash).send(
            **send_conf
        )
        sleep(10)

        bob_pytezos.contract(blind_auction.address).revealBids(
            {
                "swap_id": swap_id,
                "secret": secret,
                "bid_id": bid_id,
                "value": value,
                "token_symbol": "XTZ"
            }
        ).with_amount(value).send(**send_conf)

        bob_pytezos.contract(blind_auction.address).revealBids(
            {
                "swap_id": swap_id,
                "secret": secret,
                "bid_id": second_bid_id,
                "value": second_value,
                "token_symbol": "XTZ"
            }
        ).with_amount(second_value).send(**send_conf)

        self.assertEqual(
            blind_auction.storage["swaps"][swap_id]["auction"]["current_price"](
            ),
            second_value,
        )
        self.assertEqual(
            blind_auction.storage["swaps"][swap_id]["auction"][
                "current_highest_bidder"
            ](),
            BOB_PK,
        )

    def test_reveal_and_collect_blind_auction(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        blind_auction_init_storage = BlindAuctionStorage(ALICE_PK, ALICE_PK)
        fa12_init_storage = FA12Storage(ALICE_PK)
        (
            nft,
            foreign_nft,
            _,
            marketplace,
            blind_auction,
            normalizer,
            usd_fa12
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            blind_auction_init_storage,
            fa12_init_storage
        )
        token_id = marketplace.storage["next_token_id"]()
        starting_price = 10 ** 6
        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1

        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": blind_auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = blind_auction.storage["next_swap_id"]()
        period = 10
        reveal_time = 10
        reserved_price = starting_price + 10 ** 6
        bid_price = reserved_price + 10 ** 4
        bid_secret = "secret"
        reserved_price_secret = "secret"
        reserved_price_hashed = hash_price(
            reserved_price, reserved_price_secret)

        blind_auction.startAuction(
            {
                "token_id": token_id,
                "start_time": pytezos.now() + 5,
                "period": period,
                "starting_price": starting_price,
                "reveal_time": reveal_time,
                "reserved_price_hashed": reserved_price_hashed,
                "adding_period": 0,
                "extra_duration": 0,
                "token_amount": 1,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)

        bid_hash = hash_bid(bid_price, bid_secret)
        bid_id = blind_auction.storage["next_bid_id"]()
        sleep(5)
        bob_pytezos.contract(blind_auction.address).bid(swap_id, bid_hash).send(
            **send_conf
        )
        sleep(10)

        bob_pytezos.contract(blind_auction.address).revealBids(
            {
                "swap_id": swap_id,
                "secret": bid_secret,
                "bid_id": bid_id,
                "value": bid_price,
                "token_symbol": "XTZ"
            }
        ).with_amount(bid_price).send(**send_conf)

        blind_auction.revealPrice(
            {
                "swap_id": swap_id,
                "revealed_price": {
                    "price": reserved_price,
                    "secret": reserved_price_secret,
                },
                "permit_lower": False,
            }
        ).send(**send_conf)
        sleep(10)

        resp = blind_auction.collect(swap_id).send(
            **send_conf
        )

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]

        management_fee_rate = blind_auction.storage["management_fee_rate"]()

        fee = bid_price * (royalties + management_fee_rate) // 10000
        royalties = royalties * fee // (royalties + management_fee_rate)
        management_fee = fee - royalties
        issuer_value = bid_price - fee

        # royalties
        self.assertEqual(internal_operations[1]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[1]["amount"]), royalties)

        # management fee
        self.assertEqual(
            internal_operations[0]["destination"], blind_auction.storage["treasury"](
            )
        )
        self.assertEqual(int(internal_operations[0]["amount"]), management_fee)

        # issuer
        self.assertEqual(internal_operations[2]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[2]["amount"]), issuer_value)

        self.assertEqual(blind_auction.context.get_balance(), 0)

        token_id = 1000
        foreign_nft.mint({"token_id": token_id, "token_metadata": {},
                         "amount_": 1}).send(**send_conf)
        foreign_nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": blind_auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = blind_auction.storage["next_swap_id"]()

        blind_auction.startAuction(
            {
                "token_id": token_id,
                "start_time": pytezos.now() + 5,
                "period": period,
                "starting_price": starting_price,
                "reveal_time": 10,
                "reserved_price_hashed": reserved_price_hashed,
                "adding_period": 0,
                "extra_duration": 0,
                "token_amount": 1,
                "token_origin": foreign_nft.address,
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)

        bid_hash = hash_bid(bid_price, bid_secret)
        bid_id = blind_auction.storage["next_bid_id"]()
        sleep(5)
        bob_pytezos.contract(blind_auction.address).bid(swap_id, bid_hash).send(
            **send_conf
        )
        sleep(10)

        bob_pytezos.contract(blind_auction.address).revealBids(
            {
                "swap_id": swap_id,
                "secret": bid_secret,
                "bid_id": bid_id,
                "value": bid_price,
                "token_symbol": "XTZ"
            }
        ).with_amount(bid_price).send(**send_conf)

        blind_auction.revealPrice(
            {
                "swap_id": swap_id,
                "revealed_price": {
                    "price": reserved_price,
                    "secret": reserved_price_secret,
                },
                "permit_lower": False,
            }
        ).send(**send_conf)
        sleep(10)

        resp = blind_auction.collect(swap_id).send(
            **send_conf
        )

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]

        management_fee_rate = blind_auction.storage["management_fee_rate"]()

        management_fee = bid_price * management_fee_rate // 10000
        issuer_value = bid_price - management_fee

        # management fee
        self.assertEqual(
            internal_operations[0]["destination"], blind_auction.storage["admin"](
            )
        )
        self.assertEqual(int(internal_operations[0]["amount"]), management_fee)

        # issuer
        self.assertEqual(internal_operations[1]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[1]["amount"]), issuer_value)

        self.assertEqual(blind_auction.context.get_balance(), 0)

    def test_reveal_counter(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        blind_auction_init_storage = BlindAuctionStorage(ALICE_PK, ALICE_PK)
        fa12_init_storage = FA12Storage(ALICE_PK)
        (
            nft,
            _,
            _,
            marketplace,
            blind_auction,
            normalizer,
            usd_fa12
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            blind_auction_init_storage,
            fa12_init_storage
        )
        token_id = marketplace.storage["next_token_id"]()
        starting_price = 10 ** 6
        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1

        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": blind_auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = blind_auction.storage["next_swap_id"]()
        period = 10
        reveal_time = 100
        reserved_price = starting_price + 10 ** 6
        reserved_price_secret = "secret"
        reserved_price_hashed = hash_price(
            reserved_price, reserved_price_secret)

        blind_auction.startAuction(
            {
                "token_id": token_id,
                "start_time": pytezos.now() + 5,
                "period": period,
                "starting_price": starting_price,
                "reveal_time": reveal_time,
                "reserved_price_hashed": reserved_price_hashed,
                "adding_period": 0,
                "extra_duration": 0,
                "token_amount": 1,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "accepted_tokens": ["USD", "XTZ"]
            }
        ).send(**send_conf)
        sleep(15)
        with self.assertRaises(MichelsonError) as err:
            for _ in range(4):
                blind_auction.revealPrice(
                    {
                        "swap_id": swap_id,
                        "revealed_price": {
                            "price": reserved_price,
                            "secret": reserved_price_secret,
                        },
                        "permit_lower": False,
                    }
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "315"})
