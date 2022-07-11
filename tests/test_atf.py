import unittest
import json
from pytezos import pytezos
from pytezos.rpc.errors import MichelsonError

from env import Env, Keys

ALICE_PK = Keys().ALICE_PK
BOB_PK = Keys().BOB_PK

alice_pytezos = Keys().alice_pytezos
bob_pytezos = Keys().bob_pytezos

send_conf = dict(min_confirmations=1)

using_params = Keys().alice_using_params


class TestAtf(unittest.TestCase):
    @staticmethod
    def print_title(instance):
        print("Test Atf: " + instance.__class__.__name__ + "...")
        print("-----------------------------------")

    @staticmethod
    def print_success(function_name):
        print(function_name + "... ok")
        print("-----------------------------------")

    class TestDeploy(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_deploys_with_default_storage(self):
            Atf = Env().deploy_Atf()
            total_supply = 1_000_000_000 * 10 ** 5
            self.assertEqual(Atf.storage["paused"](), False)
            self.assertEqual(Atf.storage["ledger"][ALICE_PK](), total_supply)
            self.assertEqual(Atf.storage["total_supply"](), total_supply)

            TestAtf.print_success("test1_it_deploys_with_default_storage")

        def test2_it_fails_when_called_with_amount(self):
            Atf = Env().deploy_Atf()

            with self.assertRaises(MichelsonError) as err:
                Atf.transfer({"from": ALICE_PK, "to": BOB_PK, "value": 0}).with_amount(
                    10
                ).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {
                             "string": "DontSendTez"})

            TestAtf.print_success("test2_it_fails_when_called_with_amount")

    class Transfer(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_transfers_sender_value(self):
            Atf = Env().deploy_Atf()

            value = 1000
            alice_balance = Atf.storage["ledger"][ALICE_PK]()
            Atf.transfer({"from": ALICE_PK, "to": BOB_PK, "value": value}).send(
                **send_conf
            )

            self.assertEqual(Atf.storage["ledger"]
                             [ALICE_PK](), alice_balance - value)
            self.assertEqual(Atf.storage["ledger"][BOB_PK](), value)

            TestAtf.print_success("test1_it_transfers_sender_value")

        def test2_it_transfers_approved_value(self):
            Atf = Env().deploy_Atf()

            value = 1000
            half_value = 500
            alice_balance = Atf.storage["ledger"][ALICE_PK]()

            Atf.approve({"spender": BOB_PK, "value": value}).send(**send_conf)

            bob_pytezos.contract(Atf.address).transfer(
                {"from": ALICE_PK, "to": Atf.address, "value": half_value}
            ).send(**send_conf)
            self.assertEqual(
                Atf.storage["ledger"][ALICE_PK](), alice_balance - half_value)
            self.assertEqual(Atf.storage["ledger"]
                             [Atf.address](), half_value)
            self.assertEqual(
                Atf.storage["allowances"][ALICE_PK, BOB_PK](), half_value)

            bob_pytezos.contract(Atf.address).transfer(
                {"from": ALICE_PK, "to": Atf.address, "value": half_value}
            ).send(**send_conf)
            self.assertEqual(Atf.storage["ledger"]
                             [ALICE_PK](), alice_balance - value)
            self.assertEqual(Atf.storage["ledger"][Atf.address](), value)
            with self.assertRaises(KeyError):
                Atf.storage["allowances"][ALICE_PK, BOB_PK]()

            TestAtf.print_success("test2_it_transfers_approved_value")

        def test3_it_fails_when_contract_in_pause(self):
            Atf = Env().deploy_Atf()

            Atf.setPause(True).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                Atf.transfer({"from": ALICE_PK, "to": BOB_PK, "value": 0}).send(
                    **send_conf
                )
            self.assertEqual(
                err.exception.args[0]["with"], {"string": "contract in pause"}
            )

            TestAtf.print_success("test3_it_fails_when_contract_in_pause")

        def test4_it_fails_when_no_allowance(self):
            Atf = Env().deploy_Atf()

            value = 1000
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(Atf.address).transfer(
                    {"from": ALICE_PK, "to": Atf.address, "value": value}
                ).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {"string": "NotEnoughAllowance"}
            )

            TestAtf.print_success("test4_it_fails_when_no_allowance")

        def test5_it_fails_when_allowance_is_lower_than_value(self):
            Atf = Env().deploy_Atf()

            value = 1000
            Atf.approve({"spender": BOB_PK, "value": value}).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(Atf.address).transfer(
                    {"from": ALICE_PK, "to": Atf.address, "value": value + 1000}
                ).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {"string": "NotEnoughAllowance"}
            )
            self.assertEqual(
                Atf.storage["allowances"][ALICE_PK, BOB_PK](), value)

            TestAtf.print_success(
                "test5_it_fails_when_allowance_is_lower_than_value")

        def test6_it_fails_when_balance_is_lower_than_value(self):
            Atf = Env().deploy_Atf()

            alice_balance = Atf.storage["ledger"][ALICE_PK]()
            value = alice_balance + 1000

            with self.assertRaises(MichelsonError) as err:
                Atf.transfer({"from": ALICE_PK, "to": BOB_PK, "value": value}).send(
                    **send_conf
                )
            self.assertEqual(
                err.exception.args[0]["with"], {"string": "NotEnoughBalance"}
            )

            TestAtf.print_success(
                "test6_it_fails_when_balance_is_lower_than_value")

    class TransferBatch(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_make_multiple_transfers(self):
            Atf = Env().deploy_Atf()

            fst_value = 5000
            snd_value = 3000
            thd_value = 1000

            alice_balance = Atf.storage["ledger"][ALICE_PK]()
            bob_pytezos.contract(Atf.address).approve(
                {"spender": ALICE_PK, "value": thd_value}
            ).send(**send_conf)

            Atf.transferBatch(
                [
                    {"from": ALICE_PK, "to": BOB_PK, "value": fst_value},
                    {"from": ALICE_PK, "to": Atf.address, "value": snd_value},
                    {"from": BOB_PK, "to": ALICE_PK, "value": thd_value},
                ]
            ).send(**send_conf)

            self.assertEqual(
                Atf.storage["ledger"][ALICE_PK](),
                alice_balance - fst_value - snd_value + thd_value,
            )
            self.assertEqual(Atf.storage["ledger"]
                             [BOB_PK](), fst_value - thd_value)
            self.assertEqual(Atf.storage["ledger"][Atf.address](), snd_value)

        def test2_it_fails_when_contract_in_pause(self):
            Atf = Env().deploy_Atf()

            Atf.setPause(True).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                Atf.transferBatch([{"from": ALICE_PK, "to": BOB_PK, "value": 0}]).send(
                    **send_conf
                )
            self.assertEqual(
                err.exception.args[0]["with"], {"string": "contract in pause"}
            )

            TestAtf.print_success("test2_it_fails_when_contract_in_pause")

    class Approve(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_adds_new_allowance(self):
            Atf = Env().deploy_Atf()

            value = 30
            allowance_key = {"owner": ALICE_PK, "spender": BOB_PK}

            Atf.approve({"spender": BOB_PK, "value": value}).send(**send_conf)
            self.assertEqual(
                Atf.storage["allowances"][allowance_key](), value)

            TestAtf.print_success("test1_it_adds_new_allowance")

        def test2_it_fails_when_contract_in_paused(self):
            Atf = Env().deploy_Atf()

            Atf.setPause(True).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                Atf.approve({"spender": BOB_PK, "value": 0}).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {"string": "contract in pause"}
            )

            TestAtf.print_success("test2_it_fails_when_contract_in_pause")

        def test3_it_fails_when_allowance_already_exists(self):
            Atf = Env().deploy_Atf()

            value = 30
            Atf.approve({"spender": BOB_PK, "value": value}).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                Atf.approve({"spender": BOB_PK, "value": value}
                             ).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {
                    "string": "UnsafeAllowanceChange"}
            )

            TestAtf.print_success(
                "test3_it_fails_when_allowance_already_exists")

    class Burn(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_burns_ledger_from_address_and_total_supply(self):
            Atf = Env().deploy_Atf()

            value = 500000000
            inital_supply = 1_000_000_000 * 10 ** 5

            alice_balance = Atf.storage["ledger"][ALICE_PK]()

            Atf.burn({"address_from": ALICE_PK, "value": value}
                      ).send(**send_conf)
            self.assertEqual(
                Atf.storage["total_supply"](), inital_supply - value)
            self.assertEqual(Atf.storage["ledger"]
                             [ALICE_PK](), alice_balance - value)

            TestAtf.print_success(
                "test1_it_burns_ledger_from_address_and_total_supply"
            )

        def test2_it_burns_approved_value(self):
            Atf = Env().deploy_Atf()

            value = 500000000
            half_value = 250000000
            inital_supply = 1_000_000_000 * 10 ** 5

            alice_balance = Atf.storage["ledger"][ALICE_PK]()

            Atf.approve({"spender": BOB_PK, "value": value}).send(**send_conf)

            bob_pytezos.contract(Atf.address).burn(
                {"address_from": ALICE_PK, "value": half_value}
            ).send(**send_conf)
            self.assertEqual(
                Atf.storage["total_supply"](), inital_supply - half_value)
            self.assertEqual(
                Atf.storage["ledger"][ALICE_PK](), alice_balance - half_value)
            self.assertEqual(
                Atf.storage["allowances"][ALICE_PK, BOB_PK](), half_value)

            bob_pytezos.contract(Atf.address).burn(
                {"address_from": ALICE_PK, "value": half_value}
            ).send(**send_conf)
            self.assertEqual(
                Atf.storage["total_supply"](), inital_supply - value)
            self.assertEqual(Atf.storage["ledger"]
                             [ALICE_PK](), alice_balance - value)
            with self.assertRaises(KeyError):
                Atf.storage["allowances"][ALICE_PK, BOB_PK]()

            TestAtf.print_success("test2_it_burns_approved_value")

        def test3_it_fails_when_burn_in_pause(self):
            Atf = Env().deploy_Atf()

            Atf.setBurnPause(True).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                Atf.burn({"address_from": ALICE_PK, "value": 500000000}).send(
                    **send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {"string": "burn in pause"}
            )

            TestAtf.print_success("test3_it_fails_when_burn_in_pause")

        def test4_it_fails_when_no_allowance(self):
            Atf = Env().deploy_Atf()

            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(Atf.address).burn(
                    {"address_from": ALICE_PK, "value": 500000000}
                ).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {"string": "NotEnoughAllowance"}
            )

            TestAtf.print_success("test4_it_fails_when_no_allowance")

        def test5_it_fails_when_allowance_is_lower_than_value(self):
            Atf = Env().deploy_Atf()

            value = 500000000
            Atf.approve({"spender": BOB_PK, "value": value}).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(Atf.address).burn(
                    {"address_from": ALICE_PK, "value": value + 1000}
                ).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {"string": "NotEnoughAllowance"}
            )
            self.assertEqual(
                Atf.storage["allowances"][ALICE_PK, BOB_PK](), value)

            TestAtf.print_success(
                "test5_it_fails_when_allowance_is_lower_than_value")

        def test6_it_fails_when_balance_is_lower_than_value(self):
            Atf = Env().deploy_Atf()

            alice_balance = Atf.storage["ledger"][ALICE_PK]()
            value = alice_balance + 1000

            with self.assertRaises(MichelsonError) as err:
                Atf.burn({"address_from": ALICE_PK, "value": value}).send(
                    **send_conf
                )
            self.assertEqual(
                err.exception.args[0]["with"], {"string": "NotEnoughBalance"}
            )

            TestAtf.print_success(
                "test6_it_fails_when_balance_is_lower_than_value")

        def test7_it_fails_when_total_supply_is_lower_than_value(self):
            # cannot happen as total_supply is always higher than balances tested before
            pass

    class GetAllowance(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_returns_allowance(self):
            Atf = Env().deploy_Atf()

            value = 30
            allowance_key = {"owner": ALICE_PK, "spender": BOB_PK}
            Atf.approve({"spender": BOB_PK, "value": value}).send(**send_conf)

            allowance = Atf.getAllowance(
                {"request": allowance_key, "callback": None}
            ).callback_view()
            self.assertEqual(allowance, value)

            TestAtf.print_success("test1_it_returns_allowance")

    class GetBalance(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_returns_balance(self):
            Atf = Env().deploy_Atf()

            balance = Atf.getBalance(
                {"owner": ALICE_PK, "callback": None}
            ).callback_view()
            self.assertEqual(balance, 1_000_000_000 * 10 ** 5)
            self.assertEqual(balance, Atf.storage["ledger"][ALICE_PK]())

            TestAtf.print_success("test1_it_returns_balance")

    class GetTotalSupply(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_returns_total_supply(self):
            Atf = Env().deploy_Atf()

            total_supply = Atf.getTotalSupply(
                {"request": None, "callback": None}
            ).callback_view()
            self.assertEqual(total_supply, 1_000_000_000 * 10 ** 5)
            self.assertEqual(total_supply, Atf.storage["total_supply"]())

            TestAtf.print_success("test1_it_returns_total_supply")

    class SetMultisig(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_sets_multisig(self):
            Atf = Env().deploy_Atf()
            self.assertNotEqual(Atf.storage["multisig"](), ALICE_PK)
            Atf.setMultisig(ALICE_PK).send(**send_conf)
            self.assertEqual(Atf.storage["multisig"](), ALICE_PK)
            TestAtf.print_success("test1_it_sets_multisig")

        def test2_it_sets_multisig_with_two_admins(self):
            Atf = Env().deploy_Atf()
            multisig_addr = Atf.storage["multisig"]()
            multisig = alice_pytezos.using(**using_params).contract(
                multisig_addr)
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            other_multisig = Env().deploy_multisig()
            Atf.setMultisig(other_multisig.address).send(**send_conf)
            self.assertEqual(Atf.storage["multisig"](), multisig_addr)
            bob_pytezos.contract(Atf.address).setMultisig(
                other_multisig.address).send(**send_conf)
            TestAtf.print_success("test2_it_sets_multisig_with_two_admins")

    class SetPause(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_updates_pause(self):
            Atf = Env().deploy_Atf()

            Atf.setPause(True).send(**send_conf)
            self.assertEqual(Atf.storage["paused"](), True)
            Atf.setPause(False).send(**send_conf)
            self.assertEqual(Atf.storage["paused"](), False)

            TestAtf.print_success("test1_it_updates_pause")

        def test2_it_updates_pause_with_two_admins(self):
            Atf = Env().deploy_Atf()
            multisig_addr = Atf.storage["multisig"]()
            multisig = alice_pytezos.using(**using_params).contract(
                multisig_addr)
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            bob_pytezos.contract(Atf.address).setPause(True).send(**send_conf)
            self.assertEqual(Atf.storage["paused"](), False)
            Atf.setPause(True).send(**send_conf)
            self.assertEqual(Atf.storage["paused"](), True)
            bob_pytezos.contract(Atf.address).setPause(
                False).send(**send_conf)
            self.assertEqual(Atf.storage["paused"](), True)
            Atf.setPause(False).send(**send_conf)
            self.assertEqual(Atf.storage["paused"](), False)

            TestAtf.print_success("test2_it_updates_pause_with_two_admins")

        def test3_it_fails_when_not_multisig_admin(self):
            Atf = Env().deploy_Atf()

            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(Atf.address).setPause(
                    True).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {
                    "int": "1001"}
            )

            TestAtf.print_success("test3_it_fails_when_not_admin")

    class SetBurnPause(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_updates_burn_pause(self):
            Atf = Env().deploy_Atf()
            Atf.setBurnPause(True).send(**send_conf)
            self.assertEqual(Atf.storage["burn_paused"](), True)
            Atf.setBurnPause(False).send(**send_conf)
            self.assertEqual(Atf.storage["burn_paused"](), False)

            TestAtf.print_success("test1_it_updates_burn_pause")

        def test2_it_updates_burn_pause_with_two_admins(self):
            Atf = Env().deploy_Atf()
            multisig_addr = Atf.storage["multisig"]()
            multisig = alice_pytezos.using(**using_params).contract(
                multisig_addr)
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)
            bob_pytezos.contract(Atf.address).setBurnPause(
                True).send(**send_conf)
            self.assertEqual(Atf.storage["burn_paused"](), False)
            Atf.setBurnPause(True).send(**send_conf)
            self.assertEqual(Atf.storage["burn_paused"](), True)
            bob_pytezos.contract(Atf.address).setBurnPause(
                False).send(**send_conf)
            self.assertEqual(Atf.storage["burn_paused"](), True)
            Atf.setBurnPause(False).send(**send_conf)
            self.assertEqual(Atf.storage["burn_paused"](), False)

            TestAtf.print_success(
                "test2_it_updates_burn_pause_with_two_admins")

        def test3_it_fails_when_not_multisig_admin(self):
            Atf = Env().deploy_Atf()
            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(Atf.address).setBurnPause(
                    True).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {
                    "int": "1001"}
            )

            TestAtf.print_success("test3_it_fails_when_not_multisig_admin")

    class SetTokenMetadata(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_updates_token_metadata(self):
            Atf = Env().deploy_Atf()

            token_id = 0
            param_metadata = {
                "uri": "".encode().hex(),
                "name": "AtfMI Token".encode().hex(),
                "symbol": "Atf".encode().hex(),
                "decimals": "8".encode().hex(),
                "shouldPreferSymbol": "true".encode().hex(),
                "thumbnailUri": "ipfs://bafybeiaqmcqjihmhj6gsqnxlxcnw6i5llrpbofwwr2rvdmydnyue3sj6n4/1vwBlfK3.jpg".encode().hex(),
            }
            Atf.setTokenMetadata(param_metadata).send(**send_conf)

            on_chain_metadata = {
                "token_id": token_id,
                "token_info": {
                    "": bytes.fromhex(param_metadata["uri"]),
                    "name": bytes.fromhex(param_metadata["name"]),
                    "symbol": bytes.fromhex(param_metadata["symbol"]),
                    "decimals": bytes.fromhex(param_metadata["decimals"]),
                    "shouldPreferSymbol": bytes.fromhex(
                        param_metadata["shouldPreferSymbol"]
                    ),
                    "thumbnailUri": bytes.fromhex(param_metadata["thumbnailUri"]),
                },
            }
            self.assertEqual(
                Atf.storage["token_metadata"][token_id](), on_chain_metadata
            )

            TestAtf.print_success("test1_it_updates_token_metadata")

        def test2_it_updates_token_metadata_with_two_admins(self):
            Atf = Env().deploy_Atf()
            multisig_addr = Atf.storage["multisig"]()
            multisig = alice_pytezos.using(**using_params).contract(
                multisig_addr)
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)

            token_id = 0
            param_metadata = {
                "uri": "".encode().hex(),
                "name": "AtfMI Token".encode().hex(),
                "symbol": "Atf".encode().hex(),
                "decimals": "8".encode().hex(),
                "shouldPreferSymbol": "true".encode().hex(),
                "thumbnailUri": "ipfs://bafybeiaqmcqjihmhj6gsqnxlxcnw6i5llrpbofwwr2rvdmydnyue3sj6n4/1vwBlfK3.jpg".encode().hex(),
            }
            Atf.setTokenMetadata(param_metadata).send(**send_conf)
            with self.assertRaises(KeyError):
                Atf.storage["token_metadata"][token_id]()
            bob_pytezos.contract(Atf.address).setTokenMetadata(
                param_metadata).send(**send_conf)

            on_chain_metadata = {
                "token_id": token_id,
                "token_info": {
                    "": bytes.fromhex(param_metadata["uri"]),
                    "name": bytes.fromhex(param_metadata["name"]),
                    "symbol": bytes.fromhex(param_metadata["symbol"]),
                    "decimals": bytes.fromhex(param_metadata["decimals"]),
                    "shouldPreferSymbol": bytes.fromhex(
                        param_metadata["shouldPreferSymbol"]
                    ),
                    "thumbnailUri": bytes.fromhex(param_metadata["thumbnailUri"]),
                },
            }
            self.assertEqual(
                Atf.storage["token_metadata"][token_id](), on_chain_metadata
            )

            TestAtf.print_success(
                "test2_it_updates_token_metadata_with_two_admins")

        def test3_it_fails_when_not_admin(self):
            Atf = Env().deploy_Atf()

            param_metadata = {
                "uri": "",
                "name": "",
                "symbol": "",
                "decimals": "",
                "shouldPreferSymbol": "",
                "thumbnailUri": "",
            }
            Atf.setTokenMetadata(param_metadata).send(**send_conf)

            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(Atf.address).setTokenMetadata(
                    param_metadata
                ).send(**send_conf)
            self.assertEqual(
                err.exception.args[0]["with"], {
                    "int": "1001"}
            )

            TestAtf.print_success("test3_it_fails_when_not_admin")

    class SetMetadata(unittest.TestCase):
        def test0_before_tests(self):
            TestAtf.print_title(self)

        def test1_it_updates_metadata(self):
            Atf = Env().deploy_Atf()

            new_metadata = json.dumps({
                "name": "Atf Atf",
                "version": "1",
                "homepage": "https://Atfmi_forever.com/",
                "authors": ["AtfMI <hello@hello.com>"],
                "interfaces": ["TZIP-012", "TZIP-021"]
            }).encode()
            Atf.setMetadata(new_metadata.hex()).send(**send_conf)

            self.assertEqual(
                Atf.storage["metadata"]["content"](), new_metadata)

            new_metadata = json.dumps({
                "name": "Atf",
                "version": "1.0.0",
                "homepage": "https://Atfmi.com/",
                "authors": ["AtfMI <hello@Atfmi.com>"],
                "interfaces": ["TZIP-012", "TZIP-016"]
            }).encode()
            Atf.setMetadata(new_metadata.hex()).send(**send_conf)

            self.assertEqual(
                Atf.storage["metadata"]["content"](), new_metadata)

            TestAtf.print_success("test1_it_updates_metadata")

        def test2_it_updates_metadata_with_two_admins(self):
            Atf = Env().deploy_Atf()
            multisig_addr = Atf.storage["multisig"]()
            multisig = alice_pytezos.using(**using_params).contract(
                multisig_addr)
            multisig.addAdmin(BOB_PK).send(**send_conf)
            multisig.setThreshold(2).send(**send_conf)

            new_metadata = json.dumps({
                "name": "ATF",
                "version": "1",
                "homepage": "https://Atfmi_forever.com/",
                "authors": ["AtfMI <hello@hello.com>"],
                "interfaces": ["TZIP-012", "TZIP-021"]
            }).encode()
            Atf.setMetadata(new_metadata.hex()).send(**send_conf)

            bob_pytezos.contract(Atf.address).setMetadata(
                new_metadata.hex()).send(**send_conf)

            self.assertEqual(
                Atf.storage["metadata"]["content"](), new_metadata)

            TestAtf.print_success("test2_it_updates_metadata_with_two_admins")

        def test3_it_fails_when_not_admin(self):
            Atf = Env().deploy_Atf()

            with self.assertRaises(MichelsonError) as err:
                bob_pytezos.contract(Atf.address).setMetadata(
                    json.dumps({"": ""}).encode().hex()).send(**send_conf)
            self.assertEqual(err.exception.args[0]["with"], {
                             "int": "1001"})

            TestAtf.print_success("test3_it_fails_when_not_admin")

    def test_inner_test_class(self):
        test_classes_to_run = [
            self.TestDeploy,
            self.Transfer,
            self.TransferBatch,
            self.Approve,
            self.Burn,
            self.GetAllowance,
            self.GetBalance,
            self.GetTotalSupply,
            self.SetPause,
            self.SetBurnPause,
            self.SetTokenMetadata,
            self.SetMetadata,
            self.SetMultisig,
        ]
        suites_list = []
        for test_class in test_classes_to_run:
            suites_list.append(
                unittest.TestLoader().loadTestsFromTestCase(test_class))

        big_suite = unittest.TestSuite(suites_list)
        unittest.TextTestRunner().run(big_suite)


if __name__ == "__main__":
    unittest.main()
