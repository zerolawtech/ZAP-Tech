pragma solidity 0.4.25;

import "./open-zeppelin/SafeMath.sol";
import "./bases/OrgShare.sol";

import "./interfaces/ICustodian.sol";
import "./interfaces/IOrgCode.sol";

/**
    @title Fungible "Book Entry" OrgShare Contract
    @dev
        Expands upon the ERC20 token standard
        https://theethereum.wiki/w/index.php/ERC20_Token_Standard
 */
contract BookShare is OrgShareBase {

    using SafeMath for uint256;

    uint256 constant SENDER = 0;
    uint256 constant RECEIVER = 1;

    mapping (address => uint256) balances;

    /**
        @notice BookShare constructor
        @param _org Address of the org's OrgCode contract
        @param _name Name of the OrgShare class
        @param _symbol Unique ticker symbol
        @param _authorizedSupply Initial authorized total supply
     */
    constructor(
        IOrgCode _org,
        string _name,
        string _symbol,
        uint256 _authorizedSupply
    )
        public
        OrgShareBase(
            _org,
            _name,
            _symbol,
            _authorizedSupply
        )
    {
        return;
    }

    /**
        @notice Fetch the current balance at an address
        @param _owner Address of balance to query
        @return integer
     */
    function balanceOf(address _owner) public view returns (uint256) {
        return balances[_owner];
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
        ) = orgCode.checkTransfer(_from, _from, _to, _zero);
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
        @notice internal check of transfer permission
        @dev
            seperate from _checkTransferView so it can be called by transfer
            related functions without the call to orgCode.checkTransfer
        @param _authID ID of caller
        @param _id ID array of member IDs
        @param _cust Custodian address (0x00 if none)
        @param _addr address array of members
        @param _rating array of member ratings
        @param _country array of member countries
        @param _value Amount being transferred
        @return array of member addresses
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
        view
        returns (address[2])
    {
        require(_value > 0, "Cannot send 0 shares");
        /* Org shares are held at the OrgCode contract address */
        if (_id[SENDER] == ownerID) {
            _addr[SENDER] = address(orgCode);
        }
        if (_id[RECEIVER] == ownerID) {
            _addr[RECEIVER] = address(orgCode);
        }
        if (_cust != 0x00) {
            /**
                if transfer originates from custodian, check custodial balance
                of receiver. Otherwise check custodial balance of sender
            */
            address _owner = (_addr[SENDER] == _cust ? _addr[RECEIVER] : _addr[SENDER]);
            require(
                custBalances[_owner][_cust] >= _value,
                "Insufficient Custodial Balance"
            );
        } else {
            require(balances[_addr[SENDER]] >= _value, "Insufficient Balance");
        }

        /* bytes4 signature for share module checkTransfer() */
        require(_callModules(
            0x70aaf928,
            0x00,
            abi.encode(_addr, _authID, _id, _rating, _country, _value)
        ));
        return _addr;
    }

    /**
        @notice ERC-20 transfer standard
        @dev calls to _checkToSend() to verify permission before transferring
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
        @dev
            * The orgCode may use this function to transfer shares belonging to
              any address.
            * Modules may call this function to transfer shares with the same
              level of authority as orgCode.
            * An member with multiple addresses may use this to transfer shares
              from any address he controls, without giving prior approval to that
              address.
            * An unregistered address cannot initiate a transfer, even if it was
              given approval.
        @param _from Sender
        @param _to Recipient
        @param _value Amount being transferred
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
            address _auth = address(orgCode);
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
        (
            bytes32 _authID,
            bytes32[2] memory _id,
            uint8[2] memory _rating,
            uint16[2] memory _country
        ) = orgCode.transferShares(
            _auth,
            _addr[SENDER],
            _addr[RECEIVER],
            /*
                Must send regular and custodial zero balances, as we do not
                yet know which type of transfer this.
            */
            [
                balances[_addr[SENDER]] == _value,
                balances[_addr[RECEIVER]] == 0,
                custBalances[_addr[RECEIVER]][_addr[SENDER]] == _value,
                custBalances[_addr[SENDER]][_addr[RECEIVER]] == 0
            ]
        );
        _addr = _checkTransfer(
            _authID,
            _id,
            /** is sender a custodian? */
            (_rating[SENDER] == 0 && _id[SENDER] != ownerID) ? _addr[SENDER] : 0x00,
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
            /*
                If the call was not made by orgCode or the sender and involves
                a change in ownership, subtract from the allowed mapping.
            */
            require(allowed[_addr[SENDER]][_auth] >= _value, "Insufficient allowance");
            allowed[_addr[SENDER]][_auth] = allowed[_addr[SENDER]][_auth].sub(_value);
        }

        /*
            balances are modified regardless of if the transfer involves a
            custodian, to keep sum of balance mapping == totalSupply
         */
        balances[_addr[SENDER]] = balances[_addr[SENDER]].sub(_value);
        balances[_addr[RECEIVER]] = balances[_addr[RECEIVER]].add(_value);

        if (_rating[SENDER] == 0 && _id[SENDER] != ownerID) {
            /* sender is custodian, reduce custodian balance */
            custBalances[_addr[RECEIVER]][_addr[SENDER]] = (
                custBalances[_addr[RECEIVER]][_addr[SENDER]].sub(_value)
            );
        }

        if (_rating[RECEIVER] == 0 && _id[RECEIVER] != ownerID) {
            /* receiver is custodian, increase custodian balance and notify */
            custBalances[_addr[SENDER]][_addr[RECEIVER]] = (
                custBalances[_addr[SENDER]][_addr[RECEIVER]].add(_value)
            );
            require(ICustodian(_addr[RECEIVER]).receiveTransfer(_addr[SENDER], _value));
        }

        /* bytes4 signature for share module transferShares() */
        require(_callModules(
            0x0675a5e0,
            0x00,
            abi.encode(_addr, _id, _rating, _country, _value)
        ));
        emit Transfer(_addr[SENDER], _addr[RECEIVER], _value);
    }

    /**
        @notice Custodian transfer function
        @dev
            called by Custodian.transferInternal to change ownership within
            the custodian contract without moving any shares
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
        /*
            transfer is presented to orgCode.transferShares as a normal one so
            zero[2:] can be set to false. set here to prevent stack depth error.
        */
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
        ) = orgCode.transferShares(msg.sender, _addr[SENDER], _addr[RECEIVER], _zero);

        _addr = _checkTransfer(
            _authID,
            _id,
            msg.sender,
            _addr,
            _rating,
            _country,
            _value
        );
        custBalances[_addr[SENDER]][msg.sender] = (
            custBalances[_addr[SENDER]][msg.sender].sub(_value)
        );
        custBalances[_addr[RECEIVER]][msg.sender] = (
            custBalances[_addr[RECEIVER]][msg.sender].add(_value)
        );
        /* bytes4 signature for share module transferSharesCustodian() */
        require(_callModules(
            0xdc9d1da1,
            0x00,
            abi.encode(msg.sender, _addr, _id, _rating, _country, _value)
        ));
        return true;
    }

    /**
        @notice Mint new shares and increase total supply
        @dev Callable by orgCode or via module
        @param _owner Owner of the shares
        @param _value Number of shares to mint
        @return bool
     */
    function mint(address _owner, uint256 _value) external returns (bool) {
        /* msg.sig = 0x40c10f19 */
        if (!_checkPermitted()) return false;
        require(_value > 0); // dev: mint 0
        orgCode.checkTransfer(address(orgCode), address(orgCode), _owner, false);
        uint256 _old = balances[_owner];
        balances[_owner] = _old.add(_value);
        totalSupply = totalSupply.add(_value);
        require(totalSupply <= authorizedSupply); // dev: exceed auth
        emit Transfer(0x00, _owner, _value);
        return _modifyTotalSupply(_owner, _old);
    }

    /**
        @notice Burn shares and decrease total supply
        @dev Callable by the orgCode or via module
        @param _owner Owner of the shares
        @param _value Number of shares to burn
        @return bool
     */
    function burn(address _owner, uint256 _value) external returns (bool) {
        /* msg.sig = 0x9dc29fac */
        if (!_checkPermitted()) return false;
        require(_value > 0); // dev: burn 0
        uint256 _old = balances[_owner];
        balances[_owner] = _old.sub(_value);
        totalSupply = totalSupply.sub(_value);
        emit Transfer(_owner, 0x00, _value);
        return _modifyTotalSupply(_owner, _old);
    }

}
