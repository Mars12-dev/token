from time import sleep
import unittest
from dataclasses import dataclass
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

    def deploy_marketplace_app(
        self,
        nft_init_storage: FA2Storage,
        royalties_init_storage: RoyaltiesStorage,
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
        marketplace_init_storage.oracle = normalizer.address
        marketplace_init_storage.usd_address = usd_fa12.address
        marketplace_init_storage.multisig = multisig.address
        marketplace_init_storage.treasury = treasury.address
        marketplace = self.deploy_marketplace(marketplace_init_storage)
        nft_init_storage.proxy = [marketplace.address, ALICE_PK]
        nft_init_storage.multisig = multisig.address
        royalties_init_storage.proxy = [marketplace.address]
        royalties_init_storage.multisig = multisig.address
        nft = self.deploy_nft(nft_init_storage)
        foreign_nft = self.deploy_nft(nft_init_storage)
        royalties_contr = self.deploy_royalties(royalties_init_storage)
        multisig.addAuthorizedContract(marketplace.address).send(**send_conf)
        multisig.addAuthorizedContract(treasury.address).send(**send_conf)
        multisig.addAuthorizedContract(nft.address).send(**send_conf)
        multisig.addAuthorizedContract(
            royalties_contr.address).send(**send_conf)
        marketplace.updateNftAddress(nft.address).send(**send_conf)
        marketplace.updateRoyaltiesAddress(
            royalties_contr.address).send(**send_conf)

        return nft, foreign_nft, royalties_contr, marketplace, normalizer, usd_fa12, multisig, treasury


class TestMarketplace(unittest.TestCase):
    def test_multisig_admin(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )
        # Test that set_threshold follows multisig rules
        self.assertEqual(multisig.storage["threshold"](), 1)
        # Multisig threshold is 1, so 1 vote is needed to complete the operation
        # Threshold can not be set to a number larger than the number of admins
        with self.assertRaises(MichelsonError) as err:
            multisig.setThreshold(2).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1006"})
        # Bob is added as admin, and threshold is set to 2
        multisig.addAdmin(BOB_PK).send(**send_conf)
        self.assertIn(BOB_PK, multisig.storage["admins"]())
        multisig.setThreshold(2).send(**send_conf)
        self.assertEqual(multisig.storage["threshold"](), 2)
        # 2 votes are needed to add Charlie as admin
        multisig.addAdmin(CHARLIE_PK).send(**send_conf)
        self.assertNotIn(CHARLIE_PK, multisig.storage["admins"]())
        bob_pytezos.contract(multisig.address).addAdmin(
            CHARLIE_PK).send(**send_conf)
        self.assertIn(CHARLIE_PK, multisig.storage["admins"]())
        # Threshold is set to 3, 2 votes are needed
        multisig.setThreshold(3).send(**send_conf)
        self.assertEqual(multisig.storage["threshold"](), 2)
        bob_pytezos.contract(multisig.address).setThreshold(
            3).send(**send_conf)
        self.assertEqual(multisig.storage["threshold"](), 3)
        # Charlie is removed from admins
        # Number of admins has to be larger than or equal to threshold
        with self.assertRaises(MichelsonError) as err:
            multisig.removeAdmin(CHARLIE_PK).send(**send_conf)
            bob_pytezos.contract(multisig.address).removeAdmin(
                CHARLIE_PK).send(**send_conf)
            charlie_pytezos.contract(multisig.address).removeAdmin(
                CHARLIE_PK).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "1010"})
        # Threshold has to be lees than 3 so that Charlie can be removed from admins
        multisig.setThreshold(2).send(**send_conf)
        bob_pytezos.contract(multisig.address).setThreshold(
            2).send(**send_conf)
        self.assertEqual(multisig.storage["threshold"](), 3)
        charlie_pytezos.contract(
            multisig.address).setThreshold(2).send(**send_conf)
        self.assertEqual(multisig.storage["threshold"](), 2)
        multisig.removeAdmin(CHARLIE_PK).send(**send_conf)
        self.assertIn(CHARLIE_PK, multisig.storage["admins"]())
        bob_pytezos.contract(multisig.address).removeAdmin(
            CHARLIE_PK).send(**send_conf)
        self.assertNotIn(CHARLIE_PK, multisig.storage["admins"]())
        # Change voting duration
        multisig.setDuration(7200).send(**send_conf)
        self.assertEqual(multisig.storage["duration"](), 3600)
        bob_pytezos.contract(multisig.address).setDuration(
            7200).send(**send_conf)
        self.assertEqual(multisig.storage["duration"](), 7200)

        # remove and then add a contracts to multisig's authorized contracts

        multisig.removeAuthorizedContract(
            royalties_contr.address).send(**send_conf)
        self.assertIn(royalties_contr.address,
                      multisig.storage["authorized_contracts"]())
        bob_pytezos.contract(multisig.address).removeAuthorizedContract(
            royalties_contr.address).send(**send_conf)
        self.assertNotIn(royalties_contr.address,
                         multisig.storage["authorized_contracts"]())

        multisig.addAuthorizedContract(
            royalties_contr.address).send(**send_conf)
        self.assertNotIn(royalties_contr.address,
                         multisig.storage["authorized_contracts"]())
        bob_pytezos.contract(multisig.address).addAuthorizedContract(
            royalties_contr.address).send(**send_conf)
        self.assertIn(royalties_contr.address,
                      multisig.storage["authorized_contracts"]())
        # 2 votes are needed to pause marketplace
        marketplace.setPause(True).send(**send_conf)
        self.assertEqual(marketplace.storage["paused"](), False)
        bob_pytezos.contract(marketplace.address).setPause(
            True).send(**send_conf)
        self.assertEqual(marketplace.storage["paused"](), True)
        # Marketplace is unpaused by Alice and Bob
        marketplace.setPause(False).send(**send_conf)
        bob_pytezos.contract(marketplace.address).setPause(
            False).send(**send_conf)
        # Change marketplace management fee
        management_fee_rate = marketplace.storage["management_fee_rate"]()
        marketplace.updateFee(management_fee_rate + 100).send(**send_conf)
        self.assertEqual(
            marketplace.storage["management_fee_rate"](), management_fee_rate)
        bob_pytezos.contract(marketplace.address).updateFee(
            management_fee_rate + 100).send(**send_conf)
        self.assertEqual(
            marketplace.storage["management_fee_rate"](), management_fee_rate + 100)
        # Change nft address
        marketplace.updateNftAddress(foreign_nft.address).send(**send_conf)
        self.assertEqual(marketplace.storage["nft_address"](), nft.address)
        bob_pytezos.contract(marketplace.address).updateNftAddress(
            foreign_nft.address).send(**send_conf)
        self.assertEqual(
            marketplace.storage["nft_address"](), foreign_nft.address)
        # change royalties address
        marketplace.updateRoyaltiesAddress(ALICE_PK).send(**send_conf)
        self.assertEqual(
            marketplace.storage["royalties_address"](), royalties_contr.address)
        bob_pytezos.contract(marketplace.address).updateRoyaltiesAddress(
            ALICE_PK).send(**send_conf)
        self.assertEqual(
            marketplace.storage["royalties_address"](), ALICE_PK)
        # Change oracle address
        marketplace.updateOracleAddress(nft.address).send(**send_conf)
        self.assertEqual(
            marketplace.storage["oracle"](), normalizer.address)
        bob_pytezos.contract(marketplace.address).updateOracleAddress(
            nft.address).send(**send_conf)
        self.assertEqual(
            marketplace.storage["oracle"](), nft.address)
        # Add a token to allowed_tokens
        marketplace.updateAllowedTokens(
            {"token_symbol": "AHA", "direction": {"add_token": usd_fa12.address}}).send(**send_conf)
        with self.assertRaises(KeyError):
            marketplace.storage["allowed_tokens"]["AHA"]()
        with self.assertRaises(KeyError):
            marketplace.storage["available_pairs"][("AHA", "USD")]()
        bob_pytezos.contract(marketplace.address).updateAllowedTokens(
            {"token_symbol": "AHA", "direction": {"add_token": usd_fa12.address}}).send(**send_conf)
        self.assertEqual(marketplace.storage["allowed_tokens"]["AHA"](), {
                         "fa12_address": usd_fa12.address, "token_symbol": "AHA"})
        self.assertEqual(
            marketplace.storage["available_pairs"][("AHA", "USD")](), "AHA-USD")
        # remove the token
        marketplace.updateAllowedTokens(
            {"token_symbol": "AHA", "direction": {"remove_token": None}}).send(**send_conf)
        self.assertEqual(marketplace.storage["allowed_tokens"]["AHA"](), {
                         "fa12_address": usd_fa12.address, "token_symbol": "AHA"})
        self.assertEqual(
            marketplace.storage["available_pairs"][("AHA", "USD")](), "AHA-USD")
        bob_pytezos.contract(marketplace.address).updateAllowedTokens(
            {"token_symbol": "AHA", "direction": {"remove_token": None}}).send(**send_conf)
        with self.assertRaises(KeyError):
            marketplace.storage["allowed_tokens"]["AHA"]()
        with self.assertRaises(KeyError):
            marketplace.storage["available_pairs"][("AHA", "USD")]()
        # update marketplace's multisig contract.

    def test_add_to_marketplace(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            marketplace,
            _,
            _,
            _,
            _
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )

        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 100
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        price = 10 ** 6

        self.assertEqual(
            royalties_contr.storage["royalties"][token_id]["royalties"](
            ), royalties
        )

        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)
        marketplace.addToMarketplace(
            {
                "token_id": token_id,
                "swap_type": {"regular": None},
                "token_price": price,
                "start_time": pytezos.now() + 5,
                "end_time": pytezos.now() + 10,
                "token_amount": 1,
                "token_origin": nft.address,
                "recipient": {"general": None},
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)

        self.assertEqual(marketplace.storage["swaps"][0]["owner"](), ALICE_PK)
        self.assertEqual(
            marketplace.storage["swaps"][0]["token_id"](), token_id)
        self.assertEqual(
            marketplace.storage["swaps"][0]["token_price"](), price)
        self.assertEqual(nft.storage["ledger"]
                         [(marketplace.address, token_id)](), 1)
        self.assertEqual(marketplace.storage["next_swap_id"](), 1)

        with self.assertRaises(MichelsonError) as err:
            avail_token_amount = nft.storage["ledger"][(ALICE_PK, token_id)]()
            marketplace.addToMarketplace(
                {
                    "token_id": token_id,
                    "swap_type": {"regular": None},
                    "token_price": price,
                    "start_time": pytezos.now() + 5,
                    "end_time": pytezos.now() + 15,
                    "token_amount": avail_token_amount + 1,
                    "token_origin": nft.address,
                    "recipient": {"general": None},
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {
                    "string": "FA2_INSUFFICIENT_BALANCE"}
            )

        token_id = 1000

        foreign_nft.mint(
            {"token_id": token_id, "token_metadata": {}, "amount_": 1}
        ).send(**send_conf)

        foreign_nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = marketplace.storage["next_swap_id"]()
        marketplace.addToMarketplace(
            {
                "token_id": token_id,
                "swap_type": {"regular": None},
                "token_price": price,
                "start_time": pytezos.now() + 5,
                "end_time": pytezos.now() + 15,
                "token_amount": 1,
                "token_origin": foreign_nft.address,
                "recipient": {"general": None},
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)

        self.assertEqual(
            foreign_nft.storage["ledger"][(ALICE_PK, token_id)](), 0)
        self.assertEqual(
            foreign_nft.storage["ledger"][(marketplace.address, token_id)](), 1
        )

        with self.assertRaises(MichelsonError) as err:
            marketplace.removeFromMarketplace(swap_id).send(**send_conf)
            marketplace.addToMarketplace(
                {
                    "token_id": token_id,
                    "swap_type": {"regular": None},
                    "token_price": price,
                    "start_time": pytezos.now() + 5,
                    "end_time": pytezos.now() + 15,
                    "token_amount": 1,
                    "token_origin": foreign_nft.address,
                    "recipient": {"general": None},
                    "token_symbol": "AHA",
                    "accepted_tokens": ["XTZ", "USD"]
                }
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "131"})

        with self.assertRaises(MichelsonError) as err:
            marketplace.removeFromMarketplace(swap_id).send(**send_conf)
            marketplace.addToMarketplace(
                {
                    "token_id": token_id,
                    "swap_type": {"regular": None},
                    "token_price": price,
                    "start_time": pytezos.now() + 5,
                    "end_time": pytezos.now() + 15,
                    "token_amount": 1,
                    "token_origin": foreign_nft.address,
                    "recipient": {"general": None},
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "USD", "AHA"]
                }
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "135"})

        with self.assertRaises(MichelsonError) as err:
            marketplace.removeFromMarketplace(swap_id).send(**send_conf)
            marketplace.addToMarketplace(
                {
                    "token_id": token_id,
                    "swap_type": {"regular": None},
                    "token_price": price,
                    "start_time": pytezos.now() + 5,
                    "end_time": pytezos.now() + 15,
                    "token_amount": 1,
                    "token_origin": foreign_nft.address,
                    "recipient": {"general": None},
                    "token_symbol": "XTZ",
                    "accepted_tokens": ["XTZ", "AHA"]
                }
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "134"})

    def test_remove_from_marketplace(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            _,
            _,
            marketplace,
            _,
            _,
            _,
            _
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1
        price, token_id = 10 ** 6, marketplace.storage["next_token_id"]()
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)
        marketplace.addToMarketplace(
            {
                "token_id": token_id,
                "swap_type": {"regular": None},
                "token_price": price,
                "start_time": pytezos.now() + 5,
                "end_time": pytezos.now() + 15,
                "token_amount": 1,
                "token_origin": nft.address,
                "recipient": {"general": None},
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)

        swap_id = 0
        marketplace.removeFromMarketplace(swap_id).send(**send_conf)

        self.assertEqual(nft.storage["ledger"]
                         [(ALICE_PK, token_id)](), amount_)
        with self.assertRaises(KeyError):
            marketplace.storage["swaps"][swap_id]()

    def test_mint(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )
        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        self.assertEqual(nft.storage["ledger"]
                         [(ALICE_PK, token_id)](), amount_)
        self.assertEqual(
            nft.storage["token_metadata"][0](),
            {
                "token_id": 0,
                "metadata": {"": b"\x05\x01\x00\x00\x00\x12http://my_metadata"},
            },
        )

        self.assertEqual(
            royalties_contr.storage["royalties"][0](),
            {"issuer": ALICE_PK, "royalties": royalties},
        )
        self.assertEqual(marketplace.storage["next_token_id"](), 1)

    def test_update_royalties(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )
        token_id = marketplace.storage["next_token_id"]()
        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        self.assertEqual(
            royalties_contr.storage["royalties"][token_id]["royalties"](
            ), royalties
        )

        new_royalties = 300

        with self.assertRaises(MichelsonError) as err:
            bob_pytezos.contract(marketplace.address).updateRoyalties(
                {"token_id": token_id, "royalties": new_royalties}
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "33"})

        marketplace.updateRoyalties(
            {"token_id": token_id, "royalties": new_royalties}
        ).send(**send_conf)

        self.assertEqual(
            royalties_contr.storage["royalties"][token_id]["royalties"](
            ), new_royalties
        )

    def test_collect(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )
        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 1
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        price = 10 ** 6
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)
        swap_id = marketplace.storage["next_swap_id"]()
        marketplace.addToMarketplace(
            {
                "token_id": token_id,
                "swap_type": {"regular": None},
                "token_price": price,
                "start_time": pytezos.now() + 5,
                "end_time": pytezos.now() + 15,
                "token_amount": 1,
                "token_origin": nft.address,
                "recipient": {"general": None},
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)
        sleep(5)

        resp = (
            bob_pytezos.contract(marketplace.address)
            .collect({"swap_id": swap_id, "token_amount": 1, "token_symbol": "XTZ", "amount_ft": price})
            .with_amount(price)
            .send(**send_conf)
        )

        with self.assertRaises(KeyError):
            marketplace.storage["swaps"][swap_id]()

        self.assertEqual(nft.storage["ledger"][(BOB_PK, token_id)](), 1)

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]

        royalties = (
            royalties_contr.storage["royalties"][token_id]["royalties"]()
            * price
            // 10000
        )
        management_fee_rate = marketplace.storage["management_fee_rate"]()
        management_fee = management_fee_rate * price // 10000
        issuer_value = price - (royalties + management_fee)

        # royalties
        self.assertEqual(internal_operations[1]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[1]["amount"]), royalties)

        # management fee
        self.assertEqual(
            internal_operations[0]["destination"], treasury.address
        )
        self.assertEqual(int(internal_operations[0]["amount"]), management_fee)

        # issuer
        self.assertEqual(internal_operations[2]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[2]["amount"]), issuer_value)

        with self.assertRaises(MichelsonError) as err:
            marketplace.collect({"swap_id": swap_id, "token_amount": 1, "token_symbol": "XTZ", "amount_ft": price}).with_amount(
                price
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "103"})

        swap_id = marketplace.storage["next_swap_id"]()

        bob_pytezos.contract(nft.address).update_operators(
            [
                {
                    "add_operator": {
                        "owner": BOB_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        bob_pytezos.contract(marketplace.address).addToMarketplace(
            {
                "token_id": token_id,
                "swap_type": {"regular": None},
                "token_price": price,
                "start_time": pytezos.now(),
                "end_time": pytezos.now() + 10,
                "token_amount": 1,
                "token_origin": nft.address,
                "recipient": {"general": None},
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)
        sleep(5)

        with self.assertRaises(MichelsonError) as err:
            marketplace.collect({"swap_id": swap_id, "token_amount": 1, "token_symbol": "XTZ", "amount_ft": price - 1}).with_amount(
                price - 1
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int", "123"})

        token_id = 1000
        price = 10 ** 6

        foreign_nft.mint(
            {"token_id": token_id, "token_metadata": {}, "amount_": 1}
        ).send(**send_conf)

        foreign_nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = marketplace.storage["next_swap_id"]()

        marketplace.addToMarketplace(
            {
                "token_id": token_id,
                "swap_type": {"regular": None},
                "token_price": price,
                "start_time": pytezos.now(),
                "end_time": pytezos.now() + 10,
                "token_amount": 1,
                "token_origin": foreign_nft.address,
                "recipient": {"general": None},
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)
        sleep(5)

        resp = (
            bob_pytezos.contract(marketplace.address)
            .collect({"swap_id": swap_id, "token_amount": 1, "token_symbol": "XTZ", "amount_ft": price})
            .with_amount(price)
            .send(**send_conf)
        )

        self.assertEqual(
            foreign_nft.storage["ledger"][(BOB_PK, token_id)](), 1)
        self.assertEqual(
            foreign_nft.storage["ledger"][(ALICE_PK, token_id)](), 0)
        self.assertEqual(
            foreign_nft.storage["ledger"][(marketplace.address, token_id)](), 0
        )

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]

        management_fee_rate = marketplace.storage["management_fee_rate"]()
        management_fee = management_fee_rate * price // 10000
        issuer_value = price - management_fee

        # management fee
        self.assertEqual(
            internal_operations[0]["destination"], marketplace.storage["treasury"](
            )
        )
        self.assertEqual(int(internal_operations[0]["amount"]), management_fee)

        # issuer
        self.assertEqual(internal_operations[1]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[1]["amount"]), issuer_value)

        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 100
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        price = 10 ** 6
        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = marketplace.storage["next_swap_id"]()

        marketplace.addToMarketplace(
            {
                "token_id": token_id,
                "swap_type": {"regular": None},
                "token_price": price,
                "start_time": pytezos.now() + 5,
                "end_time": pytezos.now() + 100,
                "token_amount": 2,
                "token_origin": nft.address,
                "recipient": {"reserved": BOB_PK},
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)
        sleep(10)

        resp = (
            bob_pytezos.contract(marketplace.address)
            .collect({"swap_id": swap_id, "token_amount": 1, "token_symbol": "XTZ", "amount_ft": price})
            .with_amount(price)
            .send(**send_conf)
        )

        self.assertEqual(nft.storage["ledger"][(BOB_PK, token_id)](), 1)
        self.assertEqual(nft.storage["ledger"][(ALICE_PK, token_id)](), 98)
        self.assertEqual(nft.storage["ledger"]
                         [(marketplace.address, token_id)](), 1)

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]

        royalties = (
            royalties_contr.storage["royalties"][token_id]["royalties"]()
            * price
            // 10000
        )
        management_fee_rate = marketplace.storage["management_fee_rate"]()
        management_fee = management_fee_rate * price // 10000
        issuer_value = price - (royalties + management_fee)

        # royalties
        self.assertEqual(internal_operations[1]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[1]["amount"]), royalties)

        # management fee
        self.assertEqual(
            internal_operations[0]["destination"], marketplace.storage["treasury"](
            )
        )
        self.assertEqual(int(internal_operations[0]["amount"]), management_fee)

        # issuer
        self.assertEqual(internal_operations[2]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[2]["amount"]), issuer_value)

        with self.assertRaises(MichelsonError) as err:
            charlie_pytezos.contract(marketplace.address).collect(
                {"swap_id": swap_id, "token_amount": 1,
                    "token_symbol": "XTZ", "amount_ft": price}
            ).with_amount(price).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int", "128"})

        with self.assertRaises(MichelsonError) as err:
            bob_pytezos.contract(marketplace.address).collect(
                {"swap_id": swap_id, "token_amount": 1, "token_symbol": "USD", "amount_ft": price}).with_amount(price).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "133"})
        usd_fa12.mint({"value": 10 ** 10, "address": BOB_PK}).send(**send_conf)
        bob_pytezos.contract(usd_fa12.address).approve({"spender": marketplace.address,
                                                        "value": 10 ** 10}).send(**send_conf)
        seller_token = "XTZ"
        buyer_token = "USD"
        pair = marketplace.storage["available_pairs"][(
            seller_token, buyer_token)]()
        conversion_rate = normalizer.storage["assetMap"][pair]["computedPrice"](
        )
        price_usd = price * conversion_rate // 10 ** 6
        bob_pytezos.contract(marketplace.address).collect(
            {"swap_id": swap_id, "token_amount": 1, "token_symbol": buyer_token, "amount_ft": price_usd}).send(**send_conf)

    def test_update_swap(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )

        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 100
        price = 10 ** 6
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        swap_id = marketplace.storage["next_swap_id"]()

        marketplace.addToMarketplace(
            {
                "token_id": token_id,
                "swap_type": {"regular": None},
                "token_price": price,
                "start_time": pytezos.now(),
                "end_time": pytezos.now() + 4,
                "token_amount": 1,
                "token_origin": nft.address,
                "recipient": {"general": None},
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)

        new_price = price + 10 ** 6

        marketplace.updateSwap({"swap_id": swap_id, "action": {"add_amount": 7}}).send(
            **send_conf
        )

        self.assertEqual(
            marketplace.storage["swaps"][swap_id]["token_amount"](), 8)
        self.assertEqual(nft.storage["ledger"][(ALICE_PK, token_id)](), 92)
        self.assertEqual(nft.storage["ledger"]
                         [(marketplace.address, token_id)](), 8)

        marketplace.updateSwap(
            {"swap_id": swap_id, "action": {"reduce_amount": 8}}
        ).send(**send_conf)

        with self.assertRaises(KeyError):
            marketplace.storage["swaps"][swap_id]()

        swap_id = marketplace.storage["next_swap_id"]()

        marketplace.addToMarketplace(
            {
                "token_id": token_id,
                "swap_type": {"regular": None},
                "token_price": price,
                "start_time": pytezos.now(),
                "end_time": pytezos.now() + 4,
                "token_amount": 10,
                "token_origin": nft.address,
                "recipient": {"general": None},
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)

        with self.assertRaises(MichelsonError) as err:
            marketplace.updateSwap(
                {"swap_id": swap_id, "action": {"reduce_amount": 15}}
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "130"})

        with self.assertRaises(MichelsonError) as err:
            bob_pytezos.contract(marketplace.address).updateSwap(
                {"swap_id": swap_id, "action": {"reduce_amount": 10}}
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "223"})

        marketplace.updateSwap(
            {"swap_id": swap_id, "action": {"update_price": new_price}}
        ).send(**send_conf)
        self.assertEqual(
            marketplace.storage["swaps"][swap_id]["token_price"](), new_price
        )

        with self.assertRaises(MichelsonError) as err:
            marketplace.updateSwap(
                {
                    "swap_id": swap_id,
                    "action": {
                        "update_times": {
                            "start_time": pytezos.now() + 10,
                            "end_time": pytezos.now(),
                        }
                    },
                }
            ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "131"})

        start_time, end_time = pytezos.now(), pytezos.now() + 50
        marketplace.updateSwap(
            {
                "swap_id": swap_id,
                "action": {
                    "update_times": {"start_time": start_time, "end_time": end_time}
                },
            }
        ).send(**send_conf)
        self.assertEqual(
            marketplace.storage["swaps"][swap_id]["start_time"](), start_time
        )
        self.assertEqual(
            marketplace.storage["swaps"][swap_id]["end_time"](), end_time)

    def test_send_offer(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )

        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 10
        price = 10 ** 6
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        start_time, end_time = pytezos.now(), pytezos.now() + 4
        offer = price + 10 ** 4

        bob_pytezos.contract(marketplace.address).sendOffer(
            {
                "token_amount": 5,
                "token_id": token_id,
                "start_time": start_time,
                "end_time": end_time,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "ft_amount": offer
            }
        ).with_amount(offer).send(**send_conf)

        self.assertEqual(
            marketplace.storage["offers"][{
                "token_id": token_id, "buyer": BOB_PK}](),
            {
                "value": offer,
                "start_time": start_time,
                "end_time": end_time,
                "token_amount": 5,
                "origin": nft.address,
                "token_symbol": "XTZ",
            },
        )

        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 10
        marketplace.mintNft({"metadata_url": metadata_url,
                            "royalties": royalties, "amount_": amount_}).send(**send_conf)
        start_time = pytezos.now()
        end_time = start_time + 100
        ft_amount = 10 ** 6
        usd_fa12.mint({"value": ft_amount, "address": BOB_PK}
                      ).send(**send_conf)
        bob_pytezos.contract(usd_fa12.address).approve(
            {"spender": marketplace.address, "value": ft_amount}).send(**send_conf)

        with self.assertRaises(MichelsonError) as err:
            bob_pytezos.contract(marketplace.address).sendOffer({
                "token_amount": 1,
                "token_id": token_id,
                "start_time": start_time,
                "end_time": end_time,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "ft_amount": ft_amount
            }).with_amount(2 * ft_amount).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "140"})

        with self.assertRaises(MichelsonError) as err:
            bob_pytezos.contract(marketplace.address).sendOffer({
                "token_amount": 1,
                "token_id": token_id,
                "start_time": start_time,
                "end_time": end_time,
                "token_origin": nft.address,
                "token_symbol": "ETH",
                "ft_amount": ft_amount
            }).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {"int": "131"})

        bob_pytezos.contract(marketplace.address).sendOffer(
            {
                "token_amount": 1,
                "token_id": token_id,
                "start_time": start_time,
                "end_time": end_time,
                "token_origin": nft.address,
                "token_symbol": "USD",
                "ft_amount": ft_amount,
            }
        ).send(**send_conf)

        self.assertEqual(
            usd_fa12.storage["tokens"][marketplace.address](), ft_amount)

    def test_update_offer(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )
        eth_fa12 = Env().deploy_fa12(fa12_init_storage)

        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 10
        price = 10 ** 6
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        start_time, end_time = pytezos.now(), pytezos.now() + 4
        offer = price + 10 ** 4

        bob_pytezos.contract(marketplace.address).sendOffer(
            {
                "token_amount": 5,
                "token_id": token_id,
                "start_time": start_time,
                "end_time": end_time,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "ft_amount": offer
            }
        ).with_amount(offer).send(**send_conf)

        start_time, end_time = pytezos.now(), pytezos.now() + 4
        offer = offer + 10 ** 4

        bob_pytezos.contract(marketplace.address).updateOffer(
            {
                "token_amount": 5,
                "token_id": token_id,
                "start_time": start_time,
                "end_time": end_time,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "ft_amount": offer,
            }
        ).with_amount(offer).send(**send_conf)

        self.assertEqual(
            marketplace.storage["offers"][{
                "token_id": token_id, "buyer": BOB_PK}](),
            {
                "token_amount": 5,
                "value": offer,
                "start_time": start_time,
                "end_time": end_time,
                "origin": nft.address,
                "token_symbol": "XTZ",
            },
        )

        token_id = marketplace.storage["next_token_id"]()
        metadata_url, royalties, amount_ = "http://my_metadata", 100, 10

        marketplace.mintNft({"metadata_url": metadata_url,
                             "royalties": royalties, "amount_": amount_}).send(**send_conf)

        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)
        start_time = pytezos.now()
        end_time = start_time + 100
        offer = 10 ** 6
        usd_fa12.mint({
            "address": BOB_PK,
            "value": offer,
        }).send(**send_conf)

        bob_pytezos.contract(usd_fa12.address).approve({
            "spender": marketplace.address,
            "value": offer,
        }).send(**send_conf)

        self.assertEqual(usd_fa12.storage["tokens"][BOB_PK](), offer)

        bob_pytezos.contract(marketplace.address).sendOffer({
            "token_amount": 5,
            "token_id": token_id,
            "start_time": start_time,
            "end_time": end_time,
            "token_origin": nft.address,
            "token_symbol": "USD",
            "ft_amount": offer
        }).send(**send_conf)

        with self.assertRaises(KeyError):
            usd_fa12.storage["tokens"][BOB_PK]()
        self.assertEqual(
            usd_fa12.storage["tokens"][marketplace.address](), offer)

        current_balance = marketplace.context.get_balance()

        bob_pytezos.contract(marketplace.address).updateOffer({
            "token_amount": 5,
            "token_id": token_id,
            "start_time": start_time,
            "end_time": end_time,
            "token_origin": nft.address,
            "token_symbol": "XTZ",
            "ft_amount": offer,
        }).with_amount(offer).send(**send_conf)

        self.assertEqual(marketplace.context.get_balance(),
                         current_balance + offer)
        self.assertEqual(usd_fa12.storage["tokens"][BOB_PK](), offer)
        with self.assertRaises(KeyError):
            usd_fa12.storage["tokens"][marketplace.address]()

        marketplace.updateAllowedTokens({
            "direction": {"add_token": eth_fa12.address},
            "token_symbol": "ETH",
        }).send(**send_conf)
        eth_fa12.mint({
            "address": BOB_PK,
            "value": offer,
        }).send(**send_conf)

        bob_pytezos.contract(eth_fa12.address).approve({
            "spender": marketplace.address,
            "value": offer,
        }).send(**send_conf)

        bob_pytezos.contract(marketplace.address).updateOffer({
            "token_amount": 5,
            "token_id": token_id,
            "start_time": start_time,
            "end_time": end_time,
            "token_origin": nft.address,
            "token_symbol": "ETH",
            "ft_amount": offer,
        }).send(**send_conf)

        self.assertEqual(marketplace.context.get_balance(),
                         current_balance)
        self.assertEqual(
            eth_fa12.storage["tokens"][marketplace.address](), offer)
        with self.assertRaises(KeyError):
            eth_fa12.storage["tokens"][BOB_PK]()

    def test_withdraw_offer(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )

        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 10
        price = 10 ** 6
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        start_time, end_time = pytezos.now(), pytezos.now() + 4
        offer = price + 10 ** 4

        bob_pytezos.contract(marketplace.address).sendOffer(
            {
                "token_amount": 5,
                "token_id": token_id,
                "start_time": start_time,
                "end_time": end_time,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "ft_amount": offer
            }
        ).with_amount(offer).send(**send_conf)

        self.assertEqual(
            marketplace.storage["offers"][{
                "token_id": token_id, "buyer": BOB_PK, }](),
            {
                "token_amount": 5,
                "value": offer,
                "start_time": start_time,
                "end_time": end_time,
                "origin": nft.address,
                "token_symbol": "XTZ",
            },
        )

        resp = (
            bob_pytezos.contract(marketplace.address)
            .withdrawOffer(token_id)
            .send(**send_conf)
        )
        with self.assertRaises(KeyError):
            marketplace.storage["offers"][{
                "token_id": token_id, "buyer": BOB_PK}]()

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]

        self.assertEqual(internal_operations[0]["destination"], BOB_PK)
        self.assertEqual(int(internal_operations[0]["amount"]), offer)

        usd_fa12.mint({"value": 10 ** 6, "address": BOB_PK}
                      ).send(**send_conf)
        bob_pytezos.contract(usd_fa12.address).approve(
            {"spender": marketplace.address, "value": 10 ** 6}).send(**send_conf)

        bob_pytezos.contract(marketplace.address).sendOffer({
            "token_amount": 5,
            "token_id": token_id,
            "start_time": start_time,
            "end_time": end_time,
            "token_origin": nft.address,
            "token_symbol": "USD",
            "ft_amount": 10 ** 6
        }).send(**send_conf)
        self.assertEqual(
            usd_fa12.storage["tokens"][marketplace.address](), 10 ** 6)
        with self.assertRaises(KeyError):
            usd_fa12.storage["tokens"][BOB_PK]()

        bob_pytezos.contract(marketplace.address).withdrawOffer(
            token_id).send(**send_conf)

        self.assertEqual(usd_fa12.storage["tokens"][BOB_PK](), 10 ** 6)
        with self.assertRaises(KeyError):
            usd_fa12.storage["tokens"][marketplace.address]()

    def test_accept_offer(self):
        nft_init_storage = FA2Storage(ALICE_PK)
        royalties_init_storage = RoyaltiesStorage(ALICE_PK)
        marketplace_init_storage = MarketplaceStorage(ALICE_PK, ALICE_PK)
        multisig_init_storage = MultisigStorage()
        fa12_init_storage = FA12Storage(ALICE_PK)
        treasury_init_storage = TreasuryStorage()
        (
            nft,
            foreign_nft,
            royalties_contr,
            marketplace,
            normalizer,
            usd_fa12,
            multisig,
            treasury
        ) = Env().deploy_marketplace_app(
            nft_init_storage,
            royalties_init_storage,
            marketplace_init_storage,
            fa12_init_storage,
            multisig_init_storage,
            treasury_init_storage,
        )

        token_id = marketplace.storage["next_token_id"]()

        metadata_url, royalties, amount_ = "http://my_metadata", 100, 100
        price = 10 ** 6
        marketplace.mintNft(
            {"metadata_url": metadata_url, "royalties": royalties, "amount_": amount_}
        ).send(**send_conf)

        nft.update_operators(
            [
                {
                    "add_operator": {
                        "owner": ALICE_PK,
                        "operator": marketplace.address,
                        "token_id": token_id,
                    }
                }
            ]
        ).send(**send_conf)

        start_time, end_time = pytezos.now(), pytezos.now() + 10
        offer = price + 10 ** 4

        bob_pytezos.contract(marketplace.address).sendOffer(
            {
                "token_id": token_id,
                "token_amount": 10,
                "start_time": start_time,
                "end_time": end_time,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "ft_amount": offer
            }
        ).with_amount(offer).send(**send_conf)
        treasury_balance = treasury.context.get_balance()
        resp = marketplace.acceptOffer(
            {
                "token_id": token_id,
                "buyer": BOB_PK,
                "token_symbol": "XTZ"
            }
        ).send(**send_conf)

        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]

        management_fee_rate = marketplace.storage["management_fee_rate"]()
        royalties_rate = royalties_contr.storage["royalties"][token_id]["royalties"](
        )

        management_fee = offer * management_fee_rate // 10000
        royalties = royalties_rate * offer // 10000
        issuer_value = offer - (management_fee + royalties)

        # management fee is sent to treasury
        self.assertEqual(
            internal_operations[0]["destination"], treasury.address
        )
        self.assertEqual(int(internal_operations[0]["amount"]), management_fee)
        self.assertEqual(treasury.context.get_balance(),
                         treasury_balance + management_fee)

        # royalties
        self.assertEqual(internal_operations[1]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[1]["amount"]), royalties)

        # issuer
        self.assertEqual(internal_operations[2]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[2]["amount"]), issuer_value)

        # test that alice can withdraw management fee from treasury
        resp = treasury.withdraw(
            {"token": "XTZ", "withdraw_destination": [{"token_amount": management_fee, "to_": ALICE_PK}]}).send(**send_conf)
        internal_operations = resp.opg_result["contents"][0]["metadata"][
            "internal_operation_results"
        ]
        self.assertEqual(
            internal_operations[2]["destination"], ALICE_PK)
        self.assertEqual(int(internal_operations[2]["amount"]), management_fee)

        marketplace.addToMarketplace(
            {
                "token_id": token_id,
                "swap_type": {"regular": None},
                "token_price": price,
                "start_time": pytezos.now(),
                "end_time": pytezos.now() + 10,
                "token_amount": 10,
                "token_origin": nft.address,
                "recipient": {"general": None},
                "token_symbol": "XTZ",
                "accepted_tokens": ["XTZ", "USD"]
            }
        ).send(**send_conf)

        bob_pytezos.contract(marketplace.address).sendOffer(
            {
                "token_id": token_id,
                "token_amount": 30,
                "start_time": pytezos.now(),
                "end_time": pytezos.now() + 50,
                "token_origin": nft.address,
                "token_symbol": "XTZ",
                "ft_amount": 10 ** 6
            }
        ).with_amount(10 ** 6).send(**send_conf)
        sleep(5)
        marketplace.acceptOffer(
            {
                "token_id": token_id,
                "buyer": BOB_PK,
                "token_symbol": "XTZ"
            }
        ).send(**send_conf)

        usd_fa12.mint({"value": 10 ** 6, "address": BOB_PK}).send(**send_conf)
        bob_pytezos.contract(usd_fa12.address).approve(
            {"value": 10 ** 6, "spender": marketplace.address}).send(**send_conf)

        bob_pytezos.contract(marketplace.address).sendOffer(
            {
                "token_id": token_id,
                "token_amount": 30,
                "start_time": pytezos.now(),
                "end_time": pytezos.now() + 50,
                "token_origin": nft.address,
                "token_symbol": "USD",
                "ft_amount": 10 ** 6
            }
        ).with_amount(10 ** 6).send(**send_conf)
        sleep(5)
        marketplace.acceptOffer(
            {
                "token_id": token_id,
                "buyer": BOB_PK,
                "token_symbol": "USD"
            }
        ).send(**send_conf)

        management_fee = 10 ** 6 * \
            marketplace.storage["management_fee_rate"]() // 10000
        seller_value = 10 ** 6 - management_fee

        self.assertEqual(usd_fa12.storage["tokens"][ALICE_PK](), seller_value)
        self.assertEqual(
            usd_fa12.storage["tokens"][treasury.address](), management_fee)
