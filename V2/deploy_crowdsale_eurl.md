# Deploy crowdsale contract with lugh's EURL token as payment method

To deploy the crowdsale contract, use the following command from the root folder of the project (`contracts/v4`):
`python3 deploy_crowdsale_eurl.py`

This script deploys the following contracts:
- `crowdsale` contract
- `collection` contract: an FA2 contract.
- `multisig` contract: a contract used to control the administration entrypoints (all entrypoints except `mintFromCrowdsale`) by multiple admins - by default this contract is deployed with one admin, in which case this acts as a regular admin.

Initial settings deploy the contracts to HangzhouNet, so another contract is deployed to simulate interaction with the EURL contract.

## Set a sale:
To set a new sale along with deployment:
- open file `contracts/v4/deploy_crowdsale_eurl.py`
- uncomment line 26
- change `sale_params` (lines 16-25) to the wanted values.

## Add to whitelist:
If the sale's `is_presale` was set as `True`, a whitelist must exist for the minting process to succeed.
To add users to the whitelist:
- open file `contracts/v4/deploy_crowdsale_eurl.py`
- uncomment line 35 `crowdsale.addToWhitelist(user_list).send(**send_conf)`
- `user_list` should follow the template from lines 28-33

## Mint:
After the sale was set and (optionally) the whitelist is finalized, users can mint NFTs for themselves or others.
To mint a user's NFTs:
- open file `contracts/v4/deploy_crowdsale_eurl.py`
- uncomment lines 43-47 (if the contract was deployed on mainnet, leave line 43 commented, as a user cannot mint EURL for themselves).
- change `mint_params` (lines 37-41) to the wanted values.

## Deploying to mainnet
To deploy to mainnet: 
- open file `contracts/v4/deploy_crowdsale_env.py` 
- comment line 9 `SHELL = "https://rpc.hangzhou.tzstats.com"`
- uncomment line 15 `SHELL = "https://rpc.tzstats.com"`
- open file `contracts/v4/deploy_crowdsale_eurl.py`
- comment line 10 `eurl_contract = Env().deploy_fa12(FA12Storage(ALICE_PK))`
- uncomment lines 13-14


# Hangzhounet contract addresses
example of the contracts deployed on Hangzhounet:

crowdsale: KT1MVXeEqS1uYtv6pLiKR3fJN23vQzbXo2m1
collection: KT1Q3F6kby3X4zrevtfF2zAHxojw93oebADT
multisig: KT19VSHyjqk2BypcFGD1hSyjDdc8wPaRdxfm