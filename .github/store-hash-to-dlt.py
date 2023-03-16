import os
import json
import hashlib

from web3 import Web3
from web3.types import TxParams
from eth_account.signers.local import LocalAccount

DLT_TYPE = os.environ["DLT_TYPE"]
DLT_HTTP_NODE = os.environ["DLT_HTTP_NODE"]
DLT_PRIVATE_KEY = os.environ["DLT_PRIVATE_KEY"]

DLT_PROVIDER = Web3.HTTPProvider(DLT_HTTP_NODE)

TWIN_DOCUMENT_FOLDERS = "./docs"
HASH_INFO_FILE = "hash-info.json"


def hash_json_file(document_path: str) -> str:
    """MD5 hash given json document in minimized format, returns hash in string format."""

    with open(document_path) as file:
        document = json.load(file)
    # Sort and minimize the json to ensure the hashed document format is consistent
    minimized_json = json.dumps(document, sort_keys=True, separators=(",", ":"))
    # Encode to bytes
    json_bytes = minimized_json.encode("utf-8")
    # Return MD5 hash in string representation
    return "0x" + hashlib.md5(json_bytes).hexdigest()


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
        "twinHash": twin_hash,
        "transactionHash": transaction_hash,
    }
    with open(twin_hash_info_file, "w+") as file:
        # Format and dump the transaction info to file
        json.dump(transaction_info, file, indent=4)


def submit_twin_hash_to_dlt(dlt: Web3, twin_hash: str) -> str:
    """Submit hash to DLT, returns transaction hash."""

    # Create an account helper with private key
    account: LocalAccount = dlt.eth.account.from_key(DLT_PRIVATE_KEY)

    # Create the transaction object
    transaction: TxParams = {
        "from": account.address,
        "gasPrice": dlt.eth.gas_price,
        "nonce": dlt.eth.get_transaction_count(account.address),
        "data": twin_hash,  # type: ignore
    }

    # Estimate gas price
    gas_required = dlt.eth.estimate_gas(transaction)
    transaction["gas"] = gas_required * 2  # Ensure success with multiplier

    # Sign the transaction with the account's private key
    signed_transaction = dlt.eth.account.sign_transaction(
        transaction, private_key=account.key
    )

    # Broadcast the transaction to the network
    transaction_hash = dlt.eth.send_raw_transaction(signed_transaction.rawTransaction)
    return transaction_hash.hex()


def main() -> None:
    # Connect to the DLT network
    dlt = Web3(DLT_PROVIDER)
    if not dlt.is_connected():
        raise ConnectionError("Could not connect to DLT Provider:", DLT_PROVIDER)

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

        # Generate the hash that will be stored in the DLT
        twin_hash = hash_json_file(twin_document)

        # Construct path to twin's hash info file
        twin_hash_file = f"{twin_folder}/{HASH_INFO_FILE}"

        # Check if hash needs to be updated to the DLT
        if not hash_requires_update(dlt, twin_hash, twin_hash_file):
            print(f"Twin hash is unchanged from DLT, skipping: {twin_document}")
            continue

        print(f"Submitting twin document hash to DLT: {twin_document}")
        transaction_hash = submit_twin_hash_to_dlt(dlt, twin_hash)

        # Save transaction info to hash file for reference
        save_transaction_info(twin_hash, transaction_hash, twin_hash_file)


if __name__ == "__main__":
    main()
