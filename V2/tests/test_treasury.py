from time import sleep
import unittest
from dataclasses import dataclass
from pytezos import ContractInterface, pytezos
from pytezos.contract.result import OperationResult
from pytezos.rpc.errors import MichelsonError


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
    admin: str
    proxy: str = ALICE_PK


@dataclass
class RoyaltiesStorage:
    admin: str
    proxy: str = ALICE_PK


@dataclass
class MarketplaceStorage:
    admin: str
    multisig: str
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
    multisig: str


normalizer_data = {
    "assetCodes": [
        "BAT-USDC",
        "BTC-USD",
        "COMP-USD",
        "DAI-USDC",
        "ETH-USD",
        "KNC-USD",
        "LINK-USD",
        "REP-USD",
        "XTZ-USD",
        "ZRX-USD",
        "USD_XTZ"
    ],
    "assetMap": {
        "ETH-USD": {
            "computedPrice": 3316384738,
            "lastUpdateTime": "2022-01-15T00:00:00Z",
            "prices": {
                "first": 6120,
                "last": 6125,
                "saved": {
                    6120: 194549700637710000,
                    6121: 116233511630250000,
                    6122: 77621893928204232,
                    6123: 82456292492700000,
                    6124: 440368278949620000,
                    6125: 559931065398780000},
                "sum": 1471160743037264232
            },
            "volumes": {
                "first": 6120,
                "last": 6125,
                "saved": {
                    6120: 58741029,
                    6121: 35116395,
                    6122: 23453652,
                    6123: 23453652,
                    6124: 23453652,
                    6125: 23453652,
                },
                "sum": 23453652
            }
        },
        "DAI-USDC": {
            "computedPrice": 999925,
            "lastUpdateTime": "2022-01-14T23:50:00Z",
            "prices": {
                "first": 1171,
                "last": 1176,
                "saved": {
                    1171: 4999595000000000,
                    1172: 1389186422514000,
                    1173: 119832113635500,
                    1174: 1027278426700,
                    1175: 2697079681000,
                    1176: 1154741999110,
                },
                "sum": 6513492636256310
            },
            "volumes": {
                "first": 1171,
                "last": 1176,
                "saved": {
                    1171: 5000000000,
                    1172: 1389267000,
                    1173: 119834750,
                    1174: 1027300,
                    1175: 2696810,
                    1176: 1154630,
                },
                "sum": 6513980490
            }
        },
        "XTZ-USD": {
            "computedPrice": 4290954,
            "lastUpdateTime": "2022-01-15T00:00:00Z",
            "prices": {
                "first": 6083,
                "last": 6088,
                "saved": {
                    6083: 3005273700000000,
                    6084: 654482400000000,
                    6085: 396807969120000,
                    6086: 1144496955340000,
                    6087: 3974896491390000,
                    6088: 837199935000000,
                },
                "sum": 10013157450850000
            },
            "volumes": {
                "first": 6083,
                "last": 6088,
                "saved": {
                    6083: 700530000,
                    6084: 152560000,
                    6085: 92640000,
                    6086: 266990000,
                    6087: 925830000,
                    6088: 195000000,
                },
                "sum": 2333550000
            }
        },
        "ZRX-USD": {
            "computedPrice": 749282,
            "lastUpdateTime": "2022-01-15T00:00:00Z",
            "prices": {
                "first": 5838,
                "last": 5843,
                "saved": {
                    5838: 22154877858080,
                    5839: 356519775771280,
                    5840: 3184437571724277,
                    5841: 6598126578808450,
                    5842: 2212488502853130,
                    5843: 2450255117240280,
                },
                "sum": 14823982424255497
            },
            "volumes": {
                "first": 5838,
                "last": 5843,
                "saved": {
                    5838: 29550160,
                    5839: 476028680,
                    5840: 4255830009,
                    5841: 8812318550,
                    5842: 2950232490,
                    5843: 3260277610,
                },
                "sum": 19784237499
            }
        },
        "LINK-USD": {
            "computedPrice": 25761710,
            "lastUpdateTime": "2022-01-15T00:00:00Z",
            "prices": {
                "first": 6112,
                "last": 6117,
                "saved": {
                    6112: 30874997668760000,
                    6113: 271896859640000,
                    6114: 52965947474250000,
                    6115: 60982435800000000,
                    6116: 181650872633440000,
                    6117: 24272617600000000,
                },
                "sum": 351018768036090000
            },
            "volumes": {
                "first": 6112,
                "last": 6117,
                "saved": {
                    6112: 1196860000,
                    6113: 10540000,
                    6114: 2056929999,
                    6115: 2369170000,
                    6116: 7049840000,
                    6117: 942260000,
                },
                "sum": 13625599999
            }
        },
        "BTC-USD": {
            "computedPrice": 43131197182,
            "lastUpdateTime": "2022-01-15T00:00:00Z",
            "prices": {
                "first": 6119,
                "last": 6124,
                "saved": {
                    6119: 168213797244570000,
                    6120: 130266880317080000,
                    6121: 79459106962620000,
                    6122: 106367856715177200,
                    6123: 874226347639768218,
                    6124: 533117550780233073,
                },
                "sum": 1891651539659448491
            },
            "volumes": {
                "first": 6119,
                "last": 6124,
                "saved": {
                    6119: 3903933,
                    6120: 3023332,
                    6121: 1843962,
                    6122: 2468400,
                    6123: 20267673,
                    6124: 12350781,
                },
                "sum": 43858081
            }
        },
        "REP-USD": {
            "computedPrice": 16944411,
            "lastUpdateTime": "2022-01-14T23:58:00Z",
            "prices": {
                "first": 2319,
                "last": 2324,
                "saved": {
                    2319: 319004893990000,
                    2320: 7702772338556779,
                    2321: 42999994510000,
                    2322: 35249834490000,
                    2323: 5985816800000,
                    2324: 844500000000,
                },
                "sum": 8106857378346779
            },
            "volumes": {
                "first": 2319,
                "last": 2324,
                "saved": {
                    2319: 18798167,
                    2320: 454619663,
                    2321: 2533883,
                    2322: 2082093,
                    2323: 354610,
                    2324: 50000,
                },
                "sum": 478438416
            }
        },
        "BAT-USDC": {
            "computedPrice": 1055751,
            "lastUpdateTime": "2022-01-14T23:53:00Z",
            "prices": {
                "first": 3941,
                "last": 3946,
                "saved": {
                    3941: 164029788000000,
                    3942: 44214828000000,
                    3943: 42259000000000,
                    3944: 903429765000000,
                    3945: 2111932000000,
                    3946: 1058726000000,
                },
                "sum": 1157104039000000
            },
            "volumes": {
                "first": 3941,
                "last": 3946,
                "saved": {
                    3941: 156000000,
                    3942: 42000000,
                    3943: 40000000,
                    3944: 855000000,
                    3945: 2000000,
                    3946: 1000000,
                },
                "sum": 1096000000
            }
        },
        "COMP-USD": {
            "computedPrice": 190298244,
            "lastUpdateTime": "2022-01-15T00:00:00Z",
            "prices": {
                "first": 5803,
                "last": 5808,
                "saved": {
                    5803: 2578676970000000,
                    5804: 15970359972000,
                    5805: 7434157200000000,
                    5806: 12750100000000,
                    5807: 1741251257246000,
                    5808: 530251724814000,
                },
                "sum": 12313057612032000
            },
            "volumes": {
                "first": 5803,
                "last": 5808,
                "saved": {
                    5803: 13557000,
                    5804: 84000,
                    5805: 39086000,
                    5806: 67000,
                    5807: 9131000,
                    5808: 2779000,
                },
                "sum": 64704000
            }
        },
        "KNC-USD": {
            "computedPrice": 1421748,
            "lastUpdateTime": "2022-01-15T00:00:00Z",
            "prices": {
                "first": 4350,
                "last": 4355,
                "saved": {
                    4350: 50484548100000,
                    4351: 54547200000000,
                    4352: 576174950000000,
                    4353: 168447580000000,
                    4354: 14543246337400000,
                    4355: 30560294520000000,
                },
                "sum": 45953195135500000
            },
            "volumes": {
                "first": 4350,
                "last": 4355,
                "saved": {
                    4350: 35700000,
                    4351: 38400000,
                    4352: 405500000,
                    4353: 118600000,
                    4354: 10227800000,
                    4355: 21495600000,
                },
                "sum": 32321600000
            }
        },
    },
    "numDataPoints": 6,
    "oracleContract": "KT19yapgDLPR3CuvK32xJHgxNJigyNxjSr4y"
}


class Env:
    def __init__(self, using_params=None):
        self.using_params = using_params or _using_params

    def deploy_treasury(self):
        with open("../michelson/treasury.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        treasury = ContractInterface.from_michelson(
            michelson).using(**self.using_params)

        storage = {
            "admins": {ALICE_PK, BOB_PK},
            "multisig": ALICE_PK,
            "ledger": {},
        }
        opg = treasury.originate(initial_storage=storage).send(**send_conf)
        treasury_addr = OperationResult.from_operation_group(
            opg.opg_result)[0].originated_contracts[0]
        treasury = pytezos.using(**self.using_params).contract(treasury_addr)

        return treasury

    def deploy_multisig(self, init_storage: MultisigStorage):
        with open("../michelson/multisig.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()

        multisig = ContractInterface.from_michelson(
            michelson).using(**self.using_params)

        storage = {
            "admins": init_storage.admins,
            "n_calls": {},
            "threshold": 2,
            "duration": 3600,
            "authorized_contracts": init_storage.authorized_contracts,
        }
        opg = multisig.originate(initial_storage=storage).send(**send_conf)
        multisig_addr = OperationResult.from_operation_group(opg.opg_result)[
            0
        ].originated_contracts[0]
        multisig = pytezos.using(**self.using_params).contract(multisig_addr)

        return multisig

    def deploy_nft(self, init_storage: FA2Storage):
        with open("../michelson/nft.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()

        fa2 = ContractInterface.from_michelson(
            michelson).using(**self.using_params)
        storage = {
            "admin": {init_storage.admin},
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
            "admin": {init_storage.admin},
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
        multisig = self.deploy_multisig()

        with open("../michelson/marketplace.tz", encoding="UTF-8") as mich_file:
            michelson = mich_file.read()
        marketplace = ContractInterface.from_michelson(michelson).using(
            **self.using_params
        )
        storage = {
            "multisig": init_storage.multisig,
            "admin": {init_storage.admin},
            "nft_address": init_storage.nft_address,
            "royalties_address": init_storage.royalties_address,
            "next_token_id": 0,
            "next_swap_id": 0,
            "tokens": {},
            "swaps": {},
            "offers": {},
            "management_fee_rate": 250,
            "paused": False,
            "allowed_tokens": {
                0: {
                    "symbol": 0,
                    "name": "XTZ",
                    "fa12_address": init_storage.xtz_address,
                },
                1: {
                    "symbol": 1,
                    "name": "USD",
                    "fa12_address": init_storage.usd_address,
                },
            },
            "available_pairs": {
                (0, 1): "XTZ-USD",
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
    ):
        normalizer = self.deploy_normalizer()
        usd_fa12 = self.deploy_fa12(fa12_init_storage)
        multisig = self.deploy_multisig(multisig_init_storage)
        marketplace_init_storage.oracle = normalizer.address
        marketplace_init_storage.usd_address = usd_fa12.address
        marketplace_init_storage.multisig = multisig.address
        marketplace = self.deploy_marketplace(marketplace_init_storage)
        treasury = self.deploy_treasury()
        nft_init_storage.proxy = [marketplace.address, ALICE_PK]
        royalties_init_storage.proxy = [marketplace.address]
        nft = self.deploy_nft(nft_init_storage)
        foreign_nft = self.deploy_nft(nft_init_storage)
        royalties_contr = self.deploy_royalties(royalties_init_storage)
        marketplace.admin(
            {"update_nft_address": nft.address}).send(**send_conf)
        marketplace.admin({"update_royalties_address":
                           royalties_contr.address}).send(**send_conf)

        return nft, foreign_nft, royalties_contr, marketplace, normalizer, usd_fa12, multisig, treasury


class TestTreasury(unittest.TestCase):
    def test_deploy_treasury(self):
        treasury = Env().deploy_treasury()
        multisig_init_storage = MultisigStorage()
        multisig = Env().deploy_multisig(multisig_init_storage)

        treasury.addAdmin(CHARLIE_PK).send(**send_conf)
        breakpoint()
