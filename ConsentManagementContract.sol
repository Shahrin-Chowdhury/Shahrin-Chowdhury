// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "./UserIdentityContract.sol";

contract ConsentManagementContract {

    // Reference to the UserIdentityContract
    UserIdentityContract private userIdentityContract;

    // Structure to represent a consent decision
    struct Consent {
        bytes32 consentID;
        bytes32 consentHash;
        string offChainDataLink;
    }

    // Mapping to store consents by patientId and consentId
    mapping(string => mapping(bytes32 => Consent)) private consents;

    // Event declarations
    event ConsentCreated(address indexed user, string indexed patientId, bytes32 consentID, bytes32 consentHash, string offChainDataLink);

    // Constructor to set the UserIdentityContract address
    constructor(address _userIdentityContractAddress) {
        userIdentityContract = UserIdentityContract(_userIdentityContractAddress);
    }

    // Function to create and link 18 consent decisions to a patient
    function createConsents(string memory patientId, bytes32[18] calldata consentHashes, string[18] calldata offChainDataLinks, string memory ssn) external {
        // Ensure that the patientId is valid
        require(bytes(patientId).length > 0, "Invalid patientId");
        require(consentHashes.length == 18, "Must provide 18 consent hashes.");
        require(offChainDataLinks.length == 18, "Must provide 18 off-chain data links.");
        
        // Validate that the patient ID exists in the UserIdentityContract
        bool isAssigned = userIdentityContract.isPatientIdAssigned(patientId);
        require(isAssigned, "Patient ID not assigned");

        // Retrieve the SSN from UserIdentityContract
        string memory storedSSN = userIdentityContract.getSSN(patientId);
        require(keccak256(abi.encodePacked(storedSSN)) == keccak256(abi.encodePacked(ssn)), "SSN does not match");

        // Loop through each consent decision and store it on-chain
        for (uint8 i = 0; i < 18; i++) {
            // Generate a unique ConsentID for each consent decision using patientId and consentHash
            bytes32 consentID = keccak256(abi.encodePacked(patientId, consentHashes[i], block.timestamp, i));
            
            // Create the consent struct
            consents[patientId][consentID] = Consent({
                consentID: consentID,
                consentHash: consentHashes[i],
                offChainDataLink: offChainDataLinks[i]
            });
            
            // Emit event to notify about the creation of the consent
            emit ConsentCreated(msg.sender, patientId, consentID, consentHashes[i], offChainDataLinks[i]);
        }
    }

    // Function to retrieve a consent by patientId and consentId
    function getConsent(string memory patientId, bytes32 consentID) external view returns (bytes32, bytes32, string memory) {
        Consent memory consent = consents[patientId][consentID];
        require(consent.consentID != 0, "Consent not found.");
        return (consent.consentID, consent.consentHash, consent.offChainDataLink);
    }
}