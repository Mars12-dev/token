import hashlib
import json
from data import normalizer_data
from time import sleep
import unittest
from dataclasses import dataclass
from pytezos import ContractInterface, pytezos
from pytezos.contract.result import OperationResult
from pytezos.michelson.parse import michelson_to_micheline
from pytezos.michelson.types import MichelsonType
from pytezos.rpc.errors import MichelsonError


# sandbox
ALICE_KEY = "edsk3EQB2zJvvGrMKzkUxhgERsy6qdDDw19TQyFWkYNUmGSxXiYm7Q"
ALICE_PK = "tz1Yigc57GHQixFwDEVzj5N1znSCU3aq15td"
CHARLIE_PK = "tz1iYCR11SMJcpAH3egtDjZRQgLgKX6agU7s"
CHARLIE_KEY = "edsk3G87qnDZhR74qYDFAC6nE17XxWkvPJtWpLw4vfeZ3otEWwwskV"
BOB_PK = "tz1RTrkJszz7MgNdeEvRLaek8CCrcvhTZTsg"
BOB_KEY = "edsk4YDWx5QixxHtEfp5gKuYDd1AZLFqQhmquFgz64mDXghYYzW6T9"

# granadanet
# shell = "https://granadanet.api.tez.ie/"

SHELL = "http://localhost:20000"

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
class AuctionStorage:
    multisig: str
    treasury: str
    nft_address: str = ALICE_PK
    royalties_address: str = ALICE_PK
    oracle: str = ALICE_PK
    xtz_address: str = ALICE_PK
    usd_address: str = ALICE_PK


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
class FA12Storage:
    admin: str


@dataclass
class TreasuryStorage:
    multisig: str = ALICE_PK


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
            "ledger": {},
            "multisig": init_storage.multisig,
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
            "admin": init_storage.admin,
            "total_supply": 0,
            "metadata": {},
            "token_metadata": {},
            "paused": False,
        }
        opg = fa12.originate(initial_storage=storage).send(**send_conf)
        fa12_addr = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        fa12 = pytezos.using(**self.using_params).contract(fa12_addr)

        return fa12

    def deploy_normalizer(self):
        with open("../michelson/normalizer.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        normalizer = ContractInterface.from_michelson(
            michelson).using(**self.using_params)
        storage = normalizer_data
        opg = normalizer.originate(initial_storage=storage).send(**send_conf)
        normalizer_addr = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        normalizer = pytezos.using(
            **self.using_params).contract(normalizer_addr)

        return normalizer

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

    def deploy_full_app(
        self,
        nft_init_storage: FA2Storage,
        royalties_init_storage: RoyaltiesStorage,
        auction_init_storage: AuctionStorage,
        marketplace_init_storage: MarketplaceStorage,
        fa12_init_storage: FA12Storage,
        multisig_init_storage: MultisigStorage,
        treasury_init_storage: TreasuryStorage,
    ):
        normalizer = self.deploy_normalizer()
        usd_fa12 = self.deploy_fa12(fa12_init_storage)
        multisig = self.deploy_multisig(multisig_init_storage)
        treasury_init_storage.multisig = multisig.address
        treasury = self.deploy_treasury(treasury_init_storage)
        auction_init_storage.oracle = normalizer.address
        auction_init_storage.usd_address = usd_fa12.address
        auction_init_storage.multisig = multisig.address
        auction_init_storage.treasury = treasury.address
        marketplace_init_storage.oracle = normalizer.address
        marketplace_init_storage.multisig = multisig.address
        marketplace_init_storage.treasury = treasury.address
        marketplace_init_storage.usd_address = usd_fa12.address
        auction = self.deploy_auction(auction_init_storage)
        marketplace = self.deploy_marketplace(marketplace_init_storage)
        nft_init_storage.proxy = [
            auction.address,
            marketplace.address,
        ]
        nft_init_storage.multisig = multisig.address
        royalties_init_storage.proxy = [
            auction.address,
            marketplace.address,
        ]
        royalties_init_storage.multisig = multisig.address
        nft = self.deploy_nft(nft_init_storage)
        foreign_nft = self.deploy_nft(nft_init_storage)
        royalties_contr = self.deploy_royalties(royalties_init_storage)
        multisig.addAuthorizedContract(marketplace.address).send(**send_conf)
        multisig.addAuthorizedContract(auction.address).send(**send_conf)
        multisig.addAuthorizedContract(treasury.address).send(**send_conf)
        multisig.addAuthorizedContract(nft.address).send(**send_conf)
        multisig.addAuthorizedContract(
            royalties_contr.address).send(**send_conf)
        auction.updateNftAddress(nft.address).send(**send_conf)
        auction.updateRoyaltiesAddress(
            royalties_contr.address).send(**send_conf)
        marketplace.updateNftAddress(nft.address).send(**send_conf)
        marketplace.updateRoyaltiesAddress(
            royalties_contr.address).send(**send_conf)

        return nft, foreign_nft, royalties_contr, auction, marketplace, normalizer, usd_fa12, multisig, treasury


def hash_price(reserved_price, secret):
    real_values = (reserved_price, secret)
    tuple_type = "(pair nat string)"
    _ty_hash_tuple = MichelsonType.match(michelson_to_micheline(tuple_type))
    tuple_bytes = _ty_hash_tuple.from_python_object(real_values).pack()
    reserved_price_hashed = hashlib.sha256(tuple_bytes).digest()
    return reserved_price_hashed


class TestAuction(unittest.TestCase):
    def test_deploy_normalizer(self):
        normalizer = Env().deploy_normalizer()
        print(normalizer.storage())

    def test_start_auction(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        auction_init_storage = AuctionStorage(ALICE_PK, ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        fa12_init_storage = FA12Storage(ALICE_PK)
        multisig_init_storage = MultisigStorage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            _,
            auction,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            auction_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage
        )
        multisig.addAuthorizedContract(foreign_nft.address).send(**send_conf)
        foreign_nft.updateProxy({"add_proxy": ALICE_PK}).send(**send_conf)
        token_id = marketplace.storage["next_token_id"]()
        swap_id = auction.storage["next_swap_id"]()
        starting_price = 10 ** 6
        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1
        period = 10

        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        start_time = pytezos.now() + 5
        token_id = marketplace.storage["next_token_id"]()
        with self.assertRaises(MichelsonError) as err:
            auction.startAuction(
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
            self.assertEqual(err.exception.args[0]["with"], {"int": "221"})

        token_id = marketplace.storage["next_token_id"]() - 1

        start_time = pytezos.now() - 10
        with self.assertRaises(MichelsonError) as err:
            auction.startAuction(
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

            self.assertEqual(err.exception.args[0]["with"], {"int": "222"})

        start_time = pytezos.now() + 5
        period = 0
        with self.assertRaises(MichelsonError) as err:
            auction.startAuction(
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
            self.assertEqual(err.exception.args[0]["with"], {"int": "223"})

        token_id = marketplace.storage["next_token_id"]()
        swap_id = auction.storage["next_swap_id"]()
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)
        period = 10
        start_time = pytezos.now() + 5
        auction.startAuction(
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

        self.assertEqual(auction.storage["next_swap_id"](), swap_id + 1)
        self.assertEqual(auction.storage["swaps"]
                         [swap_id]["owner"](), ALICE_PK)
        self.assertEqual(auction.storage["swaps"]
                         [swap_id]["token_id"](), token_id)
        self.assertEqual(auction.storage["swaps"]
                         [swap_id]["token_amount"](), 1)
        self.assertEqual(auction.storage["swaps"]
                         [swap_id]["origin"](), nft.address)
        self.assertEqual(
            auction.storage["swaps"][swap_id]["auction"](),
            {
                "current_price": starting_price,
                "current_highest_bidder": auction.address,
                "start_time": start_time,
                "end_time": start_time + period,
                "reserved_price_hashed": b"",
                "reserved_price": 0,
                "permit_lower": False,
                "reveal_time": start_time + period,
                "adding_period": 0,
                "extra_duration": 0,
                "reveal_counter": 0,
                "current_symbol": "XTZ"
            },
        )

        with self.assertRaises(MichelsonError) as err:
            extra_token_amount = nft.storage["ledger"][(
                ALICE_PK, token_id)]() + 1
            start_time = pytezos.now() + 5
            auction.startAuction(
                {
                    "token_id": token_id,
                    "start_time": start_time,
                    "period": period,
                    "starting_price": starting_price,
                    "reveal_time": 0,
                    "reserved_price_hashed": b"",
                    "adding_period": 0,
                    "extra_duration": 0,
                    "token_amount": extra_token_amount,
                    "token_origin": nft.address,
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"](
                ), {"string": "FA2_INSUFFICIENT_BALANCE"}
            )

        token_id = 1000
        foreign_nft.mint({"token_id": token_id, "token_metadata": {},
                         "amount_": 1}).send(**send_conf)

        foreign_nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)
        swap_id = auction.storage["next_swap_id"]()
        start_time = pytezos.now() + 5
        auction.startAuction({
            "token_id": token_id,
            "start_time": start_time,
            "period": period,
            "starting_price": starting_price,
            "reveal_time": 0,
            "reserved_price_hashed": b"",
            "adding_period": 0,
            "extra_duration": 0,
            "token_amount": extra_token_amount,
            "token_origin": foreign_nft.address,
            "token_symbol": "XTZ",
            "accepted_tokens": ["XTZ", "USD"]
        }).send(**send_conf)

        self.assertEqual(auction.storage["next_swap_id"](), swap_id + 1)
        self.assertEqual(auction.storage["swaps"]
                         [swap_id]["owner"](), ALICE_PK)
        self.assertEqual(auction.storage["swaps"]
                         [swap_id]["token_id"](), token_id)
        self.assertEqual(auction.storage["swaps"]
                         [swap_id]["token_amount"](), 1)
        self.assertEqual(auction.storage["swaps"]
                         [swap_id]["origin"](), foreign_nft.address)
        self.assertEqual(
            auction.storage["swaps"][swap_id]["auction"](),
            {
                "current_price": starting_price,
                "current_highest_bidder": auction.address,
                "current_symbol": "XTZ",
                "start_time": start_time,
                "end_time": start_time + period,
                "reserved_price_hashed": b"",
                "reserved_price": 0,
                "permit_lower": False,
                "reveal_time": start_time + period,
                "adding_period": 0,
                "extra_duration": 0,
                "reveal_counter": 0,
            },
        )

    def test_bid(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        auction_init_storage = AuctionStorage(ALICE_PK, ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        fa12_init_storage = FA12Storage(ALICE_PK)
        multisig_init_storage = MultisigStorage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            _,
            auction,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            auction_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage
        )
        token_id = marketplace.storage["next_token_id"]()
        swap_id = auction.storage["next_swap_id"]()
        starting_price = 10 ** 6
        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1
        period = 10

        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        with self.assertRaises(MichelsonError) as err:
            start_time = pytezos.now() + 5
            auction.startAuction(
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
            print("sleep 5 seconds")
            sleep(5)
            swap_id = auction.storage["next_swap_id"]()
            auction.bid({"swap_id": swap_id, "token_symbol": "XTZ",
                        "ft_amount": 0}).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "213"})

        with self.assertRaises(MichelsonError) as err:
            swap_id = auction.storage["next_swap_id"]()
            start_time = pytezos.now() + 5
            auction.startAuction(
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
            print("sleep 5 seconds")
            sleep(5)
            auction.bid({"swap_id": swap_id, "token_symbol": "XTZ", "ft_amount": starting_price - 1}).with_amount(
                starting_price - 1).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "225"})

        with self.assertRaises(MichelsonError) as err:
            swap_id = auction.storage["next_swap_id"]()
            start_time = pytezos.now() + 100
            auction.startAuction(
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
            auction.bid({"swap_id": swap_id, "token_symbol": "XTZ", "ft_amount": starting_price + 1}).with_amount(
                starting_price + 1).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "226"})

        token_id = marketplace.storage["next_token_id"]()
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = auction.storage["next_swap_id"]()
        start_time = pytezos.now() + 5
        period = 100
        auction.startAuction(
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
        print("sleep 5 seconds")
        sleep(5)
        bob_pytezos.contract(auction.address).bid({"swap_id": swap_id, "token_symbol": "XTZ", "ft_amount": starting_price + 1}).with_amount(
            starting_price + 1
        ).send(**send_conf)

        self.assertEqual(
            auction.storage["swaps"][swap_id]["auction"]["current_price"](),
            starting_price + 1,
        )
        self.assertEqual(
            auction.storage["swaps"][swap_id]["auction"]["current_highest_bidder"](),
            BOB_PK,
        )
        self.assertEqual(auction.context.get_balance(), starting_price + 1)

        bob_pytezos.contract(auction.address).bid({"swap_id": swap_id, "token_symbol": "XTZ", "ft_amount": starting_price + 100}).with_amount(
            starting_price + 100
        ).send(**send_conf)

        self.assertEqual(
            auction.storage["swaps"][swap_id]["auction"]["current_price"](),
            starting_price + 100,
        )
        self.assertEqual(
            auction.storage["swaps"][swap_id]["auction"]["current_highest_bidder"](),
            BOB_PK,
        )
        self.assertEqual(auction.context.get_balance(), starting_price + 100)

        token_id = marketplace.storage["next_token_id"]()
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = auction.storage["next_swap_id"]()
        start_time = pytezos.now() + 5
        period = 100
        auction.startAuction(
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
        print("sleep 5 seconds")
        sleep(5)
        bob_pytezos.contract(auction.address).bid({"swap_id": swap_id, "token_symbol": "XTZ", "ft_amount": starting_price + 1}).with_amount(
            starting_price + 1
        ).send(**send_conf)

        usd_fa12.mint({"value": starting_price * 10,
                      "address": CHARLIE_PK}).send(**send_conf)
        charlie_pytezos.contract(usd_fa12.address).approve(
            {"value": starting_price * 10, "spender": auction.address}).send(**send_conf)

        with self.assertRaises(MichelsonError) as err:
            charlie_pytezos.contract(auction.address).bid(
                {"swap_id": swap_id, "token_symbol": "USD", "ft_amount": starting_price + 10}).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "209"})
        charlie_pytezos.contract(auction.address).bid({
            "swap_id": swap_id, "token_symbol": "USD", "ft_amount": starting_price * 10
        }).send(**send_conf)

        self.assertEqual(
            usd_fa12.storage["tokens"][auction.address](), starting_price * 10)
        self.assertEqual(
            auction.storage["swaps"][swap_id]["auction"]["current_highest_bidder"](), CHARLIE_PK)
        self.assertEqual(
            auction.storage["swaps"][swap_id]["auction"]["current_price"](), starting_price * 10)
        self.assertEqual(auction.storage["swaps"]
                         [swap_id]["auction"]["current_symbol"](), "USD")
        with self.assertRaises(KeyError):
            usd_fa12.storage["tokens"][CHARLIE_PK]()

    def test_reveal_price(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        auction_init_storage = AuctionStorage(ALICE_PK, ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        fa12_init_storage = FA12Storage(ALICE_PK)
        multisig_init_storage = MultisigStorage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            _,
            auction,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            auction_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage
        )
        token_id = marketplace.storage["next_token_id"]()
        price = 10 ** 6
        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1
        period = 10
        reserved_price = 2 * 10 ** 6
        secret = "secret"
        reserved_price_hashed = hash_price(reserved_price, secret)

        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = auction.storage["next_swap_id"]()
        start_time = pytezos.now() + 5

        auction.startAuction(
            {
                "token_id": token_id,
                "start_time": start_time,
                "period": period,
                "starting_price": price,
                "reveal_time": 50,
                "reserved_price_hashed": reserved_price_hashed,
                "adding_period": 0,
                "extra_duration": 0,
                "token_amount": 1,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)
        print("sleep 20 seconds")
        sleep(20)
        auction.revealPrice(
            {
                "swap_id": swap_id,
                "permit_lower": True,
                "revealed_price": {"secret": secret, "price": reserved_price, "token_symbol": "XTZ"}
            }
        ).send(**send_conf)

        self.assertEqual(
            auction.storage["swaps"][swap_id]["auction"]["reserved_price"](),
            reserved_price,
        )
        self.assertEqual(
            auction.storage["swaps"][swap_id]["auction"]["permit_lower"](), True
        )

        with self.assertRaises(MichelsonError) as err:
            auction.removeFromMarketplace(swap_id).send(**send_conf)
            swap_id = auction.storage["next_swap_id"]()
            start_time = pytezos.now() + 5
            auction.startAuction(
                {
                    "token_id": token_id,
                    "start_time": start_time,
                    "period": period,
                    "starting_price": price,
                    "reveal_time": 50,
                    "reserved_price_hashed": reserved_price_hashed,
                    "adding_period": 0,
                    "extra_duration": 0,
                    "token_amount": 1,
                    "token_origin": nft.address,
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)
            fake_secret = "fake secret"
            print("sleep 5 seconds")
            sleep(5)
            auction.revealPrice(
                {
                    "swap_id": swap_id,
                    "permit_lower": True,
                    "revealed_price": {"secret": fake_secret, "price": reserved_price, "token_symbol": "XTZ"}
                }
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "225"})

        with self.assertRaises(MichelsonError) as err:
            auction.removeFromMarketplace(swap_id).send(**send_conf)
            period = 100
            start_time = pytezos.now() + 5
            swap_id = auction.storage["next_swap_id"]()
            auction.startAuction(
                {
                    "token_id": token_id,
                    "start_time": start_time,
                    "period": period,
                    "starting_price": price,
                    "reveal_time": 50,
                    "reserved_price_hashed": reserved_price_hashed,
                    "adding_period": 0,
                    "extra_duration": 0,
                    "token_amount": 1,
                    "token_origin": nft.address,
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)
            print("sleep 5 seconds")
            sleep(5)
            auction.revealPrice(
                {
                    "swap_id": swap_id,
                    "permit_lower": True,
                    "revealed_price": {"secret": secret, "price": reserved_price, "token_symbol": "XTZ"}
                }
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": 215})

        with self.assertRaises(MichelsonError) as err:
            auction.removeFromMarketplace(swap_id).send(**send_conf)
            period = 0
            start_time = pytezos.now() + 5
            swap_id = auction.storage["next_swap_id"]()
            auction.startAuction(
                {
                    "token_id": token_id,
                    "start_time": start_time,
                    "period": period,
                    "starting_price": price,
                    "reveal_time": 0,
                    "reserved_price_hashed": reserved_price_hashed,
                    "adding_period": 0,
                    "extra_duration": 0,
                    "token_amount": 1,
                    "token_origin": nft.address,
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)
            print("sleep 5 seconds")
            sleep(5)
            auction.revealPrice(
                {
                    "swap_id": swap_id,
                    "permit_lower": True,
                    "revealed_price": {"secret": secret, "price": reserved_price, "token_symbol": "XTZ"}
                }
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": 215})

        with self.assertRaises(MichelsonError) as err:
            period = 2
            start_time = pytezos.now() + 5
            swap_id = auction.storage["next_swap_id"]()
            auction.startAuction(
                {
                    "token_id": token_id,
                    "start_time": start_time,
                    "period": period,
                    "starting_price": price,
                    "reveal_time": 0,
                    "reserved_price_hashed": reserved_price_hashed,
                    "adding_period": 100,
                    "extra_duration": 0,
                    "token_amount": 1,
                    "token_origin": nft.address,
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)
            print("sleep 5 seconds")
            sleep(5)
            bob_pytezos.contract(auction.address).revealPrice(
                {
                    "swap_id": swap_id,
                    "permit_lower": True,
                    "revealed_price": {"secret": secret, "price": reserved_price, "token_symbol": "XTZ"}
                }
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": 223})
        print(f"reserved_price_hashed = {reserved_price_hashed}")

    def test_auction_collect(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        auction_init_storage = AuctionStorage(ALICE_PK, ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        fa12_init_storage = FA12Storage(ALICE_PK)
        multisig_init_storage = MultisigStorage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            auction,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            auction_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage
        )
        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = auction.storage["next_swap_id"]()
        starting_price = 10 ** 6
        period = 10
        amount = starting_price + 10 ** 4

        with self.assertRaises(MichelsonError) as err:
            start_time = pytezos.now() + 5
            auction.startAuction(
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
            print("sleep 5 seconds")
            sleep(5)
            auction.bid({"swap_id": swap_id, "token_symbol": "XTZ",
                        "ft_amount": amount}).with_amount(amount).send(**send_conf)
            print("sleep 10 seconds")
            sleep(10)
            auction.collect(swap_id).with_amount(
                amount
            ).send(**send_conf)

            self.assertEqual(err.exception.args[0]["with"], {"int": "231"})

        with self.assertRaises(MichelsonError) as err:
            start_time = pytezos.now() + 5
            auction.startAuction(
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
            print("sleep 5 seconds")
            sleep(5)
            auction.bid({"swap_id": swap_id, "token_symbol": "XTZ",
                        "ft_amount": amount}).with_amount(amount).send(**send_conf)
            auction.collect(swap_id).send(**send_conf)

            self.assertEqual(err.exception.args[0]["with"], {"int": "230"})

        token_id = marketplace.storage["next_token_id"]()
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        start_time = pytezos.now() + 5
        swap_id = auction.storage["next_swap_id"]()
        period = 10

        auction.startAuction(
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
        print("sleep 5 seconds")
        sleep(5)
        bob_pytezos.contract(auction.address).bid({"swap_id": swap_id, "token_symbol": "XTZ", "ft_amount": amount}).with_amount(amount).send(
            **send_conf
        )

        print("sleep 10 seconds")
        sleep(10)
        resp = (
            bob_pytezos.contract(auction.address)
            .collect(swap_id)
            .send(**send_conf)
        )

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]

        management_fee_rate = auction.storage["management_fee_rate"]()

        fee = amount * (royalties + management_fee_rate) // 10000
        royalties = (
            royalties_contr.storage["royalties"][token_id]["royalties"]()
            * amount
            // 10000
        )
        management_fee = amount * management_fee_rate // 10000
        issuer_value = amount - (royalties + management_fee)

        # royalties
        self.assertEqual(internal_operations[1]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[1]["amount"]), royalties)

        # management fee
        self.assertEqual(
            internal_operations[0]["destination"], auction.storage["treasury"]()
        )
        self.assertEqual(int(internal_operations[0]["amount"]), management_fee)

        # issuer
        self.assertEqual(internal_operations[2]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[2]["amount"]), issuer_value)
        (
            nft,
            foreign_nft,
            _,
            auction,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            auction_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage
        )

        multisig.addAuthorizedContract(foreign_nft.address).send(**send_conf)
        foreign_nft.updateProxy({"add_proxy": ALICE_PK}).send(**send_conf)
        token_id = marketplace.storage["next_token_id"]()
        royalties = 1000
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = auction.storage["next_swap_id"]()
        period = 10
        starting_price = 10 ** 6
        reveal_time = 10
        reserved_price = starting_price + 10 ** 6
        reserved_price_secret = "secret"
        reserved_price_hashed = hash_price(
            reserved_price, reserved_price_secret)
        amount = reserved_price + 10 ** 4

        start_time = pytezos.now() + 5

        auction.startAuction(
            {
                "token_id": token_id,
                "start_time": start_time,
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
        print("sleep 5 seconds")
        sleep(5)

        bob_pytezos.contract(auction.address).bid({"swap_id": swap_id, "token_symbol": "XTZ", "ft_amount": amount}).with_amount(amount).send(
            **send_conf
        )
        print("sleep 10 seconds")
        sleep(10)
        auction.revealPrice(
            {
                "swap_id": swap_id,
                "revealed_price": {
                    "price": reserved_price,
                    "secret": reserved_price_secret,
                    "token_symbol": "XTZ",
                },
                "permit_lower": False,
            }
        ).send(**send_conf)
        print("sleep 10 seconds")
        sleep(10)

        resp = (
            bob_pytezos.contract(auction.address)
            .collect(swap_id)
            .send(**send_conf)
        )

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]

        management_fee_rate = auction.storage["management_fee_rate"]()

        fee = amount * (royalties + management_fee_rate) // 10000
        royalties = royalties * fee // (royalties + management_fee_rate)
        management_fee = fee - royalties
        issuer_value = amount - fee

        # royalties
        self.assertEqual(internal_operations[1]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[1]["amount"]), royalties)

        # management fee
        self.assertEqual(
            internal_operations[0]["destination"], auction.storage["treasury"]()
        )
        self.assertEqual(int(internal_operations[0]["amount"]), management_fee)

        # issuer
        self.assertEqual(internal_operations[2]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[2]["amount"]), issuer_value)

        token_id = 1000

        foreign_nft.mint({"token_id": token_id, "token_metadata": {},
                         "amount_": 1}).send(**send_conf)

        foreign_nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)
        swap_id = auction.storage["next_swap_id"]()
        starting_price = 10 ** 5
        period = 10

        start_time = pytezos.now() + 5
        auction.startAuction({
            "token_id": token_id,
            "start_time": start_time,
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
        }).send(**send_conf)
        amount = 10 ** 6
        print("sleep 5 seconds")
        sleep(5)

        bob_pytezos.contract(auction.address).bid({"swap_id": swap_id, "token_symbol": "XTZ", "ft_amount": amount}).with_amount(amount).send(
            **send_conf
        )
        print("sleep 10 seconds")
        sleep(10)

        resp = (
            bob_pytezos.contract(auction.address)
            .collect(swap_id)
            .send(**send_conf)
        )

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]

        management_fee_rate = auction.storage["management_fee_rate"]()

        management_fee = amount * (management_fee_rate) // 10000
        issuer_value = amount - management_fee

        # management fee
        self.assertEqual(
            internal_operations[0]["destination"], auction.storage["treasury"]()
        )
        self.assertEqual(int(internal_operations[0]["amount"]), management_fee)

        # issuer
        self.assertEqual(internal_operations[1]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[1]["amount"]), issuer_value)

    def test_remove_from_marketplace(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        auction_init_storage = AuctionStorage(ALICE_PK, ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        fa12_init_storage = FA12Storage(ALICE_PK)
        multisig_init_storage = MultisigStorage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            _,
            auction,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            auction_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage
        )

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 100
        starting_price, token_id = 10 ** 6, marketplace.storage["next_token_id"](
        )
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)
        start_time = pytezos.now() + 5
        period = 10
        reveal_time = 0
        swap_id = auction.storage["next_swap_id"]()

        auction.startAuction(
            {
                "token_id": token_id,
                "start_time": start_time,
                "period": period,
                "starting_price": starting_price,
                "reveal_time": reveal_time,
                "reserved_price_hashed": b"",
                "adding_period": 0,
                "extra_duration": 0,
                "token_amount": 1,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)

        auction.removeFromMarketplace(swap_id).send(**send_conf)

        self.assertEqual(nft.storage["ledger"]
                         [(ALICE_PK, token_id)](), amount_)
        with self.assertRaises(KeyError):
            auction.storage["swaps"][swap_id]()
        with self.assertRaises(KeyError):
            auction.storage["tokens"][(token_id, ALICE_PK)]()

        with self.assertRaises(MichelsonError) as err:
            swap_id = auction.storage["next_swap_id"]()
            period = 10
            start_time = pytezos.now() + 5

            auction.startAuction(
                {
                    "token_id": token_id,
                    "start_time": start_time,
                    "period": period,
                    "starting_price": starting_price,
                    "reveal_time": reveal_time,
                    "reserved_price_hashed": b"",
                    "adding_period": 0,
                    "extra_duration": 0,
                    "token_amount": 1,
                    "token_origin": nft.address,
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)
            print("sleep 5 seconds")
            sleep(5)
            bob_pytezos.contract(auction.address).bid({"swap_id": swap_id, "token_symbol": "XTZ", "ft_amount": starting_price + 10 ** 4}).with_amount(
                starting_price + 10 ** 4
            ).send(**send_conf)
            auction.removeFromMarketplace(swap_id).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "226"})

        with self.assertRaises(MichelsonError) as err:
            swap_id = auction.storage["next_swap_id"]()
            period = 10
            start_time = pytezos.now() + 5

            auction.startAuction(
                {
                    "token_id": token_id,
                    "start_time": start_time,
                    "period": period,
                    "starting_price": starting_price,
                    "reveal_time": reveal_time,
                    "reserved_price_hashed": b"",
                    "adding_period": 0,
                    "extra_duration": 0,
                    "token_amount": 1,
                    "token_origin": nft.address,
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)
            bob_pytezos.contract(auction.address).removeFromMarketplace(swap_id).send(
                **send_conf
            )
            self.assertEqual(err.exception.args[0]["with"], {"int": "232"})

    # def test_update_admin(self):
    #     auction_init_storage = AuctionStorage(ALICE_PK)
    #     auction = Env().deploy_auction(auction_init_storage)

    #     with self.assertRaises(MichelsonError) as err:
    #         bob_pytezos.contract(auction.address).updateMarketplaceAdmin(BOB_PK).send(
    #             **send_conf
    #         )
    #         self.assertEqual(err.exception.args[0]["with"], {"int": "220"})

    #     auction.updateMarketplaceAdmin(BOB_PK).send(**send_conf)

    #     self.assertEqual(auction.storage["admin"](), BOB_PK)

    # def test_update_fee(self):
    #     auction_init_storage = AuctionStorage(ALICE_PK)
    #     auction = Env().deploy_auction(auction_init_storage)
    #     new_fee = 10

    #     with self.assertRaises(MichelsonError) as err:
    #         bob_pytezos.contract(auction.address).updateFee(
    #             new_fee).send(**send_conf)
    #         self.assertEqual(err.exception.args[0]["with"], {"int": "220"})

    #     auction.updateFee(new_fee).send(**send_conf)

    #     self.assertEqual(auction.storage["management_fee_rate"](), new_fee)

    def test_reveal_counter(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        auction_init_storage = AuctionStorage(ALICE_PK, ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        fa12_init_storage = FA12Storage(ALICE_PK)
        multisig_init_storage = MultisigStorage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            _,
            auction,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_full_app(
            nft_init_storage,
            royalties_init_storage,
            auction_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage
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
                        "operator": auction.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = auction.storage["next_swap_id"]()
        period = 10
        reveal_time = 10
        reserved_price = starting_price + 10 ** 6
        reserved_price_secret = "secret"
        reserved_price_hashed = hash_price(
            reserved_price, reserved_price_secret)

        auction.startAuction(
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
        print("sleep 15 seconds")
        sleep(15)
        with self.assertRaises(MichelsonError) as err:
            for _ in range(4):
                auction.revealPrice({"swap_id": swap_id,
                                     "revealed_price": {
                                         "price": reserved_price,
                                         "secret": reserved_price_secret,
                                         "token_symbol": "XTZ",
                                     },
                                     "permit_lower": False,
                                     }
                                    ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "216"})
