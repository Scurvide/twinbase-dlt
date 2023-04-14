import os
import json
import secrets

import yaml
from web3 import Web3
from eth_account.signers.local import LocalAccount

DLT_TYPE = os.environ["DLT_TYPE"]
DLT_HTTP_NODE = os.environ["DLT_HTTP_NODE"]
DLT_PRIVATE_KEY = os.environ["DLT_PRIVATE_KEY"]
DLT_GAS_PROVIDED = int(os.environ["DLT_GAS_PROVIDED"])

DLT_PROVIDER = Web3.HTTPProvider(DLT_HTTP_NODE)

TWIN_DOCUMENT_FOLDERS = "./docs"
HASH_INFO_FILE = "hash-info.json"
HASH_ALGORITHM = "Keccak256"


def hash_text(input: str) -> str:
    """Return Keccak256 hash in string representation."""

    return Web3.keccak(text=input).hex()


def hash_json_file(document_path: str) -> str:
    """Hash given json document to hexstring."""

    with open(document_path) as file:
        json_string = file.read()

    # Return Keccak256 hash in string representation
    return hash_text(json_string)


def hash_requires_update(dlt: Web3, twin_hash: str, twin_hash_info_file: str) -> bool:
    """Check if twin document hash has changed from the one stored in DLT."""

    try:
        # Attempt to find transaction hash from transaction file
        with open(twin_hash_info_file) as hash_info:
            transaction_hash = json.load(hash_info)["transactionHash"]
        # Get transaction from DLT
        transaction = dlt.eth.get_transaction(transaction_hash)
        # Compare hashes
        if int(twin_hash, 16) == int(transaction["input"], 16):
            # Hash has not changed from DLT, no update needed
            return False
    except (FileNotFoundError, KeyError, ValueError):
        # File or hash not found, or hash is invalid
        pass
    # Hash requires an update
    return True


def save_transaction_info(
    twin_hash: str, transaction_hash: str, twin_hash_info_file: str
) -> None:
    """Save transaction information for later reference."""

    # Collect transaction info
    transaction_info = {
        "dlt": DLT_TYPE,
        "node": DLT_HTTP_NODE,
        "twinHashAlgorithm": HASH_ALGORITHM,
        "twinHash": twin_hash,
        "transactionHash": transaction_hash,
    }
    with open(twin_hash_info_file, "w+") as file:
        # Format and dump the transaction info to file
        json.dump(transaction_info, file, indent=4)


def submit_twin_hash_to_dlt(dlt: Web3, nonce: int, twin_hash: str) -> str:
    """Submit hash to DLT, returns transaction hash."""

    # Create an account helper with private key
    account: LocalAccount = dlt.eth.account.from_key(DLT_PRIVATE_KEY)

    # Create the transaction object
    transaction = {
        "to": None,  # This is a contract creation transaction, so there is no recipient
        "from": account.address,
        "gas": DLT_GAS_PROVIDED,
        "gasPrice": dlt.eth.gas_price,
        "nonce": nonce,
        "data": twin_hash,
    }

    # Sign the transaction with the account's private key
    signed_transaction = dlt.eth.account.sign_transaction(
        transaction, private_key=account.key
    )

    # Broadcast the transaction to the network
    transaction_hash = dlt.eth.send_raw_transaction(signed_transaction.rawTransaction)
    return transaction_hash.hex()


def salt_twin(twin_folder: str, salt: str) -> str:
    """Add salt as attribute to twin json and yaml documents,
    returns salted twin json file path."""

    twin_json = twin_folder + "/index.json"
    twin_yaml = twin_folder + "/index.yaml"

    # Add salt to twin json
    with open(twin_json) as json_file:
        twin_document = json.load(json_file)
    twin_document["salt"] = salt
    with open(twin_json, "w") as json_file:
        json.dump(twin_document, json_file, indent=4)

    # Add salt to twin yaml
    with open(twin_yaml, "w") as yaml_file:
        yaml.dump(
            twin_document,
            yaml_file,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )

    return twin_json


def main() -> None:
    # Connect to the DLT network
    dlt = Web3(DLT_PROVIDER)
    if not dlt.is_connected():
        raise ConnectionError("Could not connect to DLT Provider:", DLT_PROVIDER)

    # Get starting nonce
    account: LocalAccount = dlt.eth.account.from_key(DLT_PRIVATE_KEY)
    nonce: int = dlt.eth.get_transaction_count(account.address)

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

        # Generate hash to check if the twin has been modified
        twin_hash = hash_json_file(twin_document)

        # Construct path to twin's hash info file
        twin_hash_file = f"{twin_folder}/{HASH_INFO_FILE}"

        # Check if hash needs to be updated to the DLT
        if not hash_requires_update(dlt, twin_hash, twin_hash_file):
            print(f"Twin hash is unchanged from DLT, skipping: {twin_document}")
            continue

        # Add new salt to twin documents
        salt = hash_text("0x" + secrets.token_hex(32))
        salted_twin_document = salt_twin(twin_folder, salt)

        # Generate hash from the freshly salted document to be stored in the DLT
        salted_twin_hash = hash_json_file(salted_twin_document)

        # Submit hash to DLT
        print(f"Submitting twin document hash to DLT: {twin_document}")
        transaction_hash = submit_twin_hash_to_dlt(dlt, nonce, salted_twin_hash)
        nonce += 1  # Increment nonce for following transactions

        # Save transaction info to new hash file
        save_transaction_info(salted_twin_hash, transaction_hash, twin_hash_file)


if __name__ == "__main__":
    main()
