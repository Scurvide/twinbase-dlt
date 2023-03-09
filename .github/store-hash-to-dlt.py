import os
from pprint import pprint

from web3 import Web3
from eth_account.signers.local import LocalAccount

DLT_PROVIDER = Web3.HTTPProvider("http://192.168.64.1:7545")
PRIVATE_KEY = os.environ["PRIVATE_KEY"]


def main() -> None:
    # Connect to the network
    web3 = Web3(DLT_PROVIDER)
    web3.eth.account.from_key
    if not web3.is_connected():
        raise ConnectionError("Could not connect to DLT Provider:", DLT_PROVIDER)

    web3.is_connected()
    return

    account: LocalAccount = web3.eth.account.from_key(PRIVATE_KEY)

    # Set the hash that will be stored in the blockchain
    hash_to_store = "0x0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

    # Create the transaction object
    transaction = {
        "to": None,  # This is a contract creation transaction, so there is no recipient
        "from": account.address,
        "gas": 100000,
        "gasPrice": web3.eth.gas_price,
        "nonce": web3.eth.get_transaction_count(account.address),
        "data": hash_to_store,
    }

    # Sign the transaction with the account's private key
    signed_transaction = web3.eth.account.sign_transaction(
        transaction, private_key=account.key
    )

    # Broadcast the transaction to the network
    transaction_hash = web3.eth.send_raw_transaction(signed_transaction.rawTransaction)
    receipt = web3.eth.wait_for_transaction_receipt(transaction_hash)

    pprint(receipt)
    pprint(web3.eth.get_transaction(transaction_hash))


if __name__ == "__main__":
    main()
