from re import match
from brownie import accounts, config, network, MatchFactory, GolfMatch, MockV3Aggregator
from brownie.network import web3
from scripts.helpers import get_account, deploy_mocks, LOCAL_BLOCKCHAIN_ENVIRONMENTS

import time

def deploy_match_factory():

    player0 = get_account()
    
    print(f"Using account: {player0}")

    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        price_feed_address = config["networks"][network.show_active()]["eth_usd_price_feed"]
    else:
        deploy_mocks()
        price_feed_address = MockV3Aggregator[-1].address

    match_factory = MatchFactory.deploy(price_feed_address, {"from":player0}, publish_source=config["networks"][network.show_active()].get("verify"))

    balance = match_factory.getBalance()
    print(f"BALANCE: {balance}")
    
def main():
    deploy_match_factory()