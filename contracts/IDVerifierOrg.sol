pragma solidity 0.4.25;

import "./bases/IDVerifier.sol";

import "./interfaces/IOrgCode.sol";

/** @title Simplified IDVerifier Contract for Single Org */
contract IDVerifierOrg is IDVerifierBase {

    IOrgCode public orgCode;

    /**
        @notice IDVerifier constructor
        @param _orgCode OrgCode contract address
     */
    constructor (IOrgCode _orgCode) public {
        orgCode = _orgCode;
    }

    /**
        @notice Check that the call originates from an approved authority
        @return bool success
     */
    function _onlyAuthority() internal returns (bool) {
        return orgCode.checkMultiSigExternal(
            msg.sender,
            keccak256(msg.data),
            msg.sig
        );
    }

    /**
        @notice Internal function to add new addresses
        @param _id member or authority ID
        @param _addr array of addresses
     */
    function _addAddresses(bytes32 _id, address[] _addr) internal {
        for (uint256 i; i < _addr.length; i++) {
            Address storage _inv = idMap[_addr[i]];
            /** If address was previous assigned to this member ID
                and is currently restricted - remove the restriction */
            if (_inv.id == _id && _inv.restricted) {
                _inv.restricted = false;
            /* If address has not had an member ID associated - set the ID */
            } else if (_inv.id == 0) {
                require(!orgCode.isAuthority(_addr[i])); // dev: auth address
                _inv.id = _id;
            /* In all other cases, revert */
            } else {
                revert(); // dev: known address
            }
        }
        emit RegisteredAddresses(_id, _addr, orgCode.getID(msg.sender));
    }

    /**
        @notice Add member to this verifier
        @dev
            Member ID is a hash formed via a concatenation of PII
            Country and region codes are based on the ISO 3166 standard
            https://sft-protocol.readthedocs.io/en/latest/data-standards.html
        @param _id Member ID
        @param _country Member country code
        @param _region Member region code
        @param _rating Member rating (accreditted, qualified, etc)
        @param _expires Record expiration in epoch time
        @param _addr Array of addresses to register to member
        @return bool success
    */
    function addMember(
        bytes32 _id,
        uint16 _country,
        bytes3 _region,
        uint8 _rating,
        uint40 _expires,
        address[] _addr
     )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        require(!orgCode.isAuthorityID(_id)); // dev: authority ID
        require(memberData[_id].country == 0); // dev: member ID
        require(_country > 0); // dev: country 0
        _setMember(0x00, _id, _country, _region, _rating, _expires);
        emit NewMember(
            _id,
            _country,
            _region,
            _rating,
            _expires,
            orgCode.getID(msg.sender)
        );
        _addAddresses(_id, _addr);
        return true;
    }

    /**
        @notice Update an member
        @dev Member country may not be changed as this will alter their ID
        @param _id Member ID
        @param _region Member region
        @param _rating Member rating
        @param _expires Record expiration in epoch time
        @return bool success
     */
    function updateMember(
        bytes32 _id,
        bytes3 _region,
        uint8 _rating,
        uint40 _expires
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        require(memberData[_id].country != 0); // dev: unknown ID
        _setMember(0x00, _id, 0, _region, _rating, _expires);
        emit UpdatedMember(
            _id,
            _region,
            _rating,
            _expires,
            orgCode.getID(msg.sender)
        );
        return true;
    }

    /**
        @notice Set or remove an member's restricted status
        @dev This modifies restriciton on all addresses attached to the ID
        @param _id Member ID
        @param _restricted Permission bool
        @return bool success
     */
    function setMemberRestriction(
        bytes32 _id,
        bool _restricted
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        require(memberData[_id].country != 0);
        memberData[_id].restricted = _restricted;
        emit MemberRestriction(_id, _restricted, orgCode.getID(msg.sender));
        return true;
    }

    /**
        @notice Register addresseses to an entity
        @dev
            Can be used to add new addresses or remove restrictions
            from already associated addresses
        @param _id Entity's ID
        @param _addr Array of addresses
        @return bool success
     */
    function registerAddresses(
        bytes32 _id,
        address[] _addr
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        _addAddresses(_id, _addr);
        return true;
    }

    /**
        @notice Flags addresses as restricted instead of removing them
        @dev
            Address associations can only be restricted, never fully removed.
            If an association were removed it would then be possible to attach
            the address to another ID which could allow for non-compliant transfers.
        @param _id Entity ID
        @param _addr Array of addresses
        @return bool success
     */
    function restrictAddresses(
        bytes32 _id,
        address[] _addr
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        for (uint256 i; i < _addr.length; i++) {
            require(idMap[_addr[i]].id == _id); // dev: wrong ID
            require(!idMap[_addr[i]].restricted); // dev: already restricted
            idMap[_addr[i]].restricted = true;
        }
        emit RestrictedAddresses(_id, _addr, orgCode.getID(msg.sender));
        return true;
    }

    /**
        @notice Check if an an member is permitted based on ID
        @param _id Member ID to query
        @return bool permission
     */
    function isPermittedID(bytes32 _id) public view returns (bool) {
        Member storage i = memberData[_id];
        if (i.restricted) return false;
        if (i.expires < now) return false;
        return true;
    }

}
