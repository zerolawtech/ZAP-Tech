pragma solidity >=0.4.24 <0.5.0;

import "../../open-zeppelin/SafeMath.sol";
import "./Module.sol";
import "../../bases/Token.sol";

/**
    @title Checkpoint Module Base Contract
    @dev Inherited contract for token modules requiring a balance checkpoint
*/
contract MultiCheckpointModuleBase is ModuleBase {

    using SafeMath for uint256;

    struct Checkpoint {

        uint128 previous;
        uint128 next;
        uint256 totalSupply;

        mapping (address => uint256) balances;
        mapping (address => bool) zeroBalances;
        mapping (address => mapping(address => uint256)) custBalances;
        mapping (address => mapping(address => bool)) custZeroBalances;

    }

    struct EpochPointers {
        uint128 previous;
        uint128 next;
    }

    mapping (address => EpochPointers) pointers;

    mapping (address => mapping(uint256 => Checkpoint)) checkpointData;



    /**
        @notice Base constructor
        @param _owner IssuingEntity contract address
     */
    constructor(address _owner) ModuleBase(_owner) public {
        return;
    }

    /**
        @notice supply permissions and hook points when attaching module
        @dev
            hooks: 0x35a341da - transferTokens
                   0x8b5f1240 - transferTokensCustodian
                   0x741b5078 - totalSupplyChanged
            hookBools - all true
     */
    function getPermissions()
        external
        pure
        returns
    (
        bytes4[] permissions,
        bytes4[] hooks,
        uint256 hookBools
    )
    {
        hooks = new bytes4[](3);
        hooks[0] = 0x35a341da;
        hooks[1] = 0x8b5f1240;
        hooks[2] = 0x741b5078;
        
        return (permissions, hooks, ~uint256(0));
    }

    /**
        @notice Internal getter for inherited contract to query checkpoint balance
        @dev Should only be called when now > time
        @param _owner Address of balance to query
        @return uint256 balance
     */
    function _getBalance(TokenBase _token, address _owner, uint256 _time) internal returns (uint256) {
        Checkpoint storage c = checkpointData[_token][_time];
        if (c.balances[_owner] > 0) return c.balances[_owner];
        if (c.zeroBalances[_owner]) return 0;
        uint256 _value = _token.balanceOf(_owner);
        _setBalance(c, _owner, _value);
        return _value;
    }

    /**
        @notice Getter, Inherited contract query custodied checkpoint balance
        @dev Should only be called when now > time
        @param _owner Address of balance to query
        @param _cust Custodian address
        @return uint256 balance
     */
    function _getCustodianBalance(
        TokenBase _token,
        address _owner,
        address _cust,
        uint256 _time
    )
        internal
        returns (uint256)
    {
        Checkpoint storage c = checkpointData[_token][_time];
        if (c.custBalances[_owner][_cust] > 0) return c.custBalances[_owner][_cust];
        if (c.custZeroBalances[_owner][_cust]) return 0;
        uint256 _value = _token.custodianBalanceOf(_owner, _cust);
        _setCustodianBalance(c, _owner, _cust, _value);
        return _value;
    }

    /**
        @notice Store a checkpoint balance
        @param _owner Address to set
        @param _value Balance at address
     */
    function _setBalance(Checkpoint storage c, address _owner, uint256 _value) private {
        while (true) {
            if (c.balances[_owner] > 0 || c.zeroBalances[_owner]) return;
            if (_value == 0) {
                c.zeroBalances[_owner] = true;
            } else {
                c.balances[_owner] = _value;
            }
            c = checkpointData[msg.sender][c.previous];
            if (c.previous == 0) return;
        }
    }

    /**
        @notice Store custodian checkpoint balance after tokens are received
        @param _owner Address of owner
        @param _cust Address of custodian
        @param _value Amount transferred
     */
    function _setCustodianBalance(
        Checkpoint storage c,
        address _owner,
        address _cust,
        uint256 _value
    )
        private
    {
        while (true) {
            if (c.custBalances[_owner][_cust] > 0 || c.custZeroBalances[_owner][_cust]) return;
            if (_value == 0) {
                c.custZeroBalances[_owner][_cust] == true;
            } else {
                c.custBalances[_owner][_cust] = _value;
            }
            c = checkpointData[msg.sender][c.previous];
            if (c.previous == 0) return;
        }
    }

    /**
        @notice Hook method, record checkpoint value after a transfer
        @param _addr Sender/receiver address
        @param _id Sender/receiver investor ID
        @param _rating Sender/receiver rating
        @param _value Amount transferred
        @return bool
     */
    function transferTokens(
        address[2] _addr,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2],
        uint256 _value
    )
        external
        returns (bool)
    {
        uint256 _previous = _getLastCheckpointTime();
        if (_previous == 0) return true;
        Checkpoint storage c = checkpointData[msg.sender][_previous];
        
        TokenBase _token = TokenBase(msg.sender);
        
        if (_rating[0] == 0 && _id[0] != ownerID) {
            uint256 _bal = _token.custodianBalanceOf(_addr[1], _addr[0]).add(_value);
            _setCustodianBalance(c, _addr[1], _addr[0], _bal);
        } else {
            _bal = _token.balanceOf(_addr[0]).add(_value);
            _setBalance(c, _addr[0], _bal);
        }
        if (_rating[1] == 0 && _id[1] != ownerID) {
            _bal = _token.custodianBalanceOf(_addr[0], _addr[1]).sub(_value);
            _setCustodianBalance(c, _addr[0], _addr[1], _bal);
        } else {
            _bal = _token.balanceOf(_addr[1]).sub(_value);
            _setBalance(c, _addr[1], _bal);
        }
        return true;
    }

    /**
        @notice Hook method, record checkpoint value after a custodial transfer
        @param _cust Custodian address
        @param _addr Sender/Receiver address
        @param _value Amount transferred
        @return bool
     */
    function transferTokensCustodian(
        address _cust,
        address[2] _addr,
        bytes32[2],
        uint8[2],
        uint16[2],
        uint256 _value
    )
        external
        returns (bool)
    {
        //require(msg.sender == address(token));
        uint256 _previous = _getLastCheckpointTime();
        if (_previous == 0) return true;
        Checkpoint storage c = checkpointData[msg.sender][_previous];
        
        uint256 _bal = TokenBase(msg.sender).custodianBalanceOf(_addr[0], _cust).add(_value);
        _setCustodianBalance(c, _addr[0], _cust, _bal);
        _bal = TokenBase(msg.sender).custodianBalanceOf(_addr[1], _cust).sub(_value);
        _setCustodianBalance(c, _addr[1], _cust, _bal);
    }

    /**
        @notice Hook method, record checkpoint value after mint/burn
        @param _addr Investor address
        @param _old Old balance
        @param _new New balance
        @return bool
     */
    function totalSupplyChanged(
        address _addr,
        bytes32,
        uint8,
        uint16,
        uint256 _old,
        uint256 _new
    )
        external
        returns (bool)
    {
        uint256 _previous = _getLastCheckpointTime();
        if (_previous == 0) return true;
        Checkpoint storage c = checkpointData[msg.sender][_previous];
        if (c.next != 0) {
            checkpointData[msg.sender][c.next].totalSupply = c.totalSupply.add(_new).sub(_old);
        }
        _setBalance(c, _addr, _old);
        return true;
    }

    function _getLastCheckpointTime() private returns (uint256) {
        EpochPointers storage p = pointers[msg.sender];
        if (p.next > now || p.next == 0) {
            return p.previous;
        }
        Checkpoint storage c = checkpointData[msg.sender][p.next];
        uint128 _prev = p.next;
        while (c.next != 0 && now > c.next) {
            checkpointData[msg.sender][c.next].totalSupply = c.totalSupply;
            _prev = c.next;
            c = checkpointData[msg.sender][c.next];
        }
        pointers[msg.sender] = EpochPointers(_prev, c.next);
        return _prev;
    }

    function newCheckpoint(address _token, uint128 _time) external returns (bool) {
        require(_time > now);
        require(checkpointData[_token][_time].totalSupply == 0);
        mapping(uint256 => Checkpoint) c = checkpointData[_token];
        if (pointers[_token].next == 0 || _time < pointers[_token].next) {
            EpochPointers memory p = pointers[_token];
            pointers[_token].next = _time;
        } else {
            uint128 _previous = pointers[_token].next;
            while (c[_previous].next != 0 && c[_previous].next < _time) {
                _previous = c[_previous].next;
            }
            p = EpochPointers(_previous, c[_previous].next);
        }
        c[p.previous].next = _time;
        if (p.next != 0) c[p.next].previous = _time;
        c[_time] = Checkpoint(p.previous, p.next, 0);
        return true;
    }

    function balanceOfAt(TokenBase _token, address _owner, uint128 _time) external view returns (uint256) {
        _getLastCheckpointTime();
        return _getBalance(_token, _owner, _time);
    }

}
