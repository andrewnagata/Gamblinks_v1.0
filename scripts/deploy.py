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
    
    # CHAINLINK TEST
    ethUsdPrice = match_factory.get_price()
    print(f"Current Price $$ - {ethUsdPrice}")
    oneDollar = match_factory.get_dollar_to_eth(1)
    decim = oneDollar / 10**18
    print(f"$1 is this many ETH - {decim}")
    oneEth = match_factory.get_eth_to_dollar(1)
    print(f"1 ETH is this many $ - {oneEth}")

    new_match = match_factory.createMatch("Jonny Coordinator", "Brookside Bangers")
    new_match.wait(1)
    new_match_address = new_match.events["OnMatchCreated"]["match_address"]
    new_match_name = new_match.events["OnMatchCreated"]["match_name"]

    current_match = GolfMatch.at(new_match_address)

    coordinator = current_match.coordinator()

    print(f"New Match named {new_match_name} with COORDINATOR wallet address: {coordinator}")

    #ADD Players
    player1 = accounts[1]
    add_player_tx = current_match.add_player("Chump Changer", player1, {"from":player0})
    add_player_tx.wait(1)
    player2 = accounts[2]
    add_player_tx = current_match.add_player("Bogey Bro", player2, {"from":player0})
    add_player_tx.wait(1)

    #Set Bets
    value = web3.toWei(1, "ether")
    bet_tx2 = current_match.updatePlayerInfo(2, {"from":player0,"value":value})
    bet_tx2.wait(1)

    value = web3.toWei(1, "ether")
    bet_tx = current_match.updatePlayerInfo(2, {"from":player1,"value":value})
    bet_tx.wait(1)

    value = web3.toWei(1, "ether")
    bet_tx = current_match.updatePlayerInfo(2, {"from":player2,"value":value})
    bet_tx.wait(1)

    player_count = current_match.getPlayerCount()
    
    print(f"There are {player_count} signed up to gamble")

    (match_name, match_state, allPlayers) = current_match.get_match_status()
   
    for i in range(0, player_count):
        #(name, address) = current_match.getPlayerAtIndex(i)
        bet = current_match.getBetForPlayer(allPlayers[i][0])
        c_bet = web3.fromWei(bet, "ether")
        print(f"Player {i}: {allPlayers[i][1]}({allPlayers[i][0]}) is betting {c_bet} ETH")

    tx_start = current_match.startMatch({"from":player0})
    tx_start.wait(1)

    #Test score reporting
    post_tx = current_match.postScore(36, 35, {"from":player0})
    post_tx.wait(1)

    post_tx = current_match.postScore(36, 36, {"from":player1})
    post_tx.wait(1)

    post_tx = current_match.postScore(36, 36, {"from":player2})
    post_tx.wait(1)

    (match_name, state, player_list) = current_match.get_match_status()
    print(f"MATCH : {match_name}   STATE: {state}")
    for player in player_list:
        print(player)
    for player in player_list:
        usd = match_factory.get_eth_to_dollar(player[4]) / 10**18
        print(f"{player[1]} wins {player[5]}: ${usd}")

    #end_tx = current_match.endMatch({"from":player0})
    #end_tx.wait(1)

    print(f"{player0} has balance of {player0.balance()}")
    print(f"{player1} has balance of {player1.balance()}")
    print(f"{player2} has balance of {player2.balance()}")

        # TEST BALANCES
    balance = match_factory.getBalance()
    print(f"MatchFactory balance: {balance}")

    m_balance = current_match.getBalance()
    print(f"Match balance: {m_balance}")

    #USD to ETH conversion
    converted = match_factory.get_eth_to_dollar(m_balance) / 10**18
    print(f"in USD: {converted}")

    d_tx = current_match.deleteMatch({"from":player0})
    d_tx.wait(1)

    match_address = match_factory.query_player_address(player0)
    print(f"Deleted match??  {match_address}")

    # r_tx = match_factory.removeMatch(new_match_address)
    # r_tx.wait(1)
    # (match_name, state, player_list) = GolfMatch.at(address).get_match_status()
    # print(f"Current deleted Match: {match_name}")
    # print(f"Current deleted state: {state}")

    #start_tx = current_match.startMatch({"from":player0})
    #start_tx.wait(1)

def main():
    deploy_match_factory()