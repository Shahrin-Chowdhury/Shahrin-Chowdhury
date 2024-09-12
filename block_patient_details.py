from web3 import Web3
from eth_account import Account

# Connect to Ethereum
web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))

# Define the contract ABI and address (provide your actual ABI)
contract_address = '0x7B52cE21066191fc4100056115e6F1Db6B76D067'
contract_abi = [
    {
        "anonymous": False,
        "inputs": [
            {
                "indexed": True,
                "internalType": "address",
                "name": "user",
                "type": "address"
            },
            {
                "indexed": False,
                "internalType": "string",
                "name": "patientId",
                "type": "string"
            }
        ],
        "name": "PatientIdAssigned",
        "type": "event"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "randomNumber",
                "type": "uint256"
            }
        ],
        "name": "generatePatientId",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "patientId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "dataHash",
                "type": "string"
            }
        ],
        "name": "storeDataHash",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "patientId",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "ssn",
                "type": "string"
            }
        ],
        "name": "storeSSN",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

contract = web3.eth.contract(address=contract_address, abi=contract_abi)

def get_transaction_details(tx_hash):
    try:
        # Wait for the transaction receipt (block is mined)
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

        # Retrieve the block in which the transaction was included
        block = web3.eth.get_block(receipt.blockNumber)

        print(f"Block Number: {block.number}")
        print(f"Block Hash: {block.hash.hex()}")
        print(f"Timestamp: {block.timestamp}")
        print(f"Miner: {block.miner}")
        print(f"Transaction Count in Block: {len(block.transactions)}")

        # Details of the transaction
        transaction = web3.eth.get_transaction(tx_hash)
        print(f"Transaction Hash: {transaction.hash.hex()}")
        print(f"From: {transaction['from']}")
        print(f"To: {transaction['to']}")
        print(f"Gas Used: {receipt.gasUsed}")
        print(f"Logs: {receipt.logs}")

        # Access events/logs from the transaction
        if receipt.logs:
            for log in receipt.logs:
                try:
                    decoded_log = contract.events.PatientIdAssigned().process_log(log)
                    print(f"Event: PatientIdAssigned")
                    print(f"User: {decoded_log.args.user}")
                    print(f"Patient ID: {decoded_log.args.patientId}")
                except Exception as e:
                    print(f"Error decoding log: {e}")

    except Exception as e:
        print(f"Error retrieving transaction details: {e}")

if __name__ == "__main__":
    # Replace this with the actual transaction hash
    tx_hash = '0xe3e60a5f61bcbaaa71812ec55be7fc7170b7d14793342d37f8aa37e979058f66'

    if tx_hash:
        get_transaction_details(tx_hash)