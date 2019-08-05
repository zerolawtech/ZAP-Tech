pragma solidity >=0.4.24 <0.5.0;

import "../open-zeppelin/SafeMath.sol";
import "../bases/Token.sol";
import "./bases/Module.sol";


/**
    @title MiniMeCheckpoint Module
    @dev
        Token level module used to record and access checkpoints with a similar
        interface to the popular MiniMe token standard
        https://github.com/Giveth/minime/blob/master/contracts/MiniMeToken.sol
*/
contract MiniMeCheckpointModule is STModuleBase {

    using SafeMath for uint256;

    struct Checkpoint {
        uint256 totalSupply;
        uint64 previous;
        uint64 next;
        bool set;
        mapping (address => uint256) balances;
        mapping (address => bool) zeroBalances;
        mapping (address => mapping(address => uint256)) custBalances;
        mapping (address => mapping(address => bool)) custZeroBalances;
    }

    uint64 previousPointer;
    uint64 nextPointer;

    mapping(uint256 => Checkpoint) checkpointData;

    event CheckpointSet(uint64 blockNumber);

    /**
        @notice Base constructor
        @param _token SecurityToken contract address
        @param _issuer IssuingEntity contract address
     */
    constructor(
        SecurityToken _token,
        address _issuer
    )
        public
        STModuleBase(_token, _issuer)
    {
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
        @notice Check if a checkpoint exists for a given token and blockNumber
        @param _blockNumber block number of checkpoint
        @return boolean
     */
    function checkpointExists(uint256 _blockNumber) external view returns (bool) {
        return checkpointData[_blockNumber].set;
    }

    /**
        @notice Query token checkpoint totalSupply
        @param _blockNumber Checkpoint block number
        @return uint256 totalSupply at checkpoint
     */
    function totalSupplyAt(uint256 _blockNumber) external view returns (uint256) {
        _advanceCheckpoints();
        require(checkpointData[_blockNumber].set);
        return checkpointData[_blockNumber].totalSupply;
    }

    /**
        @notice Query token checkpoint balance
        @param _owner Address of balance to query
        @param _blockNumber Checkpoint block number
        @return uint256 balance at checkpoint
     */
    function balanceOfAt(
        address _owner,
        uint256 _blockNumber
    )
        external
        view
        returns (uint256)
    {
        _advanceCheckpoints();
        Checkpoint storage c = checkpointData[_blockNumber];
        require(c.set);
        if (c.balances[_owner] > 0) return c.balances[_owner];
        if (c.zeroBalances[_owner]) return 0;
        uint256 _value = token.balanceOf(_owner);
        _setBalance(c, _owner, _value);
        return _value;
    }

    /**
        @notice Query token checkpoint balance
        @param _owner Address of balance to query
        @param _cust Custodian address
        @param _blockNumber Checkpoint block number
        @return uint256 balance at checkpoint
     */
    function custodianBalanceOfAt(
        address _owner,
        address _cust,
        uint256 _blockNumber
    )
        external
        view
        returns (uint256)
    {
        _advanceCheckpoints();
        Checkpoint storage c = checkpointData[_blockNumber];
        require(c.set);
        if (c.custBalances[_owner][_cust] > 0) {
            return c.custBalances[_owner][_cust];
        }
        if (c.custZeroBalances[_owner][_cust]) return 0;
        uint256 _value = token.custodianBalanceOf(_owner, _cust);
        _setCustodianBalance(c, _owner, _cust, _value);
        return _value;
    }

    /**
        @notice Store a checkpoint balance
        @param c Checkpoint storage pointer
        @param _owner Address to set
        @param _value Balance at address
     */
    function _setBalance(
        Checkpoint storage c,
        address _owner,
        uint256 _value
    )
        private
    {
        while (true) {
            if (c.balances[_owner] > 0 || c.zeroBalances[_owner]) return;
            if (_value == 0) {
                c.zeroBalances[_owner] = true;
            } else {
                c.balances[_owner] = _value;
            }
            if (c.previous == 0) return;
            c = checkpointData[c.previous];
        }
    }

    /**
        @notice Store custodian checkpoint balance after tokens are received
        @param c Checkpoint storage pointer
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
            if (
                c.custBalances[_owner][_cust] > 0 ||
                c.custZeroBalances[_owner][_cust]
            ) return;
            if (_value == 0) {
                c.custZeroBalances[_owner][_cust] = true;
            } else {
                c.custBalances[_owner][_cust] = _value;
            }
            if (c.previous == 0) return;
            c = checkpointData[c.previous];
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
        _onlyToken();
        uint256 _previous = _advanceCheckpoints();
        if (_previous == 0) return true;
        Checkpoint storage c = checkpointData[_previous];
        uint256 _bal;

        if (_rating[0] == 0 && _id[0] != ownerID) {
            _bal = token.custodianBalanceOf(_addr[1], _addr[0]).add(_value);
            _setCustodianBalance(c, _addr[1], _addr[0], _bal);
        } else {
            _bal = token.balanceOf(_addr[0]).add(_value);
            _setBalance(c, _addr[0], _bal);
        }
        if (_rating[1] == 0 && _id[1] != ownerID) {
            _bal = token.custodianBalanceOf(_addr[0], _addr[1]).sub(_value);
            _setCustodianBalance(c, _addr[0], _addr[1], _bal);
        } else {
            _bal = token.balanceOf(_addr[1]).sub(_value);
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
        _onlyToken();
        uint256 _previous = _advanceCheckpoints();
        if (_previous == 0) return true;
        Checkpoint storage c = checkpointData[_previous];

        uint256 _bal = token.custodianBalanceOf(_addr[0], _cust).add(_value);
        _setCustodianBalance(c, _addr[0], _cust, _bal);
        _bal = token.custodianBalanceOf(_addr[1], _cust).sub(_value);
        _setCustodianBalance(c, _addr[1], _cust, _bal);
        return true;
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
        _onlyToken();
        _advanceCheckpoints();
        uint64 _next = nextPointer;
        if (_next == 0) return true;
        Checkpoint storage c = checkpointData[_next];
        c.totalSupply = c.totalSupply.add(_new).sub(_old);
        _setBalance(c, _addr, _old);
        return true;
    }

    /**
        @notice Advance token checkpoint and modify total supply
        @return block number of most recently passed checkpoint
     */
    function _advanceCheckpoints() private returns (uint256) {
        if (nextPointer > block.number || nextPointer == 0) {
            return previousPointer;
        }
        Checkpoint storage c = checkpointData[nextPointer];
        uint64 _prev = nextPointer;
        while (c.next != 0) {
            checkpointData[c.next].totalSupply = c.totalSupply;
            if (c.next > block.number) break;
            _prev = c.next;
            c = checkpointData[c.next];
        }
        previousPointer = _prev;
        nextPointer = c.next;
        return _prev;
    }

    /**
        @notice Set a new checkpoint
        @dev callable by a permitted authority or token module
        @param _blockNumber block number to set checkpoint at
        @return bool success
     */
    function newCheckpoint(
        uint64 _blockNumber
    )
        external
        returns (bool)
    {
        require(_blockNumber >= block.number); // dev: blockNumber
        require(issuer.isActiveToken(token)); // dev: token
        if (!token.isPermittedModule(msg.sender, 0x17020cc7)) {
            if (!_onlyAuthority()) return false;
        }
        require(!checkpointData[_blockNumber].set); // dev: already set
        if (nextPointer == 0 || _blockNumber < nextPointer) {
            (uint64 _prev, uint64 _next) = (previousPointer, nextPointer);
            nextPointer = _blockNumber;
            checkpointData[_blockNumber].totalSupply = token.totalSupply();
        } else {
            uint64 _previous = nextPointer;
            while (
                checkpointData[_prev].next != 0 &&
                checkpointData[_prev].next < _blockNumber
            ) {
                _prev = checkpointData[_prev].next;
            }
            _next = checkpointData[_previous].next;
        }
        checkpointData[_prev].next = _blockNumber;
        if (_next != 0) checkpointData[_next].previous = _blockNumber;
        checkpointData[_blockNumber].previous = _prev;
        checkpointData[_blockNumber].next = _next;
        checkpointData[_blockNumber].set = true;
        emit CheckpointSet(_blockNumber);
        return true;
    }

}
