pragma solidity >=0.4.24 <0.5.0;

import "./open-zeppelin/SafeMath.sol";
import "./IssuingEntity.sol";
import "./components/NFTModular.sol";

/** Non-Fungible ERC20 Contract */
contract NFToken is NFTModular {

	using SafeMath for uint256;

	bytes32 public ownerID;
	IssuingEntity public issuer;

	string public name;
	string public symbol;
	uint256 public constant decimals = 0;
	uint256 public totalSupply;
	uint256 public authorizedSupply;

	uint48[281474976710656] tokens;
	mapping (uint48 => Range) rangeMap;
	mapping (address => Balance) balances;
	mapping(address => mapping (address => uint256)) allowed;

	struct Balance {
		uint48 balance;
		uint48[] ranges;
	}

	struct Range {
		address owner;
		uint48 stop;
		uint32 time;
		bytes2 tag;
	}

	event Approval(
		address indexed owner,
		address indexed spender,
		uint256 tokens
	);
	event Transfer(address indexed from, address indexed to, uint256 amount);
	event TransferRange(
		address indexed from,
		address indexed to,
		uint256 start,
		uint256 stop,
		uint256 amount
	);
	event RangeSet(
		bytes2 indexed tag,
		uint256 start,
		uint256 stop,
		uint32 time
	);
	event TotalSupplyChanged(
		address indexed owner,
		uint256 oldBalance,
		uint256 newBalance
	);
	event AuthorizedSupplyChanged(uint256 oldAuthorized, uint256 newAuthorized);

	modifier checkBounds(uint256 _idx) {
		require(_idx != 0, "Index cannot be 0");
		require(_idx <= totalSupply, "Index exceeds totalSupply");
		_;
	}

	/**
		@notice Security token constructor
		@dev Initially the total supply is credited to the issuer
		@param _issuer Address of the issuer's IssuingEntity contract
		@param _name Name of the token
		@param _symbol Unique ticker symbol
		@param _authorizedSupply Initial authorized token supply
	 */
	constructor(
		address _issuer,
		string _name,
		string _symbol,
		uint256 _authorizedSupply
	)
		public
	{
		issuer = IssuingEntity(_issuer);
		ownerID = issuer.ownerID();
		name = _name;
		symbol = _symbol;
		authorizedSupply = _authorizedSupply;
	}

	/**
		@notice Fetch circulating supply
		@dev Circulating supply = total supply - amount retained by issuer
		@return integer
	 */
	function circulatingSupply() external view returns (uint256) {
		return totalSupply.sub(balances[address(issuer)].balance);
	}

	/**
		@notice Fetch the amount retained by issuer
		@return integer
	 */
	function treasurySupply() external view returns (uint256) {
		return balances[address(issuer)].balance;
	}

	/**
		@notice ERC-20 balanceOf standard
		@param _owner Address of balance to query
		@return integer
	 */
	function balanceOf(address _owner) external view returns (uint48) {
		return balances[_owner].balance;
	}

	/**
		@notice Fetch information about a range
		@param _idx Token index number
		@return owner, start of range, stop of range, time restriction, tag
	 */
	function getRange(
		uint256 _idx
	)
		external
		view
		checkBounds(_idx)
		returns (
			address _owner,
			uint48 _start,
			uint48 _stop,
			uint32 _time,
			bytes2 _tag
		)
	{
		_start = _getPointer(_idx);
		Range storage r = rangeMap[_start];
		return (r.owner, _start, r.stop, r.time, r.tag);
	}

	/**
		@notice Fetch the token ranges owned by an address
		@param _owner Address to query
		@return Array of [(start, stop),..]
	 */
	function rangesOf(address _owner) external view returns (uint48[2][]) {
		Balance storage b = balances[_owner];
		uint256 _count;
		for (uint256 i; i < b.ranges.length; i++) {
			if (b.ranges[i] != 0) _count++;
		}
		uint48[2][] memory _ranges = new uint48[2][](_count);
		_count = 0;
		for (i = 0; i < b.ranges.length; i++) {
			if (b.ranges[i] == 0) continue;
			_ranges[_count] = [b.ranges[i], rangeMap[b.ranges[i]].stop];
			_count++;
		}
		return _ranges;
	}

	/**
		@notice ERC-20 allowance standard
		@param _owner Owner of the tokens
		@param _spender Spender of the tokens
		@return integer
	 */
	function allowance(
		address _owner,
		address _spender
	 )
		external
		view
		returns (uint256)
	{
		return allowed[_owner][_spender];
	}

	/**
		@notice View function to check if a transfer is permitted
		@dev If a transfer is not allowed, the function will throw
		@param _from Address of sender
		@param _to Address of recipient
		@param _value Amount being transferred
		@return bool success
	 */
	function checkTransfer(
		address _from,
		address _to, 
		uint256 _value
	)
		external
		view
		returns (bool)
	{
		/* Sending 0 balance is blocked to reduce logic around investor limits */
		_checkToSend(_from, [_from, _to], _value);
		return true;
	}


	/**
		@notice internal check of transfer permission before performing it
		@param _auth Address calling to initiate the transfer
		@param _addr Address of sender, recipient
		@param _value Amount being transferred
		@return ID of caller
		@return ID array of investors
		@return address array of investors 
		@return uint8 array of investor ratings
		@return uint16 array of investor countries
	 */
	function _checkToSend(
		address _auth,
		address[2] _addr,
		uint256 _value
	)
		internal
		returns (
			bytes32 _authID,
			bytes32[2] _id,
			address[2],
			uint8[2] _rating,
			uint16[2] _country,
			uint48[] _range
		)
	{
		require(_value > 0, "Cannot send 0 tokens");
		require(uint48(_value) == _value);
		(_authID, _id, _rating, _country) = issuer.checkTransfer(
			address(this),
			_auth,
			_addr[0],
			_addr[1],
			_value == balances[_addr[0]].balance,
			_value
		);
		(_addr, _range) = _checkTransfer(
			_addr,
			_authID,
			_id,
			_rating,
			_country,
			_value
		);
		return(_authID, _id, _addr, _rating, _country, _range);
	}

	/**
		@notice internal check of transfer permission
		@dev common logic for checkTransfer() and _checkToSend()
		@param _addr address array of investors 
		@param _authID ID of caller
		@param _id ID array of investor IDs
		@param _rating array of investor ratings
		@param _country array of investor countries
		@param _value Amount being transferred
		@return array of investor addresses
	 */
	function _checkTransfer(
		address[2] _addr,
		bytes32 _authID,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value
	)
		internal
		returns (
			address[2],
			uint48[] _range
		)
	{
		/* Issuer tokens are held at the IssuingEntity contract address */
		if (_id[0] == ownerID) {
			_addr[0] = address(issuer);
		}
		if (_id[1] == ownerID) {
			_addr[1] = address(issuer);
		}
		require(_addr[0] != _addr[1], "Cannot send to self");
		require(balances[_addr[0]].balance >= _value, "Insufficient Balance");
		/* bytes4 signature for token module checkTransfer() */
		_callModules(0x70aaf928, 0x00, abi.encode(
			_addr,
			_authID,
			_id,
			_rating,
			_country,
			_value
		));
		_range = _findTransferrableRanges(_addr, _authID, _id, _rating, _country, _value);
		return (_addr, _range);
	}

	
	function _findTransferrableRanges(
		address[2] _addr,
		bytes32 _authID,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value
	)
		internal
		returns (uint48[])
	{
		Balance storage b = balances[_addr[0]];
		uint256 _count;
		uint48[] memory _range = new uint48[](b.ranges.length);
		for (uint256 i; i < b.ranges.length; i++) {
			if(!_checkTime(b.ranges[i])) continue;
			if (_callModules(
				0x12345678,
				rangeMap[b.ranges[i]].tag,
				abi.encode(
					_addr,
					_authID,
					_id,
					_rating,
					_country,
					uint48[2]([b.ranges[i],r.stop])
				)
			)) {
				Range storage r = rangeMap[b.ranges[i]];
				_range[_count] = b.ranges[i];
				
				if (r.stop - _range[_count] >= _value) {
					return _range;
				}
				_value -= (r.stop - _range[_count]);
				_count++;
			}
		}
		revert("Insufficient transferable tokens");
	}


	/**
		@notice Modify authorized Supply
		@dev Callable by issuer or via module
		@param _value New authorized supply value
		@return bool
	 */
	function modifyAuthorizedSupply(uint256 _value) external returns (bool) {
		/* msg.sig = 0xc39f42ed */
		if (!_checkPermitted()) return false;
		require(_value >= totalSupply);
		/* bytes4 signature for token module modifyAuthorizedSupply() */
		_callModules(
			0xb1a1a455,
			0x00,
			abi.encode(address(this), totalSupply, _value)
		);
		emit AuthorizedSupplyChanged(totalSupply, _value);
		authorizedSupply = _value;
		return true;
	}

	/**
		@notice Mints new tokens
		@param _owner Address to assign new tokens to
		@param _value Number of tokens to mint
		@param _time Time restriction to apply to tokens
		@param _tag Tag to apply to tokens
		@return Bool success
	 */
	function mint(
		address _owner,
		uint48 _value,
		uint32 _time,
		bytes2 _tag
	)
		public
		returns (bool)
	{
		if (!_checkPermitted()) return false;
		require(_value > 0);
		require(totalSupply + _value > totalSupply);
		require(totalSupply + _value <= 2**48 - 2);
		require(_time == 0 || _time > now);
		require(_value > 0);
		issuer.checkTransfer(
			address(this),
			address(issuer),
			address(issuer),
			_owner,
			false,
			_value
		);
		uint48 _start = uint48(totalSupply + 1);
		uint48 _stop = _start + _value;
		if (_compareRanges(tokens[totalSupply], _owner, _time, _tag)) {
			/* merge with previous range */
			uint48 _pointer = tokens[totalSupply];
			rangeMap[_pointer].stop = _stop;
		} else {
			/* create new range */
			_addRangePointers(_start, _stop);
			rangeMap[_start] = Range(_owner, _stop, _time, _tag);
			balances[_owner].ranges.push(_start);
		}
		balances[_owner].balance += _value;
		totalSupply += _value;
		_modifyTotalSupply(_owner, _value);
		emit RangeSet(_tag, _start, _stop, _time);
		emit Transfer(0x00, msg.sender, _value);
		emit TransferRange(0x00, msg.sender, _start, _stop, _value);
		return true;
	}

	/**
		@notice Burns tokens
		@param _pointer Start index of range to burn
		@return Bool success
	 */
	function burn(
		uint48 _pointer
	)
		public
		returns (bool)
	{
		if (!_checkPermitted()) return false;
		require(tokens[_pointer] == _pointer);
		Range storage r = rangeMap[_pointer];
		require(r.owner != 0x00);
		_replaceInBalanceRange(r.owner, _pointer, 0);
		uint48 _value = r.stop - _pointer;
		totalSupply -= _value;
		balances[r.owner].balance -= _value;
		_modifyTotalSupply(r.owner, _value);
		emit Transfer(r.owner, 0x00, _value);
		emit TransferRange(r.owner, 0x00, _pointer, r.stop, _value);
		r.owner = 0x00;
		return true;
	}


	/**
		@notice Internal shared logic for minting and burning
		@param _owner Owner of the tokens
		@param _old Previous balance
		@return bool success
	 */
	function _modifyTotalSupply(address _owner, uint256 _old) internal returns (bool) {
		uint256 _new = balances[_owner].balance;
		(
			bytes32 _id,
			uint8 _rating,
			uint16 _country
		) = issuer.modifyTokenTotalSupply(_owner, _old, _new);
		/* bytes4 signature for token module totalSupplyChanged() */
		_callModules(
			0x741b5078,
			0x00,
			abi.encode(_owner, _id, _rating, _country, _old, _new)
		);
		emit TotalSupplyChanged(_owner, _old, _new);
		return true;
	}

	/**
		@notice Modifies a single range
		@dev If changes allow it, range will be merged with neighboring ranges
		@param _pointer Start index of range to modify
		@param _time New time restriction value
		@param _tag New tag value
		@return Bool success
	 */
	function modifyRange(
		uint48 _pointer,
		uint32 _time,
		bytes2 _tag
	)
		public
		checkBounds(_pointer)
		returns (bool)
	{
		require(tokens[_pointer] == _pointer);
		Range storage r = rangeMap[_pointer];
		require(r.owner != 0x00);
		require(_time == 0 || _time > now);
		if (_compareRanges(tokens[_pointer-1], r.owner, _time, _tag)) {
			/* merge with previous range */
			uint48 _prev = tokens[_pointer-1];
			_removeRangePointers(_prev, _pointer);
			_removeRangePointers(_pointer, r.stop);
			_addRangePointers(_prev, r.stop);
			_replaceInBalanceRange(r.owner, _pointer, 0);
			rangeMap[_prev].stop = r.stop;
			delete rangeMap[_pointer];
			r = rangeMap[_prev];
			_pointer = _prev;
		}
		if (_compareRanges(r.stop, r.owner, _time, _tag)) {
			/* merge with next range */
			uint48 _next = rangeMap[r.stop].stop;
			_removeRangePointers(r.stop, _next);
			_removeRangePointers(_pointer, r.stop);
			_addRangePointers(_pointer, _next);
			_replaceInBalanceRange(r.owner, r.stop, 0);
			delete rangeMap[r.stop];
			r.stop = _next;
		}
		rangeMap[_pointer].time = _time;
		rangeMap[_pointer].tag = _tag;
		emit RangeSet(_tag, _pointer, rangeMap[_pointer].stop, _time);
		return true;
	}


	/**
		@notice Modifies one or more many ranges
		@dev Whenever possible, ranges will be merged
		@param _start Start index
		@param _stop Stop index
		@param _time New time restriction value
		@param _tag New tag value
		@return Bool success
	 */
	function modifyRanges(
		uint48 _start,
		uint48 _stop,
		uint32 _time,
		bytes2 _tag
	)
		public
		checkBounds(_start)
		checkBounds(_stop-1)
		returns (bool)
	{
		require(_time == 0 || _time > now);
		uint48 _pointer = _getPointer(_stop);
		if (_pointer != _stop) {
			Range storage r = rangeMap[_pointer];
			if (r.tag != _tag || r.time != _time) {
				_splitRange(_stop);
			} else {
				/* merge with next */
				_stop = r.stop;
			}
		}
		_pointer = _getPointer(_start);
		if (_pointer != _start) {
			r = rangeMap[_pointer];
			if (r.tag != _tag || r.time != _time) {
				_splitRange(_start);
			} else {
				/* merge with previous */
				_start = _pointer;
			}
		}
		while (_start < _stop) {
			r = rangeMap[_start];
			if (r.stop < _stop && rangeMap[r.stop].owner == r.owner) {
				/* merge with next range */
				uint48 _next = rangeMap[r.stop].stop;
				_removeRangePointers(r.stop, _next);
				_removeRangePointers(_start, r.stop);
				_addRangePointers(_start, _next);
				_replaceInBalanceRange(r.owner, r.stop, 0);
				delete rangeMap[r.stop];
				r.stop = _next;
				continue;
			}
			if (r.tag != _tag) r.tag = _tag;
			if (r.time != _time) r.time = _time;
			emit RangeSet(_tag, _start, rangeMap[_start].stop, _time);
			_start = rangeMap[_start].stop;
		}
		return true;
	}

	/**
		@notice ERC-20 approve standard
		@dev
			Approval may be given to addresses that are not registered,
			but the address will not be able to call transferFrom()
		@param _spender Address being approved to transfer tokens
		@param _value Amount approved for transfer
		@return bool success
	 */
	function approve(address _spender, uint256 _value) external returns (bool) {
		require(_spender != address(this));
		require(_value == 0 || allowed[msg.sender][_spender] == 0);
		allowed[msg.sender][_spender] = _value;
		emit Approval(msg.sender, _spender, _value);
		return true;
	}

	/**
		@notice ERC-20 transfer standard
		@dev calls to _checkToSend() to verify permission before transferring
		@param _to Recipient
		@param _value Amount being transferred
		@return bool success
	 */
	function transfer(address _to, uint256 _value) external returns (bool) {
		(
			bytes32 _authID,
			bytes32[2] memory _id,
			address[2] memory _addr,
			uint8[2] memory _rating,
			uint16[2] memory _country,
			uint48[] memory _range
		) = _checkToSend(msg.sender, [msg.sender, _to], _value);
		_transfer(_authID, _id, _addr, _rating, _country, _range, uint48(_value));
		return true;
	}

	/**
		@notice ERC-20 transferFrom standard
		@dev This will transfer tokens starting from balance.ranges[0]
		@param _from Sender address
		@param _to Receipient address
		@param _value Number of tokens to send
		@return bool success
	 */
	function transferFrom(
		address _from,
		address _to,
		uint256 _value
	)
		external
		returns (bool)
	{
		/* If called by a module, the authority becomes the issuing contract. */
		/* msg.sig = 0x23b872dd */
		if (isPermittedModule(msg.sender, msg.sig)) {
			address _auth = address(issuer);
		} else {
			_auth = msg.sender;
		}
		(
			bytes32 _authID,
			bytes32[2] memory _id,
			address[2] memory _addr,
			uint8[2] memory _rating,
			uint16[2] memory _country,
			uint48[] memory _range
		) = _checkToSend(_auth, [_from, _to], _value);

		if (_id[0] != _id[1] && _authID != ownerID && _authID != _id[0]) {
			/*
				If the call was not made by the issuer or the sender and involves
				a change in ownership, subtract from the allowed mapping.
			*/
			require(allowed[_from][_auth] >= _value, "Insufficient allowance");
			allowed[_from][_auth] = allowed[_from][_auth].sub(_value);
		}
		_transfer(_authID, _id, _addr, _rating, _country, _range, uint48(_value));
		return true;
	}

	// /**
	// 	@notice transfer tokens with a specific index range
	// 	@param _to Receipient address
	// 	@return bool success
	//  */
	// function transferRange(
	// 	address _to,
	// 	uint48[2] _range
	// )
	// 	external
	// 	checkBounds(_range[0])
	// 	checkBounds(_range[1]-1)
	// 	returns (bool)
	// {
	// 	require(_range[0] < _range[1]);
	// 	uint48 _pointer = _getPointer(_range[1]-1);
	// 	require(msg.sender == rangeMap[_pointer].owner);
	// 	require(_pointer <= _range[0]);
	// 	require(_checkTime(_pointer));
	// 	uint48 _value = _range[1] - _range[0];
	// 	address[2] memory _addr = [msg.sender, _to];
		
	// 	/* issuer check transfer */
	// 	(
	// 		bytes32 _authID,
	// 		bytes32[2] memory _id,
	// 		uint8[2] memory _rating,
	// 		uint16[2] memory _country
	// 	) = issuer.checkTransfer(
	// 		address(this),
	// 		msg.sender,
	// 		msg.sender,
	// 		_addr[1],
	// 		_value == balances[msg.sender].balance,
	// 		_value
	// 	);

	// 	/* bytes4 signature for token module checkTransfer() */
	// 	_callModules(0x70aaf928, 0x00, abi.encode(
	// 		_addr,
	// 		_authID,
	// 		_id,
	// 		_rating,
	// 		_country,
	// 		_value
	// 	));

	// 	/* range check transfer */
	// 	require(_callModules(
	// 			0x12345678,
	// 			rangeMap[_pointer].tag,
	// 			abi.encode(
	// 				_addr,
	// 				_authID,
	// 				_id,
	// 				_rating,
	// 				_country,
	// 				_range
	// 			)
	// 		));
		
	// 	uint48[] memory _newRange = new uint48[](1);
	// 	_newRange[0] = _range[0];
	// 	_transfer(_authID, _id, _addr, _rating, _country, _newRange, _value);
	// 	return true;
	// }



	/**
		@notice shared logic for transfer and transferFrom
		
	 */
	function _transfer(
		bytes32,
		bytes32[2] memory _id,
		address[2] memory _addr,
		uint8[2] memory _rating,
		uint16[2] memory _country,
		uint48[] memory _range,
		uint48 _value
	) internal {
		Balance storage _from = balances[_addr[0]];
		Balance storage _to = balances[_addr[1]];
		require(_value <= _from.balance);
		_from.balance -= _value;
		_to.balance += _value;
		
		require(issuer.transferTokens(
			_id,
			_rating,
			_country,
			_value,
			[_from.balance == 0, _to.balance == _value]
		));

		_transferFromRange(_range, _addr, _id, _rating, _country, _value);
		emit Transfer(_addr[0], _addr[1], _value);
	}

	/**
		@notice Transfer tokens from a balance range array
		@param _range Balance range array
		@param _value Amount to transfer
		@return Remaining value
	 */
	function _transferFromRange(
		uint48[] _range,
		address[2] _addr,
		bytes32[2] _id,
		uint8[2] _rating,
		uint16[2] _country,
		uint48 _value
	)
		internal
		returns (uint48)
	{
		for (uint256 i; i < _range.length; i++) {
			if (_range[i] == 0) continue;
			uint48 _start = _range[i];
			uint48 _stop = rangeMap[_start].stop;
			uint48 _amount = _stop - _start;
			if (_value < _amount) {
				_stop -= _amount - _value;
				_value = 0;
			}
			else {
				_value -= _amount;
			}
			_transferRange(_start, _addr[0], _addr[1], _start, _stop);
			_callModules(
				0x12345678,
				rangeMap[_range[i]].tag,
				abi.encode(_addr, _id, _rating, _country, uint48[2]([_start, _stop]))
			);
			if (_value == 0) return;
		}
		revert();
	}

	/**
		@notice internal - transfer ownership of a single range of tokens
		@param _pointer Range array pointer
		@param _from Sender address
		@param _to Recipient address
		@param _start Start index of range
		@param _stop Stop index of range
	 */
	function _transferRange(
		uint48 _pointer,
		address _from,
		address _to,
		uint48 _start,
		uint48 _stop
	)
		internal
	{
		uint48 _rangeStop = rangeMap[_pointer].stop;
		uint48 _prev = tokens[_start-1];
		bytes2 _tag = rangeMap[_pointer].tag;
		emit TransferRange(_from, _to, _start, _stop, _stop-_start);
		
		if (_pointer == _start) {
			// touches both
			if (_rangeStop == _stop) {
				_replaceInBalanceRange(_from, _start, 0);
				bool _left = _compareRanges(_prev, _to, 0, _tag);
				bool _right = _compareRanges(_stop, _to, 0, _tag);
				// no join
				if (!_left && !_right) {
					_replaceInBalanceRange(_to, 0, _start);
					rangeMap[_pointer].owner = _to;
					return;
				}
				_removeRangePointers(_pointer, _stop);
				// join left
				if (!_right) {
					delete rangeMap[_pointer];
					rangeMap[_prev].stop = _stop;
					_addRangePointers(_prev, _stop);
					return;
				}
				// join right
				if (!_left) {
					_replaceInBalanceRange(_to, _stop, _start);
					rangeMap[_pointer] = Range(_to, rangeMap[_stop].stop, 0, _tag);
					_addRangePointers(_pointer, rangeMap[_stop].stop);
				// join both
				} else {
					_replaceInBalanceRange(_to, _stop, 0);
					delete rangeMap[_pointer];
					rangeMap[_prev].stop = rangeMap[_stop].stop;
					_removeRangePointers(_prev, _start);
					_removeRangePointers(_stop, rangeMap[_stop].stop);
				}
				delete rangeMap[_stop];
				return;
			}

			// touches left
			delete rangeMap[_pointer];
			_removeRangePointers(_start, _rangeStop);
			_replaceInBalanceRange(_from, _start, _stop);
			
			// same owner left
			if (_compareRanges(_prev, _to, 0, _tag)) {
				_removeRangePointers(_prev, _start);
				_start = _prev;
			} else {
				_replaceInBalanceRange(_to, 0, _start);
			}
			rangeMap[_start] = Range(_to, _stop, 0, _tag);
			_addRangePointers(_start, _stop);
			rangeMap[_stop] = Range(_from, _rangeStop, 0, _tag);
			_addRangePointers(_stop, _rangeStop);
			return;
		}

		// shared logic - touches right and touches nothing
		_removeRangePointers(_pointer, _rangeStop);
		rangeMap[_pointer].stop = _start;
		_addRangePointers(_pointer, _start);

		// touches right
		if (_rangeStop == _stop) {
			// same owner right
			if (_compareRanges(_stop, _to, 0, _tag)) {
				_replaceInBalanceRange(_to, _stop, _start);
				_removeRangePointers(_stop, rangeMap[_stop].stop);
				uint48 _next = rangeMap[_stop].stop;
				delete rangeMap[_stop];
				_stop = _next;
			} else {
				_replaceInBalanceRange(_to, 0, _start);
			}
			rangeMap[_start] = Range(_to, _stop, 0, _tag);
			_addRangePointers(_start, _stop);
			return;
		}

		//touches nothing
		_replaceInBalanceRange(_to, 0, _start);
		rangeMap[_start] = Range(_to, _stop, 0, _tag);
		_addRangePointers(_start, _stop);
		
		_replaceInBalanceRange(_from, 0, _stop);
		rangeMap[_stop] = Range(_from, _rangeStop, 0, _tag);
		_addRangePointers(_stop, _rangeStop);
	}

	/**
		@notice Checks if time restriction on a range has expired
		@param _pointer Range index
		@return bool time restriction < now
	 */
	function _checkTime(uint48 _pointer) internal returns (bool) {
		if (rangeMap[_pointer].time > now) return false;
		if (rangeMap[_pointer].time > 0) {
			rangeMap[_pointer].time = 0;
		}
		return true;
	}

	/**
		@notice Compares an existing range to a set of owner/time/tag values
		@dev Used when updating ranges to determine if a merge is possible
		@param _pointer Range index to compare against
		@param _owner New range owner
		@param _time New range time
		@param _tag New range tag
		@return equality boolean
	 */
	function _compareRanges(
		uint48 _pointer,
		address _owner,
		uint32 _time,
		bytes2 _tag
	)
		internal
		returns (bool)
	{
		Range storage r = rangeMap[_pointer];
		if (r.time > 0 && r.time < now) {
			r.time = 0;
		}
		return (r.owner == _owner && r.time == _time && r.tag == _tag);
	}

	/**
		@notice Splits a range
		@dev
			Called when a new tag is added, to prevent a balance range
			where some tokens are tagged differently from others
		@param _split Index to split the range at
	 */
	function _splitRange(uint48 _split) internal {
		if (tokens[_split] != 0) return;
		uint48 _pointer = _getPointer(_split);
		Range storage r = rangeMap[_pointer];
		uint48 _stop = r.stop;
		r.stop = _split;
		rangeMap[_split] = Range(r.owner, _stop, r.time, r.tag);
		_replaceInBalanceRange(r.owner, 0, _split);
		_removeRangePointers(_pointer, _stop);
		_addRangePointers(_pointer, _split);
		_addRangePointers(_split, _stop);
	}

	/**
		@notice internal - replace value in balance range array
		@param _addr Balance addresss
		@param _old Token index to remove
		@param _new Token index to add
	 */
	function _replaceInBalanceRange(
		address _addr,
		uint48 _old,
		uint48 _new
	)
		internal
	{
		uint48[] storage r = balances[_addr].ranges;
		for (uint256 i; i < r.length; i++) {
			if (r[i] == _old) {
				r[i] = _new;
				return;
			}
		}
		if (_new != 0) {
			r.push(_new);
		}
	}

	/**
		@notice Add pointers to the token range
		@param _start Start index of range
		@param _stop Stop index of range
	 */
	function _addRangePointers(uint48 _start, uint48 _stop) internal {
		tokens[_start] = _start;
		_stop -= 1;
		if (_start == _stop) return;
		tokens[_stop] = _start;
		uint256 _interval = 16;
		while (true) {
			uint256 i = (_stop / _interval * _interval);
			if (i == 0) return;
			_interval *= 16;
			if (i % _interval == 0) continue;
			if (i > _start) tokens[i] = _start;
		}
	}

	/**
		@notice Remove pointers from a range
		@dev
			Only called after all new range pointers have been added, to
			minimize storage costs.
		@param _start Start index of range
		@param _stop Stop index of range
	 */
	function _removeRangePointers(uint48 _start, uint48 _stop) internal {
		delete tokens[_start];
		_stop -= 1;
		if (_start == _stop) return;
		delete tokens[_stop];
		uint256 _interval = 16;
		while (true) {
			uint256 i = (_stop / _interval * _interval);
			if (i == 0) return;
			_interval *= 16;
			if (i % _interval == 0) continue;
			if (i > _start) {
				delete tokens[i];
			}
		}
	}

	/**
		@notice Find an array range pointer
		@dev
			Given a token index, this will iterate through the range
			and return the mapping pointer that the index is present within.
		@param _idx Token index
	 */
	function _getPointer(uint256 _idx) internal view returns (uint48) {
		uint256 i = _idx;
		uint256 _increment = 1;
		while (true) {
			if (tokens[i] != 0x00) return tokens[i];
			if (i % (_increment * 16) == 0) {
				_increment *= 16;
			}
			i += _increment;
		}
	}

	/**
		@notice Checks that a call comes from a permitted module or the issuer
		@dev If the caller is the issuer, requires multisig approval
		@return bool multisig approved
	 */
	function _checkPermitted() internal returns (bool) {
		if (isPermittedModule(msg.sender, msg.sig)) return true;
		require(issuer.isApprovedAuthority(msg.sender, msg.sig));
		return issuer.checkMultiSigExternal(msg.sig, keccak256(msg.data));
	}

}