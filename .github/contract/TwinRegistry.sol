// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

contract TwinRegistry {
    address private owner;
    uint256 private rootHashId;

    constructor() {
        owner = msg.sender;
        rootHashId = 0;
    }

    // Struct to store twin hashes
    struct Twin {
        string id;
        bytes32 hash;
        uint256 timestamp;
    }

    Twin[] private twins;
    mapping(string => uint256) private twinIndex;

    modifier ownerOnly() {
        require(msg.sender == owner, "Only contract owner can manage twins");
        _;
    }

    // function hashString(string calldata _string) public pure returns (bytes32) {
    //     return keccak256(abi.encodePacked(_string));
    // }

    // Function to update or add a twin hash to the registry
    function putTwinHash(string calldata id, bytes32 twinHash) public {
        if (twinIndex[id] == 0) {
            postTwinHash(id, twinHash);
        } else {
            patchTwinHash(id, twinHash);
        }
    }

    // Function to add a twin hash to the registry
    function postTwinHash(
        string calldata id,
        bytes32 twinHash
    ) public ownerOnly {
        require(
            twinIndex[id] == 0,
            "Twin already exists, use methods 'putTwin' or 'patchTwin' instead"
        );

        twins.push(Twin(id, twinHash, block.timestamp));
        twinIndex[id] = twins.length;
    }

    // Function to update a twin hash in the registry
    function patchTwinHash(
        string calldata id,
        bytes32 twinHash
    ) public ownerOnly {
        require(
            twinIndex[id] != 0,
            "Twin does not exist, use method 'postTwin' instead"
        );

        uint256 index = twinIndex[id] - 1;
        twins[index].hash = twinHash;
        twins[index].timestamp = block.timestamp;
    }

    // Verify that twin hash matches
    function verifyTwinHash(
        string calldata id,
        bytes32 twinHash
    ) public view returns (bool, uint256) {
        Twin memory twin = getTwin(id);
        if (twin.hash == twinHash) {
            return (true, twin.timestamp);
        }
        return (false, block.timestamp);
    }

    function derpifyTwin(
        string calldata id,
        bytes32 twinHash
    ) public view returns (bytes32, bytes32) {
        Twin memory twin = getTwin(id);
        return (twin.hash, twinHash);
    }

    // Function to get a twin
    function getTwin(string calldata id) public view returns (Twin memory) {
        require(twinIndex[id] != 0, "Twin does not exist");

        uint256 index = twinIndex[id] - 1;
        return twins[index];
    }

    // Function to get all twins
    function getTwins() public view returns (Twin[] memory) {
        return twins;
    }

    // Interledger functionalities
    event InterledgerEventSending(uint256 id, bytes32 data);

    function interledgerCommit(uint256 id) public {
        rootHashId = id;
    }

    // Submit merkle tree root hash to interledger
    function setRootHash(bytes32 rootHash) public ownerOnly {
        emit InterledgerEventSending(rootHashId + 1, rootHash);
    }
}
