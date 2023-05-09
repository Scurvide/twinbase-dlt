import os
import json
import secrets

import yaml
from web3 import Web3
from web3.contract.contract import Contract
from eth_account.signers.local import LocalAccount

DLT_TYPE = os.environ["DLT_TYPE"]
DLT_GAS_PROVIDED = int(os.environ["DLT_GAS_PROVIDED"])
DLT_PRIVATE_KEY = os.environ["DLT_PRIVATE_KEY"]

TWIN_DOCUMENT_FOLDERS = "./docs"
CONTRACT_INFO_FILE = "./docs/static/contract/contract-info.json"
CONTRACT_NAME = "TwinRegistry"


def hash_text(input: str) -> str:
    """Return Keccak256 hash in string representation."""

    return Web3.keccak(text=input).hex()


def twin_requires_update(contract: Contract, twin_document_path: str) -> bool:
    """Check if twin document hash has changed from the one stored in ledger."""

    with open(twin_document_path) as twin_json:
        twin_hash = hash_text(twin_json.read())
        twin_json.seek(0)
        twin_id = json.load(twin_json)["dt-id"]

    try:
        # Get twin from ledger
        dlt_twin = contract.functions.getTwin(twin_id).call()
        # Compare hashes
        if int(twin_hash, 16) == int(dlt_twin[1].hex(), 16):
            # Twin hash unchanged from ledger
            return False
    except ValueError:
        # Twin does not exist in ledger
        pass

    # Twin hash requires an update
    return True


def add_twin_to_ledger(
    dlt: Web3, contract: Contract, nonce: int, twin_json: str
) -> str:
    """Submit hash to DLT, returns transaction hash."""

    # Get account from private key
    account: LocalAccount = dlt.eth.account.from_key(DLT_PRIVATE_KEY)

    # Get twin id and hash
    twin_id = json.loads(twin_json)["dt-id"]
    twin_hash = hash_text(twin_json)

    # Create the transaction object
    transaction = contract.functions.postTwinHash(twin_id, twin_hash).build_transaction(
        {
            "from": account.address,
            "gas": DLT_GAS_PROVIDED,
            "nonce": nonce,  # type: ignore
        }
    )

    # Sign the transaction with the account's private key
    signed_transaction = dlt.eth.account.sign_transaction(
        transaction, private_key=account.key
    )

    # Broadcast the transaction to the network
    transaction_hash = dlt.eth.send_raw_transaction(signed_transaction.rawTransaction)
    transaction_receipt = dlt.eth.wait_for_transaction_receipt(transaction_hash)

    # If gas used is the same as gas provided,
    # gas has likely run out and transaction failed
    if transaction_receipt["gasUsed"] == DLT_GAS_PROVIDED:
        raise ValueError(
            "Out of gas!",
            "Increase gas provided if you want this transaction to succeed",
            f"DLT_GAS_PROVIDED={DLT_GAS_PROVIDED}",
        )

    return transaction_hash.hex()


def salt_twin(twin_folder: str) -> str:
    """Add salt as attribute to twin json and yaml documents,
    returns salted twin json."""

    salt = hash_text("0x" + secrets.token_hex(32))
    twin_json_path = twin_folder + "/index.json"
    twin_yaml_path = twin_folder + "/index.yaml"

    # Add salt to twin json
    with open(twin_json_path) as json_file:
        twin_document = json.load(json_file)
    twin_document["salt"] = salt
    twin_json = json.dumps(twin_document, indent=4)
    with open(twin_json_path, "w") as json_file:
        json_file.write(twin_json)

    # Add salt to twin yaml
    with open(twin_yaml_path, "w") as yaml_file:
        yaml.dump(
            twin_document,
            yaml_file,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

    return twin_json


def get_contract_info() -> dict:
    """Load contract info from file"""
    with open(CONTRACT_INFO_FILE) as info_file:
        contract_info = json.load(info_file)
    return contract_info[CONTRACT_NAME]


def main() -> None:
    # Load contract info from file
    contract_info = get_contract_info()

    # Connect to the DLT network
    provider = Web3.HTTPProvider(contract_info["node"])
    dlt = Web3(provider)
    if not dlt.is_connected():
        raise ConnectionError("Could not connect to DLT Provider:", provider)

    # Get account
    account: LocalAccount = dlt.eth.account.from_key(DLT_PRIVATE_KEY)
    if contract_info["minter"] != account.address:
        raise ValueError(
            "Given private key has no permissions to contract:", contract_info["name"]
        )

    # Get starting nonce
    nonce: int = dlt.eth.get_transaction_count(account.address)

    # Get contract instance
    contract = dlt.eth.contract(address=contract_info["address"], abi=contract_info["abi"])  # type: ignore

    # Loop through twin folders, collect hashes and write them to DLT
    for folder in os.listdir(TWIN_DOCUMENT_FOLDERS):
        twin_folder = f"{TWIN_DOCUMENT_FOLDERS}/{folder}"

        # Skipping non-folders and folders from the excluded list
        if not os.path.isdir(twin_folder) or folder in ("static", "new-twin"):
            continue

        # Ensure folder has a twin document in json
        twin_document = twin_folder + "/index.json"
        if not os.path.isfile(twin_document):
            raise FileNotFoundError(f"Twin is missing file: {twin_document}")

        # Check if twin hash needs to be update to the ledger
        if not twin_requires_update(contract, twin_document):
            print(f"Twin hash is unchanged from contract, skipping: {twin_document}")
            continue

        # Add new salt to twin documents in folder
        salted_twin_json = salt_twin(twin_folder)

        # Submit twin Json to ledger
        print(f"Submitting twin document hash to contract: {twin_document}")
        add_twin_to_ledger(dlt, contract, nonce, salted_twin_json)
        nonce += 1  # Increment nonce for following transactions


if __name__ == "__main__":
    main()
