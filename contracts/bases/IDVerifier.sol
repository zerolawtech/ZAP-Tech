pragma solidity 0.4.25;

/**
    @title IDVerifierBase Abstract Base Contract
    @dev Methods in this ABC are defined in contracts that inherit IDVerifierBase
*/
contract IDVerifierBaseABC {

    function addMember(bytes32, uint16, bytes3, uint8, uint40, address[]) external returns (bool);
    function updateMember(bytes32, bytes3, uint8, uint40) external returns (bool);
    function setMemberRestriction(bytes32, bool) external returns (bool);
    function registerAddresses(bytes32, address[]) external returns (bool);
    function restrictAddresses(bytes32, address[]) external returns (bool);
    function isPermittedID(bytes32) public view returns (bool);

}

/**
    @title Verifier Base
    @dev Shared methods for IDVerifierOrg and IDVerifierRegistrar
*/
contract IDVerifierBase is IDVerifierBaseABC {

    struct Address {
        bytes32 id;
        bool restricted;
    }

    struct Member {
        uint8 rating;
        uint16 country;
        uint40 expires;
        bool restricted;
        bytes3 region;
        bytes32 authority;
    }

    mapping (address => Address) idMap;
    mapping (bytes32 => Member) memberData;

    event NewMember(
        bytes32 indexed id,
        uint16 indexed country,
        bytes3 region,
        uint8 rating,
        uint40 expires,
        bytes32 indexed authority
    );
    event UpdatedMember(
        bytes32 indexed id,
        bytes3 region,
        uint8 rating,
        uint40 expires,
        bytes32 indexed authority
    );
    event MemberRestriction(
        bytes32 indexed id,
        bool restricted,
        bytes32 indexed authority
    );
    event RegisteredAddresses(
        bytes32 indexed id,
        address[] addr,
        bytes32 indexed authority
    );
    event RestrictedAddresses(
        bytes32 indexed id,
        address[] addr,
        bytes32 indexed authority
    );

    /**
        @notice Internal method to set member values
        @param _authID Authority ID
        @param _id Member ID
        @param _country Member country code
        @param _region Member region code
        @param _rating Member rating (accreditted, qualified, etc)
        @param _expires Record expiration in epoch time
    */
    function _setMember(
        bytes32 _authID,
        bytes32 _id,
        uint16 _country,
        bytes3 _region,
        uint8 _rating,
        uint40 _expires
    )
        internal
    {
        Member storage i = memberData[_id];
        if (i.country == 0) {
            i.country = _country;
        }
        if (i.rating != _rating) {
            i.rating = _rating;
        }
        require(i.rating > 0); // dev: rating 0
        if (i.region != _region) {
            i.region = _region;
        }
        if (i.expires != _expires) {
            i.expires = _expires;
        }
        if (i.authority != _authID) {
            i.authority = _authID;
        }
    }

    /**
        @notice Fetch member information using an address
        @dev
            This call increases gas efficiency around share transfers
            by minimizing the amount of calls to the verifier
        @param _addr Address to query
        @return bytes32 member ID
        @return bool member permission from isPermitted()
        @return uint8 member rating
        @return uint16 member country code
     */
    function getMember(
        address _addr
    )
        external
        view
        returns (
            bytes32 _id,
            bool _permitted,
            uint8 _rating,
            uint16 _country
        )
    {
        _id = idMap[_addr].id;
        Member storage i = memberData[_id];
        require(i.country != 0, "Address not registered");
        return (_id, isPermitted(_addr), i.rating, i.country);
    }

    /**
        @notice Use addresses to fetch information on 2 members
        @dev
            This call is increases gas efficiency around share transfers
            by minimizing the amount of calls to the verifier.
        @param _from first address to query
        @param _to second address to query
        @return bytes32 array of member ID
        @return bool array - Member permission from isPermitted()
        @return uint8 array of member ratings
        @return uint16 array of member country codes
     */
    function getMembers(
        address _from,
        address _to
    )
        external
        view
        returns (
            bytes32[2] _id,
            bool[2] _permitted,
            uint8[2] _rating,
            uint16[2] _country
        )
    {
        Member storage f = memberData[idMap[_from].id];
        require(f.country != 0, "Sender not Registered");
        Member storage t = memberData[idMap[_to].id];
        require(t.country != 0, "Receiver not Registered");
        return (
            [idMap[_from].id, idMap[_to].id],
            [isPermitted(_from), isPermitted(_to)],
            [f.rating,t.rating],
            [f.country, t.country]
        );
    }

    /**
        @notice Returns true if an ID is registered in this contract
        @param _id member ID
        @return bool
     */
    function isRegistered(bytes32 _id) external view returns (bool) {
        return memberData[_id].country != 0;
    }

    /**
        @notice Fetch member ID from an address
        @dev
            This cannot revert on fail because OrgCode may call multiple
            verifier contracts. A response of 0x00 is means the address is
            not registered.
        @param _addr Address to query
        @return bytes32 member ID
     */
    function getID(address _addr) external view returns (bytes32) {
        return idMap[_addr].id;
    }

    /**
        @notice Fetch member rating from an ID
        @dev If the member is unknown the call will throw
        @param _id Member ID
        @return uint8 rating code
     */
    function getRating(bytes32 _id) external view returns (uint8) {
        require (memberData[_id].country != 0);
        return memberData[_id].rating;
    }

    /**
        @notice Fetch member region from an ID
        @dev If the member is unknown the call will throw
        @param _id Member ID
        @return bytes3 region code
     */
    function getRegion(bytes32 _id) external view returns (bytes3) {
        require (memberData[_id].country != 0);
        return memberData[_id].region;
    }

    /**
        @notice Fetch member country from an ID
        @dev If the member is unknown the call will throw
        @param _id Member ID
        @return string
     */
    function getCountry(bytes32 _id) external view returns (uint16) {
        require (memberData[_id].country != 0);
        return memberData[_id].country;
    }

    /**
        @notice Fetch member KYC expiration from an ID
        @dev If the member is unknown the call will throw
        @param _id Member ID
        @return uint40 expiration epoch time
     */
    function getExpires(bytes32 _id) external view returns (uint40) {
        require (memberData[_id].country != 0);
        return memberData[_id].expires;
    }

    /**
        @notice Check if an an member and address are permitted
        @param _addr Address to query
        @return bool permission
     */
    function isPermitted(address _addr) public view returns (bool) {
        if (idMap[_addr].restricted) return false;
        return isPermittedID(idMap[_addr].id);
    }

    /**
        @notice Generate a unique member ID
        @dev https://sft-protocol.readthedocs.io/en/latest/data-standards.html
        @param _idString ID string to generate hash from
        @return bytes32 member ID hash
     */
    function generateID(string _idString) external pure returns (bytes32) {
        return keccak256(abi.encodePacked(_idString));
    }

}
