pragma solidity 0.4.25;

/** @title IDVerifier Interface
    @dev
        this is a minimal interface that can be used to interact with both
        IDVerifierOrg and IDVerifierRegistrar contracts
 */
interface IIDVerifier {
    event MemberRestriction (bytes32 indexed id, bool restricted, bytes32 indexed authority);
    event NewMember (bytes32 indexed id, uint16 indexed country, bytes3 region, uint8 rating, uint40 expires, bytes32 indexed authority);
    event RegisteredAddresses (bytes32 indexed id, address[] addr, bytes32 indexed authority);
    event RestrictedAddresses (bytes32 indexed id, address[] addr, bytes32 indexed authority);
    event UpdatedMember (bytes32 indexed id, bytes3 region, uint8 rating, uint40 expires, bytes32 indexed authority);

    function addMember (bytes32, uint16, bytes3, uint8, uint40, address[]) external returns (bool);
    function registerAddresses (bytes32, address[]) external returns (bool);
    function restrictAddresses (bytes32, address[]) external returns (bool);
    function setMemberRestriction (bytes32, bool) external returns (bool);
    function updateMember (bytes32, bytes3, uint8, uint40) external returns (bool);
    function generateID (string _idString) external pure returns (bytes32);
    function getCountry (bytes32 _id) external view returns (uint16);
    function getExpires (bytes32 _id) external view returns (uint40);
    function getID (address _addr) external view returns (bytes32);
    function getMember (address _addr) external view returns (bytes32 _id, bool _permitted, uint8 _rating, uint16 _country);
    function getMembers (address _from, address _to) external view returns (bytes32[2] _id, bool[2] _permitted, uint8[2] _rating, uint16[2] _country);
    function getRating (bytes32 _id) external view returns (uint8);
    function getRegion (bytes32 _id) external view returns (bytes3);
    function isPermitted (address _addr) external view returns (bool);
    function isPermittedID (bytes32) external view returns (bool);
    function isRegistered (bytes32 _id) external view returns (bool);
}
