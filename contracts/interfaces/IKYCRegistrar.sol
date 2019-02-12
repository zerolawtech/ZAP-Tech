pragma solidity >=0.4.24<0.5.0;

interface IKYCRegistrar {
	function isPermitted(address _addr) public view returns (bool);

	function isPermittedID(bytes32 _id) public view returns (bool);

	function addAuthority(
		address[] _addr,
		uint16[] _countries,
		uint32 _threshold
	) external  returns (bool);

	function setAuthorityThreshold(bytes32 _id, uint32 _threshold)
		external
		returns (bool);

	function setAuthorityCountries(bytes32 _id, uint16[] _countries, bool _auth)
		external
		returns (bool);

	function setAuthorityRestriction(bytes32 _id, bool _permitted)
		external
		returns (bool);

	function addInvestor(
		bytes32 _id,
		uint16 _country,
		bytes3 _region,
		uint8 _rating,
		uint40 _expires,
		address[] _addr
	) external returns (bool);

	function updateInvestor(
		bytes32 _id,
		bytes3 _region,
		uint8 _rating,
		uint40 _expires
	) external returns (bool);

	function setInvestorRestriction(bytes32 _id, bool _permitted)
		external
		returns (bool);

	function setInvestorAuthority(bytes32[] _id, bytes32 _authID)
		external
		returns (bool);

	function registerAddresses(bytes32 _id, address[] _addr)
		external
		returns (bool);

	function restrictAddresses(bytes32 _id, address[] _addr)
		external
		returns (bool);

	function getInvestor(address _addr)
		external
		view
		returns (bytes32 _id, bool _allowed, uint8 _rating, uint16 _country);

	function getInvestorByID(bytes32 _id)
		external
		view
		returns (bool _allowed, uint8 _rating, uint16 _country);

	function getInvestors(address _from, address _to)
		external
		view
		returns (
		bytes32[2] _id,
		bool[2] _allowed,
		uint8[2] _rating,
		uint16[2] _country
	);

	function getInvestorsByID(bytes32 _fromID, bytes32 _toID)
		external
		view
		returns (bool[2] _allowed, uint8[2] _rating, uint16[2] _country);

	function isRegistered(bytes32 _id) external view returns (bool);

	function getID(address _addr) external view returns (bytes32);

	function getRating(bytes32 _id) external view returns (uint8);

	function getRegion(bytes32 _id) external view returns (bytes3);

	function getCountry(bytes32 _id) external view returns (uint16);

	function getExpires(bytes32 _id) external view returns (uint40);

	function generateID(string _idString) external pure returns (bytes32);
}
