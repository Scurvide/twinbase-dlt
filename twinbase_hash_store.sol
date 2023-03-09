// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8;

contract TwinbaseHashStore {

    mapping(uint => string) documentHashes;

    function storeDocumentHash(uint id, string calldata documentHash) public returns (string memory) {
        // Store document hash by its id
        documentHashes[id] = documentHash;
        return documentHashes[id];
    }

    function getDocumentHash(uint id) public view returns (string memory) {
        // Return the hash of a document by its id
        return documentHashes[id];
    }
}