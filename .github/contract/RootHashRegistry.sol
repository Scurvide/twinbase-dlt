// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.0;

import "./MerkleProof.sol";

contract RootHashRegistry {
    // Struct to store twin hashes
    struct Root {
        uint256 nonce;
        bytes32 hash;
        uint256 timestamp;
    }

    Root[] private rootHashes;

    event InterledgerEventAccepted(uint256 nonce);

    event InterledgerEventRejected(uint256 nonce);

    function interledgerReceive(uint256 nonce, bytes32 payload) public {
        rootHashes.push(Root(nonce, payload, block.timestamp));
        emit InterledgerEventAccepted(nonce);
    }

    function getRootHash() public view returns (Root memory) {
        require(rootHashes.length > 0, "No root hash found");
        return rootHashes[rootHashes.length - 1];
    }

    function getRootHashes() public view returns (Root[] memory) {
        require(rootHashes.length > 0, "No root hashes found");
        return rootHashes;
    }

    // function hashString(string calldata _string) public pure returns (bytes32) {
    //     return keccak256(abi.encodePacked(_string));
    // }

    function verifyHash(
        bytes32[] memory proof,
        bytes32 leafHash
    ) public view returns (bool, uint256, bytes32, bytes32) {
        Root memory root = getRootHash();
        // bytes32 leaf = hashString(object);
        bool verified = MerkleProof.verify(proof, root.hash, leafHash);
        // require(
        //     MerkleProof.verify(proof, root.hash, leafHash),
        //     "Invalid proof"
        // );
        return (verified, root.timestamp, root.hash, leafHash);
    }
}
