import os
import json
import hashlib

from web3 import Web3
from eth_account.signers.local import LocalAccount

DLT_PROVIDER = Web3.HTTPProvider(os.environ["DLT_HTTP_PROVIDER"])
DLT_PRIVATE_KEY = os.environ["DLT_PRIVATE_KEY"]

TWIN_DOCUMENT = "./docs/index.json"
TRANSACTION_RECEIPT = "./docs/dlt-transaction-receipt.json"


def hash_json(document_path: str) -> str:
    """Hash given json document in minimized format with MD5, returns hash in string format."""
    with open(document_path) as file:
        document = json.load(file)
    # Sort and minimize the json to ensure the hashed document format is consistent
    minimized_json = json.dumps(document, sort_keys=True, separators=(",", ":"))
    # Encode to bytes
    json_bytes = minimized_json.encode("utf-8")
    # Return MD5 hash in string representation
    return "0x" + hashlib.md5(json_bytes).hexdigest()


def hash_changed(twin_document_hash: str) -> bool:
    """Check if twin document hash has changed from the latest stored in DLT."""
    # Attempt to find previous hash from transaction file
    try:
        with open(TRANSACTION_RECEIPT) as transaction:
            dlt_document_hash = json.load(transaction)["hash"]
    except (FileNotFoundError, KeyError):
        return True
    # Compare hashes
    if int(twin_document_hash, 16) == int(dlt_document_hash, 16):
        return False
    return True


def save_transaction_receipt(document_hash: str, receipt) -> None:
    """Save transaction information for later reference."""
    # Convert transaction object to json using encoder by Web3
    transaction_json = Web3.to_json(
        {
            "dlt": "eth",
            "provider": str(DLT_PROVIDER),
            "hash": document_hash,
            "receipt": receipt,
        }
    )
    with open(TRANSACTION_RECEIPT, "w+") as file:
        # Reload json, format, and dump the transaction to file
        json.dump(json.loads(transaction_json), file, indent=4)


def main() -> None:
    # Generate the hash that will be stored in the blockchain
    document_hash = hash_json(TWIN_DOCUMENT)

    # Check if hash needs to be updated
    if not hash_changed(document_hash):
        print("Twin document hash is unchanged, skipping.")
        return

    print("Submitting twin document hash to DLT.")

    # Connect to the network
    web3 = Web3(DLT_PROVIDER)

    if not web3.is_connected():
        raise ConnectionError("Could not connect to DLT Provider:", DLT_PROVIDER)

    account: LocalAccount = web3.eth.account.from_key(DLT_PRIVATE_KEY)

    # Create the transaction object
    transaction = {
        "to": None,  # This is a contract creation transaction, so there is no recipient
        "from": account.address,
        "gas": 100000,
        "gasPrice": web3.eth.gas_price,
        "nonce": web3.eth.get_transaction_count(account.address),
        "data": document_hash,
    }

    # Sign the transaction with the account's private key
    signed_transaction = web3.eth.account.sign_transaction(
        transaction, private_key=account.key
    )

    # Broadcast the transaction to the network
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    web3.eth.wait_for_transaction_receipt(transaction_hash)

    # Save transaction receipt to json file for reference
    save_transaction_receipt(
        document_hash, web3.eth.wait_for_transaction_receipt(transaction_hash)
    )


if __name__ == "__main__":
    main()
