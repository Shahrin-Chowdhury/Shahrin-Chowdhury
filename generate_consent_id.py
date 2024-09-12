from web3 import Web3
from eth_account import Account
from pymongo import MongoClient
import hashlib
import json
import random
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB Connection
client = MongoClient('mongodb://localhost:27017/')
db = client['ConsentofPatient']
collection = db['ConsentData']

print("MongoDB connection successful.")

# Ethereum Connection
web3 = Web3(Web3.HTTPProvider('http://localhost:7545'))

if not web3.is_connected():
    print("Ethereum node connection failed.")
    exit()
else:
    print("Ethereum node connection successful.")

# Contract Details (Replace these with your actual contract address and ABI)
user_identity_contract_address = '0x0e96a11Ff3eA9f57677E7Ee37ce560586E12CaB9'  # Replace with actual UserIdentityContract address
user_identity_contract_abi = json.loads('''[
    {
      "constant": true,
      "inputs": [
        {"name": "ssn", "type": "string"}
      ],
      "name": "getPatientIdBySSN",
      "outputs": [
        {"name": "", "type": "string"}
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {"name": "patientId", "type": "string"}
      ],
      "name": "getSSN",
      "outputs": [
        {"name": "", "type": "string"}
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    },
    {
      "constant": true,
      "inputs": [
        {"name": "patientId", "type": "string"}
      ],
      "name": "isPatientIdAssigned",
      "outputs": [
        {"name": "", "type": "bool"}
      ],
      "payable": false,
      "stateMutability": "view",
      "type": "function"
    }
  ]''')

consent_management_contract_address = '0x794fFEc8971ed627ffCd4F6D135441559020AD9D'  # Replace with actual ConsentManagementContract address
consent_management_contract_abi = json.loads('''[
    {
      "constant": false,
      "inputs": [
        {"name": "patientId", "type": "string"},
        {"name": "consentHashes", "type": "bytes32[18]"},
        {"name": "offChainDataLinks", "type": "string[18]"},
        {"name": "ssn", "type": "string"}
      ],
      "name": "createConsents",
      "outputs": [],
      "payable": false,
      "stateMutability": "nonpayable",
      "type": "function"
    }
  ]''')

user_identity_contract = web3.eth.contract(address=user_identity_contract_address, abi=user_identity_contract_abi)
consent_management_contract = web3.eth.contract(address=consent_management_contract_address, abi=consent_management_contract_abi)

# Use private key from environment variables
private_key = os.getenv('PRIVATE_KEY')
if not private_key:
    raise Exception("Private key not found in environment variables.")

account = Account.from_key(private_key)
print(f"Account loaded successfully. Address: {account.address}")

def compute_hash(data):
    """Compute SHA256 hash of the provided data."""
    return hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()

def get_patient_id_from_user_identity_contract(ssn):
    """Fetch PatientID from UserIdentityContract based on SSN."""
    try:
        patient_id = user_identity_contract.functions.getPatientIdBySSN(ssn).call()
        if patient_id:
            return patient_id
        else:
            print(f"No PatientID found for SSN {ssn}.")
            return None
    except Exception as e:
        print(f"Error fetching PatientID for SSN {ssn}: {e}")
        return None

def generate_consent_ids():
    try:
        # Retrieve consent data from MongoDB
        for patient in collection.find():
            ssn = patient.get('Social Security Number')  # Fetching 'Social Security Number' from MongoDB
            if not ssn:
                print(f"SSN missing for patient. Skipping entry.")
                continue

            # Get patient ID using SSN from smart contract
            patient_id = get_patient_id_from_user_identity_contract(ssn)
            if not patient_id:
                print(f"Skipping patient with missing PatientID for SSN: {ssn}")
                continue

            print(f"Processing patient with ID: {patient_id}")

            consent_hashes = []
            off_chain_data_links = []
            consent_ids = []

            # Collecting consent data
            for i in range(1, 19):  # Iterate over C1 to C18
                consent_data = {
                    'consent': patient.get(f'C{i}')
                }

                # Generate consent hash and convert it to bytes32 format
                consent_hash = compute_hash(consent_data)
                consent_hash_bytes = web3.keccak(text=consent_hash)  # Generate bytes32 hash
                consent_hashes.append(consent_hash_bytes)

                # Placeholder for off-chain data links (update this as necessary)
                off_chain_data_links.append("")

                # Generate a unique consent ID (e.g., C44, C239, etc.)
                consent_id = f"C{random.randint(1, 9999)}"
                consent_ids.append(consent_id)

                # Print each generated consent hash and ID
                print(f"Consent {i}: Hash={consent_hash}, ID={consent_id}")

            # Ensure there are exactly 18 consents
            if len(consent_hashes) != 18 or len(off_chain_data_links) != 18:
                print(f"Invalid consent data for patient {patient_id}.")
                continue

            # Debug: Print all consent hashes before sending to blockchain
            print(f"Generated consent hashes for patient {patient_id}: {consent_hashes}")

            # Generate transaction to store data on blockchain
            try:
                tx = consent_management_contract.functions.createConsents(
                    patient_id,
                    consent_hashes,
                    off_chain_data_links,
                    ssn  # Ensure the SSN is passed to the smart contract
                ).build_transaction({
                    'from': account.address,
                    'nonce': web3.eth.get_transaction_count(account.address),
                    'gas': 3000000,
                    'gasPrice': web3.to_wei('20', 'gwei')
                })

                # Sign and send the transaction
                signed_tx = web3.eth.account.sign_transaction(tx, private_key=private_key)
                tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)

                # Wait for transaction receipt
                receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
                if receipt.status == 1:  # Check for successful transaction
                    print(f"Successfully created consents for patient {patient_id}. Transaction hash: {tx_hash.hex()}")
                    print(f"Patient {patient_id} has been linked with 18 different consent IDs. Consent IDs: {', '.join(consent_ids)}")
                else:
                    print(f"Transaction failed for patient {patient_id} with hash: {tx_hash.hex()}")
            except Exception as tx_error:
                print(f"Transaction failed for patient {patient_id}: {str(tx_error)}")

    except Exception as e:
        print(f"Error occurred: {e}")

# Execute the function to generate and store consents
generate_consent_ids()