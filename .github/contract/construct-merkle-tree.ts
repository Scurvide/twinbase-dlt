import { StandardMerkleTree } from "@openzeppelin/merkle-tree";
import Web3 from "web3"
import { AbiItem } from 'web3-utils';
import fs from "fs";

import contractInfo from "../../docs/static/contract/contract-info.json";

declare var process: {
    env: {
        DLT_PRIVATE_KEY: string
    }
}

const treeFile: string = "./docs/static/contract/tree.json"

const abi: AbiItem[] = contractInfo.TwinRegistry.abi as AbiItem[];
let local_ledger = new Web3(contractInfo.TwinRegistry.node);
const twinStore = new local_ledger.eth.Contract(abi, contractInfo.TwinRegistry.address);
const account = local_ledger.eth.accounts.privateKeyToAccount(process.env.DLT_PRIVATE_KEY);

// const publicAbi: AbiItem[] = contractInfo.RootHashRegistry.abi as AbiItem[];
// let public_ledger = new Web3(contractInfo.RootHashRegistry.node);
// const rootStore = new public_ledger.eth.Contract(publicAbi, contractInfo.RootHashRegistry.address);

function buildMerkleTree(hashes: string[][]) {
    return StandardMerkleTree.of(hashes, ["bytes32"]);
}

function submitRootHash(hashes: string[][]) {
    for (let hash of hashes) {
        console.log(hash);
    }
    const tree = buildMerkleTree(hashes)
    twinStore.methods.setRootHash(tree.root).send({ from: account.address })
        .then(function (result) {
            console.log("Submitted root hash:", tree.root);
            console.log("Transaction hash:", result.transactionHash);
            fs.writeFileSync(treeFile, JSON.stringify(tree.dump(), null, 4));
            console.log("Updated tree:", treeFile)
        })
}

async function getTwinHashes() {
    let results: any[] = await twinStore.methods.getTwins().call();
    let hashes: string[][] = [];
    for (let twin of results) {
        hashes.push([twin.hash]);
    }
    return hashes;
}

getTwinHashes().then((hashes) => {
    submitRootHash(hashes);
})
