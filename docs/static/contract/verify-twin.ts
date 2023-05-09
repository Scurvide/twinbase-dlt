import { StandardMerkleTree } from "@openzeppelin/merkle-tree";
import Web3 from "web3";
import { AbiItem } from 'web3-utils';
import { Contract } from "web3-eth-contract";

// import contractInfo from "./contract-info.json";

// const abi: AbiItem[] = contractInfo.TwinRegistry.abi as AbiItem[];
// const local_ledger = new Web3(contractInfo.TwinRegistry.node);
// const twinStore = new local_ledger.eth.Contract(abi, contractInfo.TwinRegistry.address);
// 
// const publicAbi: AbiItem[] = contractInfo.RootHashRegistry.abi as AbiItem[];
// const public_ledger = new Web3(contractInfo.RootHashRegistry.node);
// const rootStore = new public_ledger.eth.Contract(publicAbi, contractInfo.RootHashRegistry.address);

var twinStore: Contract;
var rootStore: Contract;

fetch("../static/contract/contract-info.json", { cache: "no-store" })
    .then((response) => response.json())
    .then((contractInfo) => {
        const abi = contractInfo.TwinRegistry.abi as AbiItem;
        const local_ledger = new Web3(contractInfo.TwinRegistry.node);
        twinStore = new local_ledger.eth.Contract(abi, contractInfo.TwinRegistry.address);

        const publicAbi = contractInfo.RootHashRegistry.abi as AbiItem;
        const public_ledger = new Web3(contractInfo.RootHashRegistry.node);
        rootStore = new public_ledger.eth.Contract(publicAbi, contractInfo.RootHashRegistry.address);
    });

/* const abi: AbiItem[] = contractInfo.TwinRegistry.abi as AbiItem[];
const local_ledger = new Web3(contractInfo.TwinRegistry.node);
const twinStore = new local_ledger.eth.Contract(abi, contractInfo.TwinRegistry.address);

const publicAbi: AbiItem[] = contractInfo.RootHashRegistry.abi as AbiItem[];
const public_ledger = new Web3(contractInfo.RootHashRegistry.node);
const rootStore = new public_ledger.eth.Contract(publicAbi, contractInfo.RootHashRegistry.address); */

function verify(twin: string) {
    const twinId: string = JSON.parse(twin)["dt-id"];
    const twinHash = Web3.utils.soliditySha3(twin) as string

    twinStore.methods.getTwin(twinId).call().then(
        function (result) {
            console.log("Twin:", result);
        }
    )
    twinStore.methods.verifyTwinHash(twinId, twinHash).call().then(
        function (result) {
            console.log("Verified:", result);
        }
    )
    twinStore.methods.getTwins().call().then(
        function (result) {
            console.log("Twins:", result);
        }
    )
}

async function getTwinHashes() {
    let results: any[] = twinStore.methods.getTwins().call();
    let hashes: string[][] = [];
    for (let twin of results) {
        hashes.push([twin.hash]);
    }
    return hashes;
}

function buildMerkleTree(hashes: string[][]) {
    return StandardMerkleTree.of(hashes, ["bytes32"]);
}

async function getMerkleProof(twinHash: string) {
    const tree = await fetch("../static/contract/tree.json", { cache: "no-store" })
        .then((response) => response.json())
        .then((tree) => StandardMerkleTree.load(tree))
    for (const [i, v] of tree.entries()) {
        if (v[0] === twinHash) {
            return tree.getProof(i);
        }
    }
}

async function verifyMerkleTree(twin: string) {
    const twinHash = Web3.utils.soliditySha3(twin) as string;
    const proof = await getMerkleProof(twinHash);
    console.log(twinHash);
    console.log(proof);

    // console.log("Root:", buildMerkleTree(hashes).root);
    console.log("Proof:", proof);
    console.log("Leaf hash:", twinHash);
    rootStore.methods.verifyHash(proof, twinHash).call().then(
        function (result) {
            console.log("Verified:", result);
        }
    )
}

function validateTwin() {
    console.log("Validating document...");

    document.getElementById("dlt-validate").hidden = true;
    document.getElementById("dlt-validating").hidden = false;

    fetch("./index.json", { cache: "no-store" })
        .then((response) => response.text())
        .then((twinJson) => {
            verify(twinJson);
            verifyMerkleTree(twinJson);
        })
}

const button = document.getElementById("dlt-validate-button");
if (button) {
    button.addEventListener("click", () => validateTwin());
}
