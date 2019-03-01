pragma solidity >=0.4.24 <0.5.0;

import "./TokenBase.sol";

/**
	@title Non-Fungible SecurityToken 
	@dev
		Expands upon the ERC20 token standard
		https://theethereum.wiki/w/index.php/ERC20_Token_Standard
 */
contract NFToken is TokenBase  {

	uint48[281474976710656] tokens;
	mapping (uint48 => Range) rangeMap;
	mapping (address => Balance) balances;

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
		TokenBase(
			_issuer,
			_name,
			_symbol,
			_authorizedSupply
		)
	{
		return;
	}

	function _checkBounds(uint256 _idx) internal view {
		require(_idx != 0, "Index cannot be 0");
		require(_idx <= totalSupply, "Index exceeds totalSupply");
	}

	/**
		@notice ERC-20 balanceOf standard
		@param _owner Address of balance to query
		@return integer
	 */
	function balanceOf(address _owner) public view returns (uint256) {
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
		returns (
			address _owner,
			uint48 _start,
			uint48 _stop,
			uint32 _time,
			bytes2 _tag
		)
	{
		_checkBounds(_idx);
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
			_auth,
			_addr[0],
			_addr[1],
			_value == balances[_addr[0]].balance,
			_value
		);

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
		_callModules(
			0x70aaf928,
			0x00,
			abi.encode(_addr, _authID, _id, _rating, _country, _value)
		);
		_range = _findTransferrableRanges(
			_authID,
			_id,
			_addr,
			_rating,
			_country,
			_value
		);
		return (_authID, _id, _addr, _rating, _country, _range);
	}

	
	/**
		@notice Find ranges that are permitted to transfer
		@param _authID ID of calling authority
		@param _id Array of investor IDs
		@param _addr Investor address array
		@param _rating Investor rating array
		@param _country Investor country array
		@param _value Value of transfer
		@return dynamic array of range pointers that to transfer
	 */
	function _findTransferrableRanges(
		bytes32 _authID,
		bytes32[2] _id,
		address[2] _addr,
		uint8[2] _rating,
		uint16[2] _country,
		uint256 _value
	)
		internal
		returns (uint48[] _range)
	{
		Balance storage b = balances[_addr[0]];
		uint256 _count;
		_range = new uint48[](b.ranges.length);
		for (uint256 i; i < b.ranges.length; i++) {
			if(!_checkTime(b.ranges[i])) continue;
			/** hook point for NFToken.checkTransferRange() */
			if (_callModules(
				0x5a5a8ad8,
				rangeMap[b.ranges[i]].tag,
				abi.encode(
					_authID,
					_id,
					_addr,
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
		external
		returns (bool)
	{
		/* msg.sig = 0x15077ec8 */
		if (!_checkPermitted()) return false;
		require(_value > 0);
		require(totalSupply + _value > totalSupply);
		require(totalSupply + _value <= 2**48 - 2);
		require(_time == 0 || _time > now);
		require(_value > 0);
		issuer.checkTransfer(
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
			_setRangePointers(_start, _stop, _start);
			rangeMap[_start] = Range(_owner, _stop, _time, _tag);
			balances[_owner].ranges.push(_start);
		}
		uint48 _old = balances[_owner].balance;
		balances[_owner].balance += _value;
		totalSupply += _value;
		_modifyTotalSupply(_owner, _old);
		emit RangeSet(_tag, _start, _stop, _time);
		emit Transfer(0x00, msg.sender, _value);
		emit TransferRange(0x00, msg.sender, _start, _stop, _value);
		return true;
	}

	/**
		@notice Burns tokens
		@dev Canoot burn multiple ranges in a single call
		@param _start Start index of range to burn
		@param _stop Stop index of range to burn
		@return Bool success
	 */
	function burn(uint48 _start, uint48 _stop) external returns (bool) {
		/* msg.sig = 0x9a0d378b */
		if (!_checkPermitted()) return false;
		require(_stop > _start);
		uint48 _pointer = _getPointer(_stop-1);
		require(_pointer <= _start);
		address _owner = rangeMap[_pointer].owner;
		require(_owner != 0x00);
		if (rangeMap[_pointer].stop > _stop) {
			_splitRange(_stop);
		}
		if (_pointer < _start) {
			_splitRange(_start);
		}
		_replaceInBalanceRange(_owner, _start, 0);
		uint48 _value = _stop - _start;
		totalSupply -= _value;
		uint48 _old = balances[_owner].balance;
		balances[_owner].balance -= _value;
		_modifyTotalSupply(_owner, _old);
		emit Transfer(_owner, 0x00, _value);
		emit TransferRange(_owner, 0x00, _start, _stop, _value);
		rangeMap[_start].owner = 0x00;
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
		returns (bool)
	{
		_checkBounds(_pointer);
		require(tokens[_pointer] == _pointer);
		Range storage r = rangeMap[_pointer];
		require(r.owner != 0x00);
		require(_time == 0 || _time > now);
		if (_compareRanges(tokens[_pointer-1], r.owner, _time, _tag)) {
			/* merge with previous range */
			uint48 _prev = tokens[_pointer-1];
			_setRangePointers(_prev, _pointer, 0);
			_setRangePointers(_pointer, r.stop, 0);
			_setRangePointers(_prev, r.stop, _prev);
			_replaceInBalanceRange(r.owner, _pointer, 0);
			rangeMap[_prev].stop = r.stop;
			delete rangeMap[_pointer];
			r = rangeMap[_prev];
			_pointer = _prev;
		}
		if (_compareRanges(r.stop, r.owner, _time, _tag)) {
			/* merge with next range */
			uint48 _next = rangeMap[r.stop].stop;
			_setRangePointers(r.stop, _next, 0);
			_setRangePointers(_pointer, r.stop, 0);
			_setRangePointers(_pointer, _next, _pointer);
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
		returns (bool)
	{
		_checkBounds(_start);
		_checkBounds(_stop-1);
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
				_setRangePointers(r.stop, _next, 0);
				_setRangePointers(_start, r.stop, 0);
				_setRangePointers(_start, _next, _start);
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
		_transfer(_id, _addr, _rating, _country, _range, uint48(_value));
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
		_transfer(_id, _addr, _rating, _country, _range, uint48(_value));
		return true;
	}

	/**
		@notice transfer tokens with a specific index range
		@param _to Receipient address
		@param _start Transfer start index
		@param _stop Transfer stop index
		@return bool success
	 */
	function transferRange(
		address _to,
		uint48 _start,
		uint48 _stop
	)
		public
		returns (bool)
	{
		_checkBounds(_start);
		_checkBounds(_stop-1);
		require(_start < _stop);
		uint48 _pointer = _getPointer(_stop-1);
		require(msg.sender == rangeMap[_pointer].owner);
		require(_pointer <= _start);
		require(_checkTime(_pointer));
		
		
		_transferRangeInternal([msg.sender, _to], _pointer, [_start, _stop]);
		return true;
	}

	/**
		@notice internal - transfer tokens with a specific index range
		@dev split from the previous function to avoid a stack depth error
		@param _addr Array of sender/reciever addresses
		@param _pointer Range pointer
		@param _range Transfer start and stop indexes
	 */
	function _transferRangeInternal(
		address[2] _addr,
		uint48 _pointer,
		uint48[2] _range
	)
		internal
	{
		uint48 _value = _range[1] - _range[0];
		(
			bytes32 _authID,
			bytes32[2] memory _id,
			uint8[2] memory _rating,
			uint16[2] memory _country
		) = issuer.checkTransfer(
			_addr[0],
			_addr[0],
			_addr[1],
			_value == balances[msg.sender].balance,
			_value
		);

		/* Issuer tokens are held at the IssuingEntity contract address */
		if (_id[0] == ownerID) {
			_addr[0] = address(issuer);
		}
		if (_id[1] == ownerID) {
			_addr[1] = address(issuer);
		}

		/* hook point for NFTModule.checkTransfer() */
		_callModules(
			0x70aaf928,
			0x00,
			abi.encode(_addr, _authID, _id, _rating, _country, _value)
		);

		/* hook point for NFTModule.checkTransferRange */
		require(_callModules(
				0x5a5a8ad8,
				rangeMap[_pointer].tag,
				abi.encode(_authID, _id, _addr, _rating, _country, _range)
			));
		
		uint48[] memory _newRange = new uint48[](1);
		_newRange[0] = _range[0];
		_transfer(_id, _addr, _rating, _country, _newRange, _value);
	}

	/**
		@notice Internal transfer function
		@dev common logic for transfer(), transferFrom() and transferRange()
		@param _id Array of sender/receiver IDs
		@param _addr Array of sender/receiver addresses
		@param _rating Array of sender/receiver ratings
		@param _country Array of sender/receiver countries
		@param _range Array of range pointers to transfer
		@param _value Amount to transfer
	 */
	function _transfer(
		bytes32[2] memory _id,
		address[2] memory _addr,
		uint8[2] memory _rating,
		uint16[2] memory _country,
		uint48[] memory _range,
		uint48 _value
	)
		internal
	{
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
			_transferSingleRange(_start, _addr[0], _addr[1], _start, _stop);
			/** hook point for NFToken.transferTokenRange() */
			_callModules(
				0x979c114f,
				rangeMap[_range[i]].tag,
				abi.encode(_id, _addr, _rating, _country, uint48[2]([_start, _stop]))
			);
			if (_value == 0) {
				emit Transfer(_addr[0], _addr[1], _value);
				return;
			}
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
	function _transferSingleRange(
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
				_setRangePointers(_pointer, _stop, 0);
				// join left
				if (!_right) {
					delete rangeMap[_pointer];
					rangeMap[_prev].stop = _stop;
					_setRangePointers(_prev, _stop, _prev);
					return;
				}
				// join right
				if (!_left) {
					_replaceInBalanceRange(_to, _stop, _start);
					rangeMap[_pointer] = Range(_to, rangeMap[_stop].stop, 0, _tag);
					_setRangePointers(_pointer, rangeMap[_stop].stop, _pointer);
				// join both
				} else {
					_replaceInBalanceRange(_to, _stop, 0);
					delete rangeMap[_pointer];
					rangeMap[_prev].stop = rangeMap[_stop].stop;
					_setRangePointers(_prev, _start, 0);
					_setRangePointers(_stop, rangeMap[_stop].stop, 0);
				}
				delete rangeMap[_stop];
				return;
			}

			// touches left
			delete rangeMap[_pointer];
			_setRangePointers(_start, _rangeStop, 0);
			_replaceInBalanceRange(_from, _start, _stop);
			
			// same owner left
			if (_compareRanges(_prev, _to, 0, _tag)) {
				_setRangePointers(_prev, _start, 0);
				_start = _prev;
			} else {
				_replaceInBalanceRange(_to, 0, _start);
			}
			rangeMap[_start] = Range(_to, _stop, 0, _tag);
			_setRangePointers(_start, _stop, _start);
			rangeMap[_stop] = Range(_from, _rangeStop, 0, _tag);
			_setRangePointers(_stop, _rangeStop, _stop);
			return;
		}

		// shared logic - touches right and touches nothing
		_setRangePointers(_pointer, _rangeStop, 0);
		rangeMap[_pointer].stop = _start;
		_setRangePointers(_pointer, _start, _pointer);

		// touches right
		if (_rangeStop == _stop) {
			// same owner right
			if (_compareRanges(_stop, _to, 0, _tag)) {
				_replaceInBalanceRange(_to, _stop, _start);
				_setRangePointers(_stop, rangeMap[_stop].stop, 0);
				uint48 _next = rangeMap[_stop].stop;
				delete rangeMap[_stop];
				_stop = _next;
			} else {
				_replaceInBalanceRange(_to, 0, _start);
			}
			rangeMap[_start] = Range(_to, _stop, 0, _tag);
			_setRangePointers(_start, _stop, _start);
			return;
		}

		//touches nothing
		_replaceInBalanceRange(_to, 0, _start);
		rangeMap[_start] = Range(_to, _stop, 0, _tag);
		_setRangePointers(_start, _stop, _start);
		
		_replaceInBalanceRange(_from, 0, _stop);
		rangeMap[_stop] = Range(_from, _rangeStop, 0, _tag);
		_setRangePointers(_stop, _rangeStop, _stop);
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
		_setRangePointers(_pointer, _stop, 0);
		_setRangePointers(_pointer, _split, _pointer);
		_setRangePointers(_split, _stop, _pointer);
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
		@notice Modify pointers in the token range
		@param _start Start index of range
		@param _stop Stop index of range
		@param _value Pointer value
	 */
	function _setRangePointers(uint48 _start, uint48 _stop, uint48 _value) internal {
		tokens[_start] = _value;
		_stop -= 1;
		if (_start == _stop) return;
		tokens[_stop] = _value;
		uint256 _interval = 16;
		while (true) {
			uint256 i = (_stop / _interval * _interval);
			if (i == 0) return;
			_interval *= 16;
			if (i % _interval == 0) continue;
			if (i > _start) tokens[i] = _value;
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

}