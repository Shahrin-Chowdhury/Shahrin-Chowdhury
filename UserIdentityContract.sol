// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract UserIdentityContract {
    // Mapping to store if a Patient ID is already assigned
    mapping(string => bool) private assignedIds;
    
    // Mapping to store patient data hashes
    mapping(string => string) private patientDataHashes;
    
    // Mapping to store patient SSNs by patient ID
    mapping(string => string) private patientSSNs;
    
    // Mapping to store patient IDs by SSN for reverse lookup
    mapping(string => string) private ssnToPatientId;
    
    // Event to notify the assignment of a new patient ID
    event PatientIdAssigned(address indexed user, string patientId);
    
    // Event to notify the storage of patient data hash
    event DataHashStored(address indexed user, string patientId, string dataHash);
    
    // Event to notify the storage of patient SSN
    event SSNStored(address indexed user, string patientId, string ssn);
    
    // Function to generate a unique Patient ID
    function generatePatientId(uint256 randomNumber) public returns (string memory) {
        require(randomNumber >= 1 && randomNumber <= 999, "Random number out of range");
        
        // Generate the Patient ID
        string memory idNumber = _toThreeDigitString(randomNumber);
        string memory patientId = string(abi.encodePacked("P", idNumber));
        
        // Ensure the Patient ID is unique
        require(!assignedIds[patientId], "Patient ID already assigned");
        assignedIds[patientId] = true;
        
        // Emit the event to notify that a Patient ID was assigned
        emit PatientIdAssigned(msg.sender, patientId);
        
        return patientId;
    }
    
    // Function to store the hash of patient data
    function storeDataHash(string memory patientId, string memory dataHash) public {
        require(assignedIds[patientId], "Patient ID not assigned");
        
        // Store the data hash
        patientDataHashes[patientId] = dataHash;
        
        // Emit the event to notify that a data hash was stored
        emit DataHashStored(msg.sender, patientId, dataHash);
    }
    
    // Function to store the Social Security Number
    function storeSSN(string memory patientId, string memory ssn) public {
        require(assignedIds[patientId], "Patient ID not assigned");
        
        // Ensure the SSN is not already associated with another patient ID
        require(bytes(ssnToPatientId[ssn]).length == 0, "SSN already assigned to a patient ID");
        
        // Store the SSN and map SSN to Patient ID
        patientSSNs[patientId] = ssn;
        ssnToPatientId[ssn] = patientId;
        
        // Emit the event to notify that an SSN was stored
        emit SSNStored(msg.sender, patientId, ssn);
    }
    
    // Public view function to check if a Patient ID is assigned
    function isPatientIdAssigned(string memory patientId) public view returns (bool) {
        return assignedIds[patientId];
    }

    // Public view function to get patient data hash
    function getDataHash(string memory patientId) public view returns (string memory) {
        require(assignedIds[patientId], "Patient ID not assigned");
        return patientDataHashes[patientId];
    }
    
    // Public view function to get patient SSN by Patient ID
    function getSSN(string memory patientId) public view returns (string memory) {
        require(assignedIds[patientId], "Patient ID not assigned");
        return patientSSNs[patientId];
    }
    
    // Public view function to get Patient ID by SSN
    function getPatientIdBySSN(string memory ssn) public view returns (string memory) {
        require(bytes(ssnToPatientId[ssn]).length != 0, "SSN not assigned");
        return ssnToPatientId[ssn];
    }

    // Helper function to convert a number to a 3-digit string
    function _toThreeDigitString(uint256 number) private pure returns (string memory) {
        if (number < 10) {
            return string(abi.encodePacked("00", uint2str(number)));
        } else if (number < 100) {
            return string(abi.encodePacked("0", uint2str(number)));
        } else {
            return uint2str(number);
        }
    }

    // Helper function to convert uint256 to string
    function uint2str(uint256 _i) private pure returns (string memory _uintAsString) {
        if (_i == 0) {
            return "0";
        }
        uint256 j = _i;
        uint256 len;
        while (j != 0) {
            len++;
            j /= 10;
        }
        bytes memory bstr = new bytes(len);
        uint256 k = len;
        while (_i != 0) {
            k = k - 1;
            uint8 temp = (48 + uint8(_i % 10));
            bytes1 b1 = bytes1(temp);
            bstr[k] = b1;
            _i /= 10;
        }
        return string(bstr);
    }
}