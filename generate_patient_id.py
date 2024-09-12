from web3 import Web3
from eth_account import Account
from pymongo import MongoClient
import random
import hashlib
import json

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['PersonalInfoofPatient']
collection = db['Patientdata']

# Connect to Ethereum
web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))
contract_address = '0x0e96a11Ff3eA9f57677E7Ee37ce560586E12CaB9'.strip()

# ABI from UserIdentityContract.json (Updated ABI including hash storage function)
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

# Create contract instance
contract = web3.eth.contract(address=contract_address, abi=contract_abi)

# Use a private key from a Ganache account
private_key = '0x614c9d21bbf36fa1ecc3f5004643a3001b5e1fb984bbcfe31ac608d19c9ea4b9'
account = Account.from_key(private_key)

def compute_hash(data):
    """Compute SHA256 hash of the provided data."""
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def generate_patient_id(random_number):
    try:
        # Generate Patient ID
        tx = contract.functions.generatePatientId(random_number).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 3000000,
            'gasPrice': web3.to_wei('20', 'gwei')
        })
        
        signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"Transaction hash for Patient ID generation: {tx_hash.hex()}")

        # Wait for the transaction to be mined
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        if not receipt:
            print("No receipt received for the transaction.")
            return None

        # Check if the receipt contains logs and process them
        if receipt and receipt['logs']:
            for log in receipt['logs']:
                try:
                    decoded_log = contract.events.PatientIdAssigned().process_log(log)
                    if decoded_log and decoded_log.transactionHash == tx_hash:
                        patient_id = decoded_log.args.patientId
                        print(f"Patient ID assigned: {patient_id}")
                        return patient_id
                except Exception as e:
                    print(f"Error processing log: {e}")
        else:
            print("Patient ID event not found in the transaction receipt.")
            return None

    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def store_patient_data(patient_id, ssn, data_hash):
    try:
        # Store the data hash
        tx_store_hash = contract.functions.storeDataHash(patient_id, data_hash).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 3000000,
            'gasPrice': web3.to_wei('20', 'gwei')
        })
        
        signed_tx_store_hash = web3.eth.account.sign_transaction(tx_store_hash, private_key=private_key)
        tx_hash_store_hash = web3.eth.send_raw_transaction(signed_tx_store_hash.rawTransaction)
        
        # Wait for the data hash storing transaction to be mined
        receipt_store_hash = web3.eth.wait_for_transaction_receipt(tx_hash_store_hash)
        if receipt_store_hash:
            print(f"Data hash stored in the smart contract: {data_hash}")
        else:
            print("No receipt received for the data hash storing transaction.")
        
        # Store the SSN
        tx_store_ssn = contract.functions.storeSSN(patient_id, ssn).build_transaction({
            'from': account.address,
            'nonce': web3.eth.get_transaction_count(account.address),
            'gas': 3000000,
            'gasPrice': web3.to_wei('20', 'gwei')
        })
        
        signed_tx_store_ssn = web3.eth.account.sign_transaction(tx_store_ssn, private_key=private_key)
        tx_hash_store_ssn = web3.eth.send_raw_transaction(signed_tx_store_ssn.rawTransaction)
        
        # Wait for the SSN storing transaction to be mined
        receipt_store_ssn = web3.eth.wait_for_transaction_receipt(tx_hash_store_ssn)
        if receipt_store_ssn:
            print(f"SSN successfully stored in the smart contract.")
            print(f"Patient ID successfully stored in the smart contract.")
        else:
            print("No receipt received for the SSN storing transaction.")
        
    except Exception as e:
        print(f"Error occurred while storing patient data: {e}")

# Generate and store patient IDs in the smart contract
for patient in collection.find():
    patient_info = {
        'Name': patient['Name'],
        'SSN': patient.get('Social Security Number'),
        'OtherInfo': patient.get('OtherInfo', '')
    }
    ssn = patient.get('Social Security Number')
    if not ssn:
        print(f"SSN missing for patient: {patient['Name']}")
        continue

    random_number = random.randint(1, 999)
    patient_id = generate_patient_id(random_number)
    if patient_id:
        data_hash = compute_hash(patient_info)
        store_patient_data(patient_id, ssn, data_hash)
        print(f"Generated Patient ID for {patient['Name']}: {patient_id}")