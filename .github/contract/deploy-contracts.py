import os
import json
from typing import Type

from web3 import Web3
from web3.contract.contract import Contract
from eth_account.signers.local import LocalAccount
import solcx

DLT_TYPE = os.environ["DLT_TYPE"]
DLT_GAS_PROVIDED = int(os.environ["DLT_GAS_PROVIDED"])

DLT_LOCAL_HTTP_NODE = os.environ["DLT_HTTP_NODE"]
DLT_LOCAL_PRIVATE_KEY = os.environ["DLT_PRIVATE_KEY"]
DLT_PUBLIC_HTTP_NODE = os.environ["DLT_PUBLIC_HTTP_NODE"]
DLT_PUBLIC_PRIVATE_KEY = os.environ["DLT_PUBLIC_PRIVATE_KEY"]

CONTRACT_FOLDER = "./.github/contract"
CONTRACT_INFO_FILE = "./docs/static/contract/contract-info.json"


class DLTContract:
    TYPE: str = DLT_TYPE
    GAS_PROVIDED: int = DLT_GAS_PROVIDED
    INFO_FILE: str = CONTRACT_INFO_FILE
    FOLDER: str = CONTRACT_FOLDER
    VERSION: str = "v0.8.0"
    solcx.install_solc("v0.8.0")

    def __init__(self, http_node: str, private_key: str, name: str) -> None:
        self.http_node = http_node
        provider = Web3.HTTPProvider(http_node)
        self.dlt = Web3(provider)
        self.account: LocalAccount = self.dlt.eth.account.from_key(private_key)

        if not self.dlt.is_connected():
            raise ConnectionError("Could not connect to DLT Provider:", provider)

        self.name = name
        self.path = f"{self.FOLDER}/{name}.sol"

    def compile(self) -> Type[Contract]:
        # Compile Solidity source code
        compiled_sol = solcx.compile_files(self.path)

        contract_interface = compiled_sol[f"{self.path}:{self.name}"]

        self.abi = contract_interface["abi"]
        """ with open(self.abi_path, "w") as abi_file:
            json.dump(contract_interface["abi"], abi_file, indent=4) """

        # Create and return the contract
        return self.dlt.eth.contract(
            abi=contract_interface["abi"], bytecode=contract_interface["bin"]
        )

    def deploy(self, contract: Type[Contract] | None = None) -> None:
        if not contract:
            contract = self.compile()

        # Construct transaction
        transaction = contract.constructor().build_transaction(
            {
                "from": self.account.address,
                "nonce": self.dlt.eth.get_transaction_count(self.account.address),
            }
        )

        # Sign transaction
        signed_transaction = self.dlt.eth.account.sign_transaction(
            transaction, self.account.key
        )

        # Deploy the contract
        transaction_hash = self.dlt.eth.send_raw_transaction(
            signed_transaction.rawTransaction
        )
        transaction_receipt = self.dlt.eth.wait_for_transaction_receipt(
            transaction_hash
        )
        # Return the contract address
        self.address = str(transaction_receipt.contractAddress)  # type: ignore
        print(f"Deployed contract {self.name}:", self.address)

    def save_info(self) -> None:
        new_info = {
            "dltType": self.TYPE,
            "node": self.http_node,
            "minter": self.account.address,
            "address": self.address,
            "abi": self.abi,
        }
        with open(self.INFO_FILE) as info_file:
            info = json.load(info_file)
        info[self.name] = new_info
        with open(self.INFO_FILE, "w") as info_file:
            json.dump(info, info_file, indent=4)
        print("Contract info saved to file:", self.INFO_FILE)


def main() -> None:
    # First contract
    local_contract = DLTContract(
        DLT_LOCAL_HTTP_NODE, DLT_LOCAL_PRIVATE_KEY, "TwinRegistry"
    )
    # Compile and deploy the contract to blockchain
    local_contract.deploy()
    local_contract.save_info()

    # Second contract
    public_contract = DLTContract(
        DLT_PUBLIC_HTTP_NODE, DLT_PUBLIC_PRIVATE_KEY, "RootHashRegistry"
    )
    # Compile and deploy the contract to blockchain
    public_contract.deploy()
    public_contract.save_info()


if __name__ == "__main__":
    main()
