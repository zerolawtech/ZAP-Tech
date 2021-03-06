pragma solidity 0.4.25;

import "../open-zeppelin/SafeMath.sol";
import {OrgModuleBase} from "./bases/Module.sol";

import "../interfaces/IOrgShare.sol";

/**
    @title MultiCheckpoint Module
    @dev Org level module used to record and access checkpoints across many OrgShares
    @notice Licensed under GNU GPLv3 - https://github.com/zerolawtech/ZAP-Tech/LICENSE
 */
contract MultiCheckpointModule is OrgModuleBase {

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
    struct EpochPointers {
        uint64 previous;
        uint64 next;
    }

    mapping (address => EpochPointers) pointers;
    mapping (address => mapping(uint256 => Checkpoint)) checkpointData;

    event CheckpointSet(address indexed share, uint64 time);

    /**
        @notice Base constructor
        @param _owner OrgCode contract address
     */
    constructor(address _owner) OrgModuleBase(_owner) public {
        return;
    }

    /**
        @notice supply permissions and hook points when attaching module
        @dev
            hooks: 0x0675a5e0 - transferShares
                   0xdc9d1da1 - transferSharesCustodian
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
        hooks[0] = 0x0675a5e0;
        hooks[1] = 0xdc9d1da1;
        hooks[2] = 0x741b5078;

        return (permissions, hooks, ~uint256(0));
    }

    /**
        @notice Check if a checkpoint exists for a given share and time
        @param _share OrgShare contract address
        @param _time Epoch time of checkpoint
        @return boolean
     */
    function checkpointExists(
        address _share,
        uint256 _time
    )
        external
        view
        returns (bool)
    {
        return checkpointData[_share][_time].set;
    }


    /**
        @notice Query share checkpoint totalSupply
        @param _share OrgShare contract address
        @param _time Checkpoint time
        @return uint256 totalSupply at checkpoint
     */
    function totalSupplyAt(
        address _share,
        uint256 _time
    )
        external
        view
        returns (uint256)
    {
        _advanceCheckpoints(_share);
        require(checkpointData[_share][_time].set);
        return checkpointData[_share][_time].totalSupply;
    }

    /**
        @notice Query share checkpoint balance
        @param _share OrgShare contract address
        @param _owner Address of balance to query
        @param _time Checkpoint time
        @return uint256 balance at checkpoint
     */
    function balanceAt(
        IOrgShareBase _share,
        address _owner,
        uint256 _time
    )
        external
        view
        returns (uint256)
    {
        _advanceCheckpoints(_share);
        Checkpoint storage c = checkpointData[_share][_time];
        require(c.set);
        if (c.balances[_owner] > 0) return c.balances[_owner];
        if (c.zeroBalances[_owner]) return 0;
        uint256 _value = _share.balanceOf(_owner);
        _setBalance(c, _owner, _value);
        return _value;
    }

    /**
        @notice Query share checkpoint balance
        @param _share OrgShare contract address
        @param _owner Address of balance to query
        @param _cust Custodian address
        @param _time Checkpoint time
        @return uint256 balance at checkpoint
     */
    function custodianBalanceAt(
        IOrgShareBase _share,
        address _owner,
        address _cust,
        uint256 _time
    )
        external
        view
        returns (uint256)
    {
        _advanceCheckpoints(_share);
        Checkpoint storage c = checkpointData[_share][_time];
        require(c.set);
        if (c.custBalances[_owner][_cust] > 0) {
            return c.custBalances[_owner][_cust];
        }
        if (c.custZeroBalances[_owner][_cust]) return 0;
        uint256 _value = _share.custodianBalanceOf(_owner, _cust);
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
            c = checkpointData[msg.sender][c.previous];
        }
    }

    /**
        @notice Store custodian checkpoint balance after shares are received
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
            c = checkpointData[msg.sender][c.previous];
        }
    }

    /**
        @notice Hook method, record checkpoint value after a transfer
        @param _addr Sender/receiver address
        @param _id Sender/receiver member ID
        @param _rating Sender/receiver rating
        @param _value Amount transferred
        @return bool
     */
    function transferShares(
        address[2] _addr,
        bytes32[2] _id,
        uint8[2] _rating,
        uint16[2],
        uint256 _value
    )
        external
        returns (bool)
    {
        _onlyShare();
        uint256 _previous = _advanceCheckpoints(msg.sender);
        if (_previous == 0) return true;
        Checkpoint storage c = checkpointData[msg.sender][_previous];
        IOrgShareBase _share = IOrgShareBase(msg.sender);
        uint256 _bal;

        if (_rating[0] == 0 && _id[0] != ownerID) {
            _bal = _share.custodianBalanceOf(_addr[1], _addr[0]).add(_value);
            _setCustodianBalance(c, _addr[1], _addr[0], _bal);
        } else {
            _bal = _share.balanceOf(_addr[0]).add(_value);
            _setBalance(c, _addr[0], _bal);
        }
        if (_rating[1] == 0 && _id[1] != ownerID) {
            _bal = _share.custodianBalanceOf(_addr[0], _addr[1]).sub(_value);
            _setCustodianBalance(c, _addr[0], _addr[1], _bal);
        } else {
            _bal = _share.balanceOf(_addr[1]).sub(_value);
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
    function transferSharesCustodian(
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
        _onlyShare();
        uint256 _previous = _advanceCheckpoints(msg.sender);
        if (_previous == 0) return true;
        Checkpoint storage c = checkpointData[msg.sender][_previous];

        IOrgShareBase _share = IOrgShareBase(msg.sender);
        uint256 _bal = _share.custodianBalanceOf(_addr[0], _cust).add(_value);
        _setCustodianBalance(c, _addr[0], _cust, _bal);
        _bal = _share.custodianBalanceOf(_addr[1], _cust).sub(_value);
        _setCustodianBalance(c, _addr[1], _cust, _bal);
        return true;
    }

    /**
        @notice Hook method, record checkpoint value after mint/burn
        @param _addr Member address
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
        _onlyShare();
        _advanceCheckpoints(msg.sender);
        uint64 _next = pointers[msg.sender].next;
        if (_next == 0) return true;
        Checkpoint storage c = checkpointData[msg.sender][_next];
        c.totalSupply = c.totalSupply.add(_new).sub(_old);
        _setBalance(c, _addr, _old);
        return true;
    }

    /**
        @notice Advance share checkpoint and modify total supply
        @param _share Share address of checkpoint to advance
        @return epoch time of most recently passed checkpoint
     */
    function _advanceCheckpoints(address _share) private returns (uint256) {
        EpochPointers storage p = pointers[_share];
        if (p.next > now || p.next == 0) {
            return p.previous;
        }
        Checkpoint storage c = checkpointData[_share][p.next];
        uint64 _prev = p.next;
        while (c.next != 0) {
            checkpointData[_share][c.next].totalSupply = c.totalSupply;
            if (c.next > now) break;
            _prev = c.next;
            c = checkpointData[_share][c.next];
        }
        pointers[_share] = EpochPointers(_prev, c.next);
        return _prev;
    }

    /**
        @notice Set a new checkpoint
        @dev callable by a permitted authority or share module
        @param _share OrgShare contract address to set checkpoint for
        @param _time Epoch time to set checkpoint at
        @return bool success
     */
    function newCheckpoint(
        IOrgShareBase _share,
        uint64 _time
    )
        external
        returns (bool)
    {
        require(_time > now); // dev: time
        require(orgCode.isActiveOrgShare(_share)); // dev: share
        if (!_share.isPermittedModule(msg.sender, 0x17020cc7)) {
            if (!_onlyAuthority()) return false;
        }
        require(!checkpointData[_share][_time].set); // dev: already set
        mapping(uint256 => Checkpoint) c = checkpointData[_share];
        if (pointers[_share].next == 0 || _time < pointers[_share].next) {
            EpochPointers memory p = pointers[_share];
            pointers[_share].next = _time;
            c[_time].totalSupply = _share.totalSupply();
        } else {
            uint64 _previous = pointers[_share].next;
            while (c[_previous].next != 0 && c[_previous].next < _time) {
                _previous = c[_previous].next;
            }
            p = EpochPointers(_previous, c[_previous].next);
        }
        c[p.previous].next = _time;
        if (p.next != 0) c[p.next].previous = _time;
        c[_time].previous = p.previous;
        c[_time].next = p.next;
        c[_time].set = true;
        emit CheckpointSet(_share, _time);
        return true;
    }

}
