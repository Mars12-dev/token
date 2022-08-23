from test_env import Env, CrowdsaleStorage, pytezos, send_conf, ALICE_PK, FA12Storage
from pytezos.contract.result import OperationResult
import unittest

import logging
logging.basicConfig(level=logging.INFO)


class TestCrowdsale(unittest.TestCase):
    def test_deploy_crowdsale(self):
        init_storage = CrowdsaleStorage(max_mint_per_transaction=2,
                                        paused=False, default_metadata=b"http://my_metadata")
        crowdsale = Env().deploy_crowdsale(init_storage)
        collection = crowdsale.storage["collection"]()
        multisig = crowdsale.storage["multisig"]()
        eurl_contract = Env().deploy_fa12(FA12Storage(ALICE_PK))
        sale_params = {
            "is_presale": False,
            "metadata_list": [],
            "price_per_token": 2,
            "max_mint_per_user": 2,
            "sale_size": 50,
            "sale_currency": {"fa12": eurl_contract.address},
            "start_time": pytezos.now(),
            "end_time": pytezos.now() + 3600,
        }
        crowdsale.setSale(sale_params).send(**send_conf)

        mint_params = {
            "tokens": 2,
            "owner": ALICE_PK,
            "amount_to_pay": 4,
        }

        eurl_contract.mint({"address": ALICE_PK, "value": 4}).send(**send_conf)
        eurl_contract.approve({"spender": crowdsale.address,
                               "value": 4}).send(**send_conf)
        crowdsale.mintFromCrowdsale(
            mint_params).with_amount(4).send(**send_conf)

        print(f"crowdsale: {crowdsale.address}")
        print(f"collection: {collection}")
        print(f"multisig: {multisig}")

    def test_update_metadata_gas(self):
        init_storage = CrowdsaleStorage(max_mint_per_transaction=2,
                                        paused=False, default_metadata=b"http://my_metadata")
        crowdsale = Env().deploy_crowdsale(init_storage)
        collection_address = crowdsale.storage["collection"]()
        collection = pytezos.contract(
            collection_address).using(**Env().using_params)
        multisig = crowdsale.storage["multisig"]()
        eurl_contract = Env().deploy_fa12(FA12Storage(ALICE_PK))
        sale_params = {
            "is_presale": False,
            "metadata_list": [],
            "price_per_token": 2,
            "max_mint_per_user": 2,
            "sale_size": 50,
            "sale_currency": {"fa12": eurl_contract.address},
            "start_time": pytezos.now(),
            "end_time": pytezos.now() + 3600,
        }
        crowdsale.setSale(sale_params).send(**send_conf)

        mint_params = {
            "tokens": 2,
            "owner": ALICE_PK,
            "amount_to_pay": 4,
        }

        eurl_contract.mint({"address": ALICE_PK, "value": 4}).send(**send_conf)
        eurl_contract.approve({"spender": crowdsale.address,
                               "value": 4}).send(**send_conf)
        crowdsale.mintFromCrowdsale(
            mint_params).send(**send_conf)

        self.assertEqual(
            collection.storage["token_metadata"][0]["metadata"](), {'': b"http://my_metadata"})

        update_metadata_param = {
            "tokens": [0],
            "metadata_urls": ["http://my_metadata1"],
        }
        crowdsale.updateMetadata(
            update_metadata_param).send(**send_conf)

        self.assertEqual(
            collection.storage["token_metadata"][0]["metadata"](), {'': b"http://my_metadata1"})

    def test_update_metadata_gas_multiple_tokens(self):
        init_storage = CrowdsaleStorage(max_mint_per_transaction=2,
                                        paused=False, default_metadata=b"http://my_metadata")
        print("---------------------")
        print("DEPLOYING CROWDSALE")
        print("---------------------")
        crowdsale = Env().deploy_crowdsale(init_storage)
        collection_address = crowdsale.storage["collection"]()
        collection = pytezos.contract(
            collection_address).using(**Env().using_params)
        multisig = crowdsale.storage["multisig"]()
        print("---------------------")
        print("DEPLOYING EURL")
        print("---------------------")
        eurl_contract = Env().deploy_fa12(FA12Storage(ALICE_PK))
        sale_params = {
            "is_presale": False,
            "metadata_list": [],
            "price_per_token": 1,
            "max_mint_per_user": 500,
            "sale_size": 500,
            "sale_currency": {"fa12": eurl_contract.address},
            "start_time": pytezos.now(),
            "end_time": pytezos.now() + 3600,
        }
        print("---------------------")
        print("SETTING SALE")
        print("---------------------")
        crowdsale.setSale(sale_params).send(**send_conf)

        mint_params = {
            "tokens": 100,
            "owner": ALICE_PK,
            "amount_to_pay": 100,
        }

        print("---------------------")
        print("MINTING EURL")
        print("---------------------")

        eurl_contract.mint(
            {"address": ALICE_PK, "value": 500}).send(**send_conf)
        print("---------------------")
        print("APPROVING EURL")
        print("---------------------")
        eurl_contract.approve({"spender": crowdsale.address,
                               "value": 500}).send(**send_conf)
        print("---------------------")
        print("MINTING NFTS")
        print("---------------------")
        for i in range(5):
            crowdsale.mintFromCrowdsale(
                mint_params).send(**send_conf)

        for i in range(500):
            print("---------------------")
            print(f"I = {i}")
            print("---------------------")
            ids = []
            metadata_list = []

            for j in range(i + 1):
                new_url = f"http://my_metadata{j}"
                metadata_list.append(new_url)
                ids.append(j)
            update_metadata_param = {
                "tokens": ids,
                "metadata_urls": metadata_list,
            }
            opg = crowdsale.updateMetadata(
                update_metadata_param).send(**send_conf)

            for j in range(i + 1):
                new_url = f"http://my_metadata{j}"
                new_url_bytes = bytes(new_url, 'utf-8')
                self.assertEqual(
                    collection.storage["token_metadata"][j]["metadata"](), {'': new_url_bytes})

            consumed_gas = OperationResult.consumed_gas(opg.opg_result)
            fee = opg.opg_result["contents"][0]["fee"]
            with open('update_metadata_gas.txt', 'a') as f:
                f.write(
                    f'{i + 1} tokens update : {consumed_gas} gas; {fee} mutez fee; \n')


if __name__ == "__main__":
    unittest.main()
