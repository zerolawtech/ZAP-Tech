pragma solidity >=0.4.24 <0.5.0;

import "./IssuingEntity.sol";

/** @title Simplified KYC Contract for Single Issuer */
contract KycIssuer {

	IssuingEntity public issuer;

	struct Address {
		bytes32 id;
		bool restricted;
	}

	struct Investor {
		uint8 rating;
		uint16 country;
		uint40 expires;
		bool restricted;
		bytes3 region;
	}

	mapping (address => Address) idMap;
	mapping (bytes32 => Investor) investorData;

	event NewInvestor(
		bytes32 indexed id,
		uint16 indexed country,
		bytes3 region,
		uint8 rating,
		uint40 expires,
		bytes32 indexed authority
	);
	event UpdatedInvestor(
		bytes32 indexed id,
		bytes3 region,
		uint8 rating,
		uint40 expires,
		bytes32 indexed authority
	);
	event InvestorRestriction(
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

	function _onlyAuthority() internal returns (bool) {
		return issuer.checkMultiSigExternal(
			msg.sender,
			keccak256(msg.data),
			msg.sig
		);
	}

	/**
		@notice KYC registrar constructor
		@param _owners Array of addresses for owning authority
		@param _threshold multisig threshold for owning authority
	 */
	constructor (address _issuer) public {
		issuer = IssuingEntity(_issuer);
	}

	/**
		@notice Internal function to add new addresses
		@param _id investor or authority ID
		@param _addr array of addresses
	 */
	function _addAddresses(bytes32 _id, address[] _addr) internal {
		for (uint256 i; i < _addr.length; i++) {
			Address storage _inv = idMap[_addr[i]];
			/** If address was previous assigned to this investor ID
				and is currently restricted - remove the restriction */
			if (_inv.id == _id && _inv.restricted) {
				_inv.restricted = false;
			/* If address has not had an investor ID associated - set the ID */
			} else if (_inv.id == 0) {
				_inv.id = _id;
			/* In all other cases, revert */
			} else {
				revert();
			}
		}
		emit RegisteredAddresses(_id, _addr, issuer.getID(msg.sender));
	}

	/**
		@notice Add investor to this registrar
		@dev
			Investor ID is a hash formed via a concatenation of PII
			Country and region codes are based on the ISO 3166 standard
			https://sft-protocol.readthedocs.io/en/latest/data-standards.html
		@param _id Investor ID
		@param _country Investor country code
		@param _region Investor region code
		@param _rating Investor rating (accreditted, qualified, etc)
		@param _expires Registry expiration in epoch time
		@param _addr Array of addresses to register to investor
		@return bool success
	*/
	function addInvestor(
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
		require(_rating > 0);
		require(_expires > now);
		investorData[_id] = Investor(
			_rating,
			_country,
			_expires,
			false,
			_region
		);
		emit NewInvestor(
			_id,
			_country,
			_region,
			_rating,
			_expires,
			issuer.getID(msg.sender)
		);
		_addAddresses(_id, _addr);
		return true;
	}

	/**
		@notice Update an investor
		@dev Investor country may not be changed as this will alter their ID
		@param _id Investor ID
		@param _region Investor region
		@param _rating Investor rating
		@param _expires Registry expiration in epoch time
		@return bool success
	 */
	function updateInvestor(
		bytes32 _id,
		bytes3 _region,
		uint8 _rating,
		uint40 _expires
	)
		external
		returns (bool)
	{
		if (!_onlyAuthority()) return false;
		require(investorData[_id].country != 0);
		Investor storage i = investorData[_id];
		i.region = _region;
		i.rating = _rating;
		i.expires = _expires;
		emit UpdatedInvestor(
			_id,
			_region,
			_rating,
			_expires,
			issuer.getID(msg.sender)
		);
		return true;
	}

	/**
		@notice Set or remove an investor's restricted status
		@dev This modifies restriciton on all addresses attached to the ID
		@param _id Investor ID
		@param _permitted Permission bool
		@return bool success
	 */
	function setInvestorRestriction(
		bytes32 _id,
		bool _permitted
	)
		external
		returns (bool)
	{
		if (!_onlyAuthority()) return false;
		require(investorData[_id].country != 0);
		investorData[_id].restricted = !_permitted;
		emit InvestorRestriction(_id, !_permitted, issuer.getID(msg.sender));
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
			the address to another ID which could allow for non-compliant token
			transfers.
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
			require(idMap[_addr[i]].id == _id);
			require(!idMap[_addr[i]].restricted);
			idMap[_addr[i]].restricted = true;
		}
		emit RestrictedAddresses(_id, _addr, issuer.getID(msg.sender));
		return true;
	}

	/**
		@notice Fetch investor information using an address
		@dev
			This call increases gas efficiency around token transfers
			by minimizing the amount of calls to the registrar
		@param _addr Address to query
		@return bytes32 investor ID
		@return bool investor permission from isPermitted()
		@return uint8 investor rating
		@return uint16 investor country code
	 */
	function getInvestor(
		address _addr
	)
		external
		view
		returns (
			bytes32 _id,
			bool _allowed,
			uint8 _rating,
			uint16 _country
		)
	{
		_id = idMap[_addr].id;
		Investor storage i = investorData[_id];
		require(i.country != 0, "Address not registered");
		return (_id, isPermitted(_addr), i.rating, i.country);
	}

	/**
		@notice Fetch investor information using an ID
		@dev
			This call increases gas efficiency around token transfers
			by minimizing the amount of calls to the registrar
		@param _id investor ID
		@return bool investor permission from isPermitted()
		@return uint8 investor rating
		@return uint16 investor country code
	 */
	function getInvestorByID(
		bytes32 _id
	)
		external
		view
		returns (
			bool _allowed,
			uint8 _rating,
			uint16 _country
		)
	{
		Investor storage i = investorData[_id];
		require(i.country != 0, "Address not registered");
		return (isPermittedID(_id), i.rating, i.country);
	}

	/**
		@notice Use addresses to fetch information on 2 investors
		@dev
			This call is increases gas efficiency around token transfers
			by minimizing the amount of calls to the registrar.
		@param _from first address to query
		@param _to second address to query
		@return bytes32 array of investor ID
		@return bool array - Investor permission from isPermitted()
		@return uint8 array of investor ratings
		@return uint16 array of investor country codes
	 */
	function getInvestors(
		address _from,
		address _to
	)
		external
		view
		returns (
			bytes32[2] _id,
			bool[2] _allowed,
			uint8[2] _rating,
			uint16[2] _country
		)
	{
		Investor storage f = investorData[idMap[_from].id];
		require(f.country != 0, "Sender not Registered");
		Investor storage t = investorData[idMap[_to].id];
		require(t.country != 0, "Receiver not Registered");
		return (
			[idMap[_from].id, idMap[_to].id],
			[isPermitted(_from), isPermitted(_to)],
			[f.rating,t.rating],
			[f.country, t.country]
		);
	}

	/**
		@notice Use IDs to fetch information on 2 investors
		@dev
			This call is increases gas efficiency around token transfers
			by minimizing the amount of calls to the registrar.
		@param _fromID first ID to query
		@param _toID second ID to query
		@return bool array - Investor permission from isPermitted()
		@return uint8 array of investor ratings
		@return uint16 array of investor country codes
	 */
	function getInvestorsByID(
		bytes32 _fromID,
		bytes32 _toID
	)
		external
		view
		returns (
			bool[2] _allowed,
			uint8[2] _rating,
			uint16[2] _country
		)
	{
		Investor storage f = investorData[_fromID];
		require(f.country != 0, "Sender not Registered");
		Investor storage t = investorData[_toID];
		require(t.country != 0, "Receiver not Registered");
		return (
			[isPermittedID(_fromID), isPermittedID(_toID)],
			[f.rating,t.rating],
			[f.country, t.country]
		);
	}

	/**
		@notice Returns true if an ID is registered in this contract
		@param _id investor ID
		@return bool
	 */
	function isRegistered(bytes32 _id) external view returns (bool) {
		return investorData[_id].country != 0;
	}

	/**
		@notice Fetch investor ID from an address
		@param _addr Address to query
		@return bytes32 investor ID
	 */
	function getID(address _addr) external view returns (bytes32) {
		return idMap[_addr].id;
	}

	/**
		@notice Fetch investor rating from an ID
		@dev If the investor is unknown the call will throw
		@param _id Investor ID
		@return uint8 rating code
	 */
	function getRating(bytes32 _id) external view returns (uint8) {
		require (investorData[_id].country != 0);
		return investorData[_id].rating;
	}

	/**
		@notice Fetch investor region from an ID
		@dev If the investor is unknown the call will throw
		@param _id Investor ID
		@return bytes3 region code
	 */
	function getRegion(bytes32 _id) external view returns (bytes3) {
		require (investorData[_id].country != 0);
		return investorData[_id].region;
	}

	/**
		@notice Fetch investor country from an ID
		@dev If the investor is unknown the call will throw
		@param _id Investor ID
		@return string
	 */
	function getCountry(bytes32 _id) external view returns (uint16) {
		require (investorData[_id].country != 0);
		return investorData[_id].country;
	}

	/**
		@notice Fetch investor KYC expiration from an ID
		@dev If the investor is unknown the call will throw
		@param _id Investor ID
		@return uint40 expiration epoch time
	 */
	function getExpires(bytes32 _id) external view returns (uint40) {
		require (investorData[_id].country != 0);
		return investorData[_id].expires;
	}

	/**
		@notice Check if an an investor and address are permitted
		@param _addr Address to query
		@return bool permission
	 */
	function isPermitted(address _addr) public view returns (bool) {
		if (idMap[_addr].restricted) return false;
		return isPermittedID(idMap[_addr].id);
	}

	/**
		@notice Check if an an investor is permitted based on ID
		@param _id Investor ID to query
		@return bool permission
	 */
	function isPermittedID(bytes32 _id) public view returns (bool) {
		Investor storage i = investorData[_id];
		if (i.restricted) return false;
		if (i.expires < now) return false;
		return true;
	}

	/**
		@notice Generate a unique investor ID
		@dev https://sft-protocol.readthedocs.io/en/latest/data-standards.html
		@param _idString ID string to generate hash from
		@return bytes32 investor ID hash
	 */
	function generateID(string _idString) external pure returns (bytes32) {
		return keccak256(abi.encodePacked(_idString));
	}

}
