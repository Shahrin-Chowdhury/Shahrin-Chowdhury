from web3 import Web3
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ethereum Connection
web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))

if not web3.is_connected():
    print("Ethereum node connection failed.")
    exit()
else:
    print("Ethereum node connection successful.")

def print_block_details(transaction_hash):
    try:
        # Fetch the transaction receipt
        receipt = web3.eth.get_transaction_receipt(transaction_hash)
        if not receipt:
            print(f"Transaction receipt not found for hash: {transaction_hash}")
            return

        # Get the block number from the receipt
        block_number = receipt.blockNumber
        block = web3.eth.get_block(block_number, full_transactions=True)

        print(f"Block Number: {block_number}")
        print(f"Block Hash: {block['hash'].hex()}")
        print(f"Timestamp: {block['timestamp']}")
        print(f"Miner: {block['miner']}")
        print(f"Transaction Count in Block: {len(block['transactions'])}")

        # Print details for the specific transaction
        tx = web3.eth.get_transaction(transaction_hash)
        print(f"Transaction Hash: {tx['hash'].hex()}")
        print(f"From: {tx['from']}")
        print(f"To: {tx['to']}")
        print(f"Gas Used: {receipt.gasUsed}")

        # Print logs
        print(f"Logs:")
        for log in receipt.logs:
            # Convert the log object to a serializable dictionary
            log_data = {
                'address': log.address,
                'blockHash': log.blockHash.hex(),
                'blockNumber': log.blockNumber,
                'data': log.data.hex(),
                'logIndex': log.logIndex,
                'removed': log.removed,
                'topics': [topic.hex() for topic in log.topics],
                'transactionHash': log.transactionHash.hex(),
                'transactionIndex': log.transactionIndex
            }
            print(json.dumps(log_data, indent=2))
        
        # Optionally, if you want to parse and print specific event details:
        for log in receipt.logs:
            # Convert the log topics and data to a more readable format
            event_data = {
                'address': log.address,
                'blockHash': log.blockHash.hex(),
                'blockNumber': log.blockNumber,
                'data': log.data.hex(),
                'logIndex': log.logIndex,
                'removed': log.removed,
                'topics': [topic.hex() for topic in log.topics],
                'transactionHash': log.transactionHash.hex(),
                'transactionIndex': log.transactionIndex
            }
            print(f"Event: {event_data.get('topics')[0]}")  # Print first topic as event name
            print(f"User: {event_data.get('topics')[1]}")  # Print second topic as user
            print(f"Patient ID: {parse_patient_id_from_log(event_data.get('data'))}")  # Placeholder for custom parsing logic
            
    except Exception as e:
        print(f"Error occurred: {e}")

def parse_patient_id_from_log(data):
    # Placeholder for extracting Patient ID or other relevant information from the log data
    # This function needs to be implemented based on the actual log data structure
    return "P197"  # Example placeholder value

# Replace with the actual transaction hash you want to inspect
transaction_hash = '0x8554990605070a7258db2281a07bf75a169edbbe488f8e49629005acaa871a83'  # Replace with the actual transaction hash

# Execute the function
print_block_details(transaction_hash)