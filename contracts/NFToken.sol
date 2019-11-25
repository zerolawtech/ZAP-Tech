pragma solidity 0.4.25;

import "./bases/Token.sol";

/**
    @title Non-Fungible SecurityToken
    @dev
        Expands upon the ERC20 token standard
        https://theethereum.wiki/w/index.php/ERC20_Token_Standard
 */
contract NFToken is TokenBase  {

    uint256 constant SENDER = 0;
    uint256 constant RECEIVER = 1;

    /** depending on the intended totalSupply, you may wish to adjust this constant */
    uint256 constant SCOPING_MULTIPLIER = 16;

    uint48 upperBound;
    uint48[281474976710656] tokens;
    mapping (uint48 => Range) rangeMap;
    mapping (address => Balance) balances;

    struct Balance {
        uint48 balance;
        uint48 length;
        uint48[140737488355328] ranges;
    }

    struct Range {
        address owner;
        uint48 stop;
        uint32 time;
        bytes2 tag;
        address custodian;
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
        @dev Initially the total supply is credited to the org
        @param _org Address of the org's OrgCode contract
        @param _name Name of the token
        @param _symbol Unique ticker symbol
        @param _authorizedSupply Initial authorized token supply
     */
    constructor(
        OrgCode _org,
        string _name,
        string _symbol,
        uint256 _authorizedSupply
    )
        public
        TokenBase(
            _org,
            _name,
            _symbol,
            _authorizedSupply
        )
    {
        return;
    }

    /* modifier to ensure a range index is within bounds */
    function _checkBounds(uint256 _idx) internal view {
        if (_idx != 0 && _idx <= upperBound) return;
        revert("Invalid index");
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
            bytes2 _tag,
            address _custodian
        )
    {
        _checkBounds(_idx);
        _start = _getPointer(_idx);
        Range storage r = rangeMap[_start];
        return (r.owner, _start, r.stop, r.time, r.tag, r.custodian);
    }

    /**
        @notice Fetch the token ranges owned by an address
        @param _owner Address to query
        @return Array of [(start, stop),..]
     */
    function rangesOf(address _owner) external view returns (uint48[2][]) {
        return _rangesOf(_owner, 0x00);
    }

    /**
        @notice Fetch the token ranges owned by an address and held by a custodian
        @param _owner Address to query
        @param _custodian Address of custodian
        @return Array of [(start, stop),..]
     */
    function custodianRangesOf(
        address _owner,
        address _custodian
    )
        external
        view
        returns
        (uint48[2][])
    {
        return _rangesOf(_owner, _custodian);
    }

    /**
        @notice Internal - shared logic for rangesOf and custodianRangesOf
        @param _owner Address to query
        @param _custodian Address of custodian
        @return Array of [(start, stop),..]
     */
    function _rangesOf(
        address _owner,
        address _custodian
    )
        internal
        view
        returns (uint48[2][])
    {
        Balance storage b = balances[_owner];
        uint256 _count;
        for (uint256 i; i < b.length; i++) {
            if (rangeMap[b.ranges[i]].custodian != _custodian) continue;
            _count++;
        }
        uint48[2][] memory _ranges = new uint48[2][](_count);
        _count = 0;
        for (i = 0; i < b.length; i++) {
            if (rangeMap[b.ranges[i]].custodian != _custodian) continue;
            _ranges[_count] = [b.ranges[i], rangeMap[b.ranges[i]].stop];
            _count++;
        }
        return _ranges;
    }

    /**
        @notice shared logic for checkTransfer and checkTransferCustodian
        @dev If a transfer is not allowed, the function will throw
        @param _cust Address of custodian contract
        @param _from Address of sender
        @param _to Address of recipient
        @param _value Amount being transferred,
        @param _zero After transfer, does the sender have a 0 balance?
     */
    function _checkTransferView(
        address _cust,
        address _from,
        address _to,
        uint256 _value,
        bool _zero
    )
        internal
    {
        (
            bytes32 _authID,
            bytes32[2] memory _id,
            uint8[2] memory _rating,
            uint16[2] memory _country
        ) = org.checkTransfer(_from, _from, _to, _zero);
        _checkTransfer(
            _authID,
            _id,
            _cust,
            [_from, _to],
            _rating,
            _country,
            _value
        );
    }

    /**
        @notice internal check of transfer permission before performing it
        @param _authID ID of calling authority
        @param _id Array of investor IDs
        @param _cust Custodian address
        @param _addr Investor address array
        @param _rating Investor rating array
        @param _country Investor country array
        @param _value Value of transfer
        @return address array of investors
        @return dynamic array of range pointers that to transfer
     */
    function _checkTransfer(
        bytes32 _authID,
        bytes32[2] _id,
        address _cust,
        address[2] _addr,
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
        /* Sending 0 balance is blocked to reduce logic around investor limits */
        require(_value > 0, "Cannot send 0 tokens");
        require(uint48(_value) == _value, "Value too large");

        /* Issuer tokens are held at the OrgCode contract address */
        if (_id[SENDER] == ownerID) {
            _addr[SENDER] = address(org);
        }
        if (_id[RECEIVER] == ownerID) {
            _addr[RECEIVER] = address(org);
        }
        require(_addr[SENDER] != _addr[RECEIVER], "Cannot send to self");

        if (_rating[SENDER] == 0 && _id[SENDER] != ownerID) {
            /* if sender is custodian, look at custodied ranges */
            _cust = _addr[SENDER];
            Balance storage b = balances[_addr[RECEIVER]];
        } else {
            b = balances[_addr[SENDER]];
        }
        if (_cust == 0x00 || (_rating[SENDER] == 0 && _id[SENDER] != ownerID)) {
            require(balances[_addr[SENDER]].balance >= _value, "Insufficient Balance");
        } else {
            require(
                custBalances[_addr[SENDER]][_cust] >= _value,
                "Insufficient Custodial Balance"
            );
        }
        _range = new uint48[](b.length);
        for (uint256 i; i < _range.length; i++) {
            _range[i] = b.ranges[i];
        }
        /* bytes4 signature for token module checkTransfer() */
        require(_callModules(
            0x70aaf928,
            0x00,
            abi.encode(_addr, _authID, _id, _rating, _country, _value)
        ));
        _range = _findTransferrableRanges(
            _authID,
            _id,
            _cust,
            _addr,
            _rating,
            _country,
            _value,
            _range
        );
        return (_addr, _range);
    }

    /**
        @notice Find ranges that are permitted to transfer
        @param _authID ID of calling authority
        @param _id Array of investor IDs
        @param _cust Custodian address
        @param _addr Investor address array
        @param _rating Investor rating array
        @param _country Investor country array
        @param _value Value of transfer
        @param _startRange Initial range to search
        @return dynamic array of range pointers that to transfer
     */
    function _findTransferrableRanges(
        bytes32 _authID,
        bytes32[2] _id,
        address _cust,
        address[2] _addr,
        uint8[2] _rating,
        uint16[2] _country,
        uint256 _value,
        uint48[] _startRange
    )
        internal
        returns (uint48[] _range)
    {
        uint256 _count;
        _range = new uint48[](_startRange.length);
        for (uint256 i; i < _startRange.length; i++) {
            if(!_checkTime(_startRange[i])) continue;
            Range storage r = rangeMap[_startRange[i]];
            if (r.custodian !=_cust) continue;
            /** hook point for NFToken.checkTransferRange() */
            if (_callModules(0x2d79c6d7, r.tag, abi.encode(
                _authID,
                _id,
                _addr,
                _rating,
                _country,
                uint48[2]([_startRange[i],r.stop])
            ))) {
                _range[_count] = _startRange[i];
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
        require(_value > 0); // dev: mint 0
        require(upperBound + _value > upperBound); // dev: overflow
        require(upperBound + _value <= 2**48 - 2); // dev: upper bound
        require(_time == 0 || _time > now); // dev: time
        org.checkTransfer(address(org), address(org), _owner, false);
        uint48 _start = uint48(upperBound + 1);
        uint48 _stop = _start + _value;
        if (_compareRanges(tokens[upperBound], _owner, _time, _tag, 0x00)) {
            /* merge with previous range */
            uint48 _pointer = tokens[upperBound];
            rangeMap[_pointer].stop = _stop;
        } else {
            /* create new range */
            _setRange(_start, _owner, _stop, _time, _tag, 0x00);
            balances[_owner].ranges[balances[_owner].length] = _start;
            balances[_owner].length += 1;
        }
        uint48 _old = balances[_owner].balance;
        balances[_owner].balance += _value;
        totalSupply += _value;
        upperBound += _value;
        require(totalSupply <= authorizedSupply); // dev: exceed auth
        emit RangeSet(_tag, _start, _stop, _time);
        emit Transfer(0x00, _owner, _value);
        emit TransferRange(0x00, _owner, _start, _stop, _value);
        _modifyTotalSupply(_owner, _old);
        return true;
    }

    /**
        @notice Burns tokens
        @dev Cannot burn multiple ranges in a single call
        @param _start Start index of range to burn
        @param _stop Stop index of range to burn
        @return Bool success
     */
    function burn(uint48 _start, uint48 _stop) external returns (bool) {
        /* msg.sig = 0x9a0d378b */
        if (!_checkPermitted()) return false;
        require(_stop > _start); // dev: burn 0
        uint48 _pointer = _getPointer(_stop-1);
        require(_pointer <= _start); // dev: multiple ranges
        require(rangeMap[_pointer].custodian == 0); // dev: custodian
        address _owner = rangeMap[_pointer].owner;
        require(_owner != 0x00); // dev: already burnt
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
        emit Transfer(_owner, 0x00, _value);
        emit TransferRange(_owner, 0x00, _start, _stop, _value);
        _modifyTotalSupply(_owner, _old);
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
        /* msg.sig = 0x712a516a */
        if (!_checkPermitted()) return false;
        _checkBounds(_pointer);
        require(tokens[_pointer] == _pointer);
        Range storage r = rangeMap[_pointer];
        require(r.owner != 0x00);
        require(_time == 0 || _time > now);
        if (_compareRanges(tokens[_pointer-1], r.owner, _time, _tag, r.custodian)) {
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
        if (_compareRanges(r.stop, r.owner, _time, _tag, r.custodian)) {
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
        @notice Modifies one or more ranges
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
        /* msg.sig = 0x786500aa */
        if (!_checkPermitted()) return false;
        _checkBounds(_start);
        _checkBounds(_stop-1);
        require(_start < _stop);
        require(_time == 0 || _time > now);
        if (_stop < upperBound + 1) {
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
            if (
                r.stop < _stop &&
                rangeMap[r.stop].owner == r.owner &&
                rangeMap[r.stop].custodian == r.custodian
            ) {
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
        @dev calls to _checkTransfer() to verify permission before transferring
        @param _to Recipient
        @param _value Amount being transferred
        @return bool success
     */
    function transfer(address _to, uint256 _value) external returns (bool) {
        _transfer(msg.sender, [msg.sender, _to], _value);
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
            address _auth = address(org);
        } else {
            _auth = msg.sender;
        }
        _transfer(_auth, [_from, _to], _value);
        return true;
    }

    /**
        @notice Internal transfer function
        @dev common logic for transfer() and transferFrom()
        @param _auth Address that called the method
        @param _addr Array of receiver/sender address
        @param _value Amount to transfer
     */
    function _transfer(
        address _auth,
        address[2] _addr,
        uint256 _value
    )
        internal
    {
        bool[4] memory _zero = [
             balances[_addr[SENDER]].balance == _value,
             balances[_addr[RECEIVER]].balance == 0,
            custBalances[_addr[RECEIVER]][_addr[SENDER]] == _value,
            custBalances[_addr[SENDER]][_addr[RECEIVER]] == 0
        ];
        (
            bytes32 _authID,
            bytes32[2] memory _id,
            uint8[2] memory _rating,
            uint16[2] memory _country
        ) = org.transferTokens(
            _auth,
            _addr[SENDER],
            _addr[RECEIVER],
            _zero
        );

        uint48 _smallVal = uint48(_value);
        uint48[] memory _range;
        (_addr, _range) = _checkTransfer(
            _authID,
            _id,
            0x00,
            _addr,
            _rating,
            _country,
            _value
        );

        if (
            _authID != _id[SENDER] &&
            _id[SENDER] != _id[RECEIVER] &&
            _authID != ownerID
        ) {
            /**
                If the call was not made by the org or the sender and involves
                a change in ownership, subtract from the allowed mapping.
            */
            require(
                allowed[_addr[SENDER]][_auth] >= _value,
                "Insufficient allowance"
            );
            allowed[_addr[SENDER]][_auth] -= _value;
        }

        address _cust;
        (_cust, _addr) = _adjustBalances(_id, _addr, _rating, _country, _smallVal);
        _transferMultipleRanges(_id, _addr, _cust, _rating, _country, _smallVal, _range);
    }

    /**
        @notice Internal function to modify balance mappings
        @dev common logic for transfer(), transferFrom() and transferRange()
        @param _id Array of sender/receiver ID
        @param _addr Array of sender/receiver addresses
        @param _rating Array of sender/receiver investor rating
        @param _country Array of sender/receiver countries
        @param _value Amount to transfer
        @return Custodian address, sender/receiver addresses
     */
    function _adjustBalances(
        bytes32[2] _id,
        address[2] _addr,
        uint8[2] _rating,
        uint16[2] _country,
        uint48 _value
    )
        internal
        returns (
            address _cust,
            address[2]
        )
    {
        require(_value <= balances[_addr[SENDER]].balance);
        balances[_addr[SENDER]].balance -= _value;
        balances[_addr[RECEIVER]].balance += _value;

        if (_rating[SENDER] == 0 && _id[SENDER] != ownerID) {
            /* sender is custodian, reduce custodian balance */
            custBalances[_addr[RECEIVER]][_addr[SENDER]] -= _value;
            _addr[SENDER] = _addr[RECEIVER];
        } else if (_rating[RECEIVER] == 0 && _id[RECEIVER] != ownerID) {
            /* receiver is custodian, increase and notify */
            _cust = _addr[RECEIVER];
            _addr[RECEIVER] = _addr[SENDER];
            custBalances[_addr[SENDER]][_cust] += _value;
            require(IBaseCustodian(_cust).receiveTransfer(_addr[SENDER], _value));
        }
        /* bytes4 signature for token module transferTokens() */
        require(_callModules(
            0x35a341da,
            0x00,
            abi.encode(_addr, _id, _rating, _country, _value)
        ));
        return (_cust, _addr);
    }

    /**
        @notice Custodian transfer function
        @dev
            called by Custodian.transferInternal to change ownership within
            the custodian contract without moving any tokens
        @param _addr Sender/Receiver addresses
        @param _value Amount to transfer
        @return bool
     */
    function transferCustodian(
        address[2] _addr,
        uint256 _value
    )
        public
        returns (bool)
    {
        bool[4] memory _zero = [
            custBalances[_addr[SENDER]][msg.sender] == _value,
            custBalances[_addr[RECEIVER]][msg.sender] == 0,
            false,
            false
        ];
        (
            bytes32 _authID,
            bytes32[2] memory _id,
            uint8[2] memory _rating,
            uint16[2] memory _country
        ) = org.transferTokens(msg.sender, _addr[SENDER], _addr[RECEIVER], _zero);

        uint48[] memory _range;
        (_addr, _range) = _checkTransfer(
            _authID,
            _id,
            msg.sender,
            _addr,
            _rating,
            _country,
            _value
        );

        custBalances[_addr[SENDER]][msg.sender] -= _value;
        custBalances[_addr[RECEIVER]][msg.sender] += _value;
        /* bytes4 signature for token module transferTokensCustodian() */
        require(_callModules(
            0x8b5f1240,
            0x00,
            abi.encode(msg.sender, _addr, _id, _rating, _country, _value)
        ));
        _transferMultipleRanges(
            _id,
            _addr,
            msg.sender,
            _rating,
            _country,
            uint48(_value),
            _range
        );
        return true;
    }

    /**
        @notice Internal transfer function
        @dev common logic for transfer(), transferFrom() and transferCustodian()
        @param _id Array of sender/receiver ID
        @param _addr Array of sender/receiver addresses
        @param _custodian Custodian of new ranges
        @param _rating Array of sender/receiver investor rating
        @param _country Array of sender/receiver countries
        @param _value Amount to transfer
        @param _range Array of range pointers to transfer
     */
    function _transferMultipleRanges(
        bytes32[2] _id,
        address[2] _addr,
        address _custodian,
        uint8[2] _rating,
        uint16[2] _country,
        uint48 _value,
        uint48[] _range
    )
        internal
    {
        emit Transfer(_addr[SENDER], _addr[RECEIVER], _value);
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
            _transferSingleRange(
                _start,
                _addr[SENDER],
                _addr[RECEIVER],
                _start,
                _stop,
                _custodian
            );
            /** hook point for NFToken.transferTokenRange() */
            require(_callModules(
                0xead529f5,
                rangeMap[_range[i]].tag,
                abi.encode(_addr, _id, _rating, _country, uint48[2]([_start, _stop]))
            ));
            if (_value == 0) {
                return;
            }
        }
        revert();
    }

    /**
        @notice transfer tokens with a specific index range
        @dev Can send tokens into a custodian, but not out of one
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
        external
        returns (bool)
    {
        _checkBounds(_start);
        _checkBounds(_stop-1);
        require(_start < _stop); // dev: stop < start
        uint48 _pointer = _getPointer(_stop-1);
        require(rangeMap[_pointer].custodian == 0x00); // dev: custodian
        require(_pointer <= _start); // dev: multiple ranges
        require(_checkTime(_pointer)); // dev: time

        address[2] memory _addr = [msg.sender, _to];
        uint48[2] memory _range = [_start, _stop];

        uint48 _value = _stop - _start;
        bool[4] memory _zero = [
            balances[msg.sender].balance == _value,
            balances[_addr[RECEIVER]].balance == 0,
            custBalances[_addr[RECEIVER]][_addr[SENDER]] == _value,
            custBalances[_addr[SENDER]][_addr[RECEIVER]] == 0
        ];
        (
            bytes32 _authID,
            bytes32[2] memory _id,
            uint8[2] memory _rating,
            uint16[2] memory _country
        ) = org.transferTokens(_addr[SENDER], _addr[SENDER], _addr[RECEIVER], _zero);

        /* Issuer tokens are held at the OrgCode contract address */
        if (_id[SENDER] == ownerID) {
            _addr[SENDER] = address(org);
        } else {
            /* prevent send from custodian */
            require(_rating[SENDER] > 0);
        }
        if (_id[RECEIVER] == ownerID) {
            _addr[RECEIVER] = address(org);
        }

        require(
            _addr[SENDER] == rangeMap[_pointer].owner,
            "Sender does not own range"
        );
        require(_addr[SENDER] != _addr[RECEIVER], "Cannot send to self");

        /* hook point for NFTModule.checkTransfer() */
        require(_callModules(
            0x70aaf928,
            0x00,
            abi.encode(_addr, _authID, _id, _rating, _country, _value)
        ));

        /* hook point for NFTModule.checkTransferRange */
        require(_callModules(
            0x2d79c6d7,
            rangeMap[_pointer].tag,
            abi.encode(_addr, _authID, _id, _rating, _country, _range)
        ));

        address _cust;
        (_cust, _addr) = _adjustBalances(_id, _addr, _rating, _country, _value);

        _transferSingleRange(
            _pointer,
            _addr[SENDER],
            _addr[RECEIVER],
            _range[0],
            _range[1],
            _cust
        );
        /* hook point for NFToken.transferTokenRange() */
        require(_callModules(
            0xead529f5,
            rangeMap[_pointer].tag,
            abi.encode(_addr, _id,  _rating, _country, _range)
        ));
    }

    /**
        @notice internal - transfer ownership of a single range of tokens
        @param _pointer Range array pointer
        @param _from Sender address
        @param _to Recipient address
        @param _start Start index of range
        @param _stop Stop index of range
        @param _custodian Custodian of range
     */
    function _transferSingleRange(
        uint48 _pointer,
        address _from,
        address _to,
        uint48 _start,
        uint48 _stop,
        address _custodian
    )
        internal
    {
        Range storage r = rangeMap[_pointer];
        uint48 _rangeStop = r.stop;
        uint48 _prev = tokens[_start-1];
        bytes2 _tag = r.tag;
        emit TransferRange(_from, _to, _start, _stop, _stop-_start);

        if (_pointer == _start) {
            /* touches both */
            if (_rangeStop == _stop) {
                _replaceInBalanceRange(_from, _start, 0);
                bool _left = _compareRanges(_prev, _to, 0, _tag, _custodian);
                bool _right = _compareRanges(_stop, _to, 0, _tag, _custodian);
                /* no join */
                if (!_left && !_right) {
                    _replaceInBalanceRange(_to, 0, _start);
                    if (_from != _to) {
                        r.owner = _to;
                    }
                    if (r.custodian != _custodian) {
                        r.custodian = _custodian;
                    }
                    return;
                }
                _setRangePointers(_pointer, _stop, 0);
                /* join left */
                if (!_right) {
                    delete rangeMap[_pointer];
                    rangeMap[_prev].stop = _stop;
                    _setRangePointers(_prev, _stop, _prev);
                    return;
                }
                /* join right */
                if (!_left) {
                    _replaceInBalanceRange(_to, _stop, _start);
                    _setRange(_pointer, _to, rangeMap[_stop].stop, 0, _tag, _custodian);
                /* join both */
                } else {
                    _replaceInBalanceRange(_to, _stop, 0);
                    delete rangeMap[_pointer];
                    rangeMap[_prev].stop = rangeMap[_stop].stop;
                    _setRangePointers(_prev, _start, 0);
                    _setRangePointers(_stop, rangeMap[_stop].stop, 0);
                    _setRangePointers(_prev, rangeMap[_prev].stop, _prev);
                }
                delete rangeMap[_stop];
                return;
            }

            /* touches left */
            _setRangePointers(_start, _rangeStop, 0);
            _setRange(_stop, _from, _rangeStop, 0, _tag, r.custodian);
            _replaceInBalanceRange(_from, _start, _stop);
            delete rangeMap[_pointer];

            /* same owner left */
            if (_compareRanges(_prev, _to, 0, _tag, _custodian)) {
                _setRangePointers(_prev, _start, 0);
                _start = _prev;
            } else {
                _replaceInBalanceRange(_to, 0, _start);
            }
            _setRange(_start, _to, _stop, 0, _tag, _custodian);
            return;
        }

        /* shared logic - touches right and touches nothing */
        _setRangePointers(_pointer, _rangeStop, 0);
        r.stop = _start;
        _setRangePointers(_pointer, _start, _pointer);

        /* touches right */
        if (_rangeStop == _stop) {
            /* same owner right */
            if (_compareRanges(_stop, _to, 0, _tag, _custodian)) {
                _replaceInBalanceRange(_to, _stop, _start);
                _setRangePointers(_stop, rangeMap[_stop].stop, 0);
                uint48 _next = rangeMap[_stop].stop;
                delete rangeMap[_stop];
                _stop = _next;
            } else {
                _replaceInBalanceRange(_to, 0, _start);
            }
            _setRange(_start, _to, _stop, 0, _tag, _custodian);
            return;
        }

        /* touches nothing */
        _replaceInBalanceRange(_to, 0, _start);
        _setRange(_start, _to, _stop, 0, _tag, _custodian);
        _replaceInBalanceRange(_from, 0, _stop);
        _setRange(_stop, _from, _rangeStop, 0, _tag, r.custodian);
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
        @param _custodian New range custodian
        @return equality boolean
     */
    function _compareRanges(
        uint48 _pointer,
        address _owner,
        uint32 _time,
        bytes2 _tag,
        address _custodian
    )
        internal
        returns (bool)
    {
        Range storage r = rangeMap[_pointer];
        if (r.time > 0 && r.time < now) {
            r.time = 0;
        }
        return (
            r.owner == _owner &&
            r.time == _time &&
            r.tag == _tag &&
            r.custodian == _custodian
        );
    }

    /**
        @notice Splits a range
        @dev
            Called when a new tag is added, to prevent a balance range
            where some tokens are tagged differently from others
        @param _split Index to split the range at
     */
    function _splitRange(uint48 _split) internal {
        if (tokens[_split-1] != 0 && tokens[_split] > tokens[_split-1]) return;
        uint48 _pointer = _getPointer(_split);
        Range storage r = rangeMap[_pointer];
        uint48 _stop = r.stop;
        r.stop = _split;
        _replaceInBalanceRange(r.owner, 0, _split);
        _setRangePointers(_pointer, _stop, 0);
        _setRangePointers(_pointer, _split, _pointer);
        _setRange(_split, r.owner, _stop, r.time, r.tag, r.custodian);
    }

    /**
        @notice sets a Range struct and associated pointers
        @dev keeping this as a seperate method reduces gas costs from SSTORE
        @param _pointer Range pointer to set
        @param _owner Address of range owner
        @param _stop Range stop index
        @param _time Range time value
        @param _tag Range tag value
        @param _custodian Range custodian value
     */
    function _setRange(
        uint48 _pointer,
        address _owner,
        uint48 _stop,
        uint32 _time,
        bytes2 _tag,
        address _custodian
    )
        internal
    {
        Range storage r = rangeMap[_pointer];
        if (r.owner != _owner) r.owner = _owner;
        if (r.stop != _stop) r.stop = _stop;
        if (r.time != _time) r.time = _time;
        if (r.tag != _tag) r.tag = _tag;
        if (r.custodian != _custodian) r.custodian = _custodian;
        _setRangePointers(_pointer, _stop, _pointer);
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
        uint48[140737488355328] storage r = balances[_addr].ranges;
        if (_old == 0) {
            // add a new range to the array
            r[balances[_addr].length] = _new;
            balances[_addr].length += 1;
            return;
        }
        for (uint256 i; i <= balances[_addr].length; i++) {
            if (r[i] == _old) {
                if (_new > 0) {
                    // replace an existing range
                    r[i] = _new;
                } else {
                    // delete an existing range
                    balances[_addr].length -= 1;
                    r[i] = r[balances[_addr].length];
                }
                return;
            }
        }
        revert();
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
        uint256 _interval = SCOPING_MULTIPLIER;
        while (true) {
            uint256 i = (_stop / _interval * _interval);
            if (i == 0) return;
            _interval *= SCOPING_MULTIPLIER;
            if (i % _interval == 0) continue;
            if (i > _start) tokens[i] = _value;
        }
    }

    /**
        @notice Find an array range pointer
        @dev
            Given a token index, this will iterate through the range
            and return the mapping pointer that the index is present within.
        @param i Token index
     */
    function _getPointer(uint256 i) internal view returns (uint48) {
        uint256 _increment = 1;
        while (true) {
            if (tokens[i] != 0x00) return tokens[i];
            if (i % (_increment * SCOPING_MULTIPLIER) == 0) {
                _increment *= SCOPING_MULTIPLIER;
                require(i <= upperBound); // dev: exceeds upper bound
            }
            i += _increment;
        }
    }
}
