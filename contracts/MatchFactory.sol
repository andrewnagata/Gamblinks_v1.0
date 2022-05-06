// SPDX-License-Identifier: MIT

pragma solidity >=0.6.0 <0.9.0;

import "@chainlink/contracts/src/v0.6/interfaces/AggregatorV3Interface.sol";
import "./GolfMatch.sol";

contract MatchFactory {

    address owner;
    GolfMatch[] public matches;
    mapping(address => GolfMatch) public addressToGolfMatch;
    mapping(address => address) public playerAddressToMatchAdress;

    AggregatorV3Interface public priceFeed;

    event OnMatchCreated(string match_name, address match_address);

    constructor(address _priceFeed) {

        owner = msg.sender;

        priceFeed = AggregatorV3Interface(_priceFeed);
    }

    function createMatch(string memory coordinator_name, string memory _match_name) public {

        GolfMatch golfMatch = new GolfMatch(_match_name, msg.sender, address(this));

        matches.push(golfMatch);

        addressToGolfMatch[address(golfMatch)] = golfMatch;

        // Add the Coordinator by default
        golfMatch.add_player(coordinator_name, msg.sender);

        emit OnMatchCreated(_match_name, address(golfMatch));
    }

    function removeMatch(address match_address) public {
        delete addressToGolfMatch[match_address];
    }

    function add_player(address _player, address _match) public {
        
        require(playerAddressToMatchAdress[_player] == address(0), "Player is already in a match");

        playerAddressToMatchAdress[_player] = _match;
    }

    function remove_player(address _player) public {
        delete playerAddressToMatchAdress[_player];
    }

    function query_player_address(address _player) public view returns(address) {
        return playerAddressToMatchAdress[_player];
    }

    function getBalance() public view returns(uint256) {
        return address(this).balance;
    }

    // Chainlink Price Feed
    function get_version() public view returns (uint256) {
        return priceFeed.version();
    }

    function get_price() public view returns(uint256) {
        (, int256 answer, , , ) = priceFeed.latestRoundData();
        return uint256(answer * 10000000000);
    }

    function get_dollar_to_eth(uint256 _dollar_amount) public view returns (uint256) {
        uint256 dollar_amount = _dollar_amount * 10**18;
        uint256 price = get_price();
        uint256 precision = 1 * 10**18;
        return (dollar_amount * precision) / price;
    }

    function get_eth_to_dollar(uint256 eth_amount) public view returns(uint256) {
        uint256 price = get_price();
        uint256 precision = 1 * 10**18;
        return (price / precision) * eth_amount;
    }
}