pragma solidity >=0.4.24 <0.5.0;

import "./bases/Module.sol";
import "../open-zeppelin/SafeMath.sol";

/**
    @title Vested Options Module
    @dev attached at token
 */
contract VestedOptions is STModuleBase {

    using SafeMath for uint256;
    using SafeMath32 for uint32;
    using SafeMath64 for uint64;

    string public constant name = "Options";
    uint256 constant FINAL_MONTH = 4294944000;

    uint256 public totalOptions;
    uint256 public totalVestedOptions;
    uint256 public ethPeg;
    uint32 public expirationMonths;
    uint32 public gracePeriodMonths;
    address public receiver;

    /** linked list */
    uint32[2] totalLimits;
    uint32 totalLength;
    mapping (uint32 => OptionTotal) public totalAtPrice;
    mapping (bytes32 => mapping (uint32 => Option[])) optionData;

    /**
        vestMap is a dynamic array of [vested total, expired total] where
        each entry corresponds to a 30 day period, descending from FINAL_MONTH
     */
    struct OptionTotal {
        bool set;
        uint64 vested;
        uint64 unvested;
        uint32 prev;
        uint32 next;
        uint32 length;
        uint64[2][1657] vestMap;
    }

    struct Option {
        bool iso;
        uint64 vested;
        uint64 unvested;
        uint32 expiryDate;
        uint32 length;
        uint64[1657] vestMap;
    }


    event NewOptions(
        bytes32 indexed id,
        uint256 index,
        uint256 amount,
        uint256 exercisePrice,
        uint32 vestDate,
        uint32 expiryDate
    );
    event VestDateModified(bytes32 indexed id, uint256 index, uint32 vestDate);
    event EthPegSet(uint256 peg);
    event ClaimedOptions(
        bytes32 indexed id,
        uint256 index,
        uint256 amount,
        uint256 exercisePrice
    );
    event ExpiredOptions(bytes32 indexed id, uint256 index, uint256 amount);
    event TerminatedOptions(bytes32 indexed id, uint256 amount);

    /**
        @notice supply permissions and hook points when attaching module
        @dev
            permissions: 0x40c10f19 - mint
            hooks: 0x741b5078 - totalSupplyChanged
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
        permissions = new bytes4[](1);
        permissions[0] = 0x40c10f19;
        hooks = new bytes4[](1);
        hooks[0] = 0x741b5078;
        return (permissions, hooks, ~uint256(0));
    }

    /**
        @notice constructor
        @param _token token address
        @param _issuer issuer address
        @param _ethPeg initial ethereum peg rate
        @param _expireMonths time for options to expire, in months
        @param _gracePeriodMonths number of months that already vested options
                                  are claimable if terminated
        @param _receiver address to send ETH to when options are exercised
     */
    constructor(
        SecurityToken _token,
        address _issuer,
        uint256 _ethPeg,
        uint32 _expireMonths,
        uint32 _gracePeriodMonths,
        address _receiver
    )
        public
        STModuleBase(_token, _issuer)
    {
        require(_expireMonths > 0);
        require(_gracePeriodMonths > 0);
        ethPeg = _ethPeg;
        expirationMonths = _expireMonths;
        gracePeriodMonths = _gracePeriodMonths;
        receiver = _receiver;
        emit EthPegSet(_ethPeg);
    }

    /**
        @notice get total amount of vested options at each exercise price
        @dev array is sorted by exercise price ascending
        @return dynamic array of (exercise price, total vested options at price)
     */
    function sortedTotals() external view returns (uint256[2][]) {
        uint256[2][] memory _options = new uint256[2][](totalLength);
        uint32 _price = totalLimits[0];
        for (uint256 i = 0; i < totalLength; i++) {
            _updateVestMap(_price);
            _options[i] = [uint256(_price), totalAtPrice[_price].vested];
            _price = totalAtPrice[_price].next;
        }
        return _options;
    }

    /**
        @notice Get information about in-money options for a given investor
        @param _id investor ID
        @param _perShareConsideration per-share consideration to be paid
        @return number of options that are in the money
        @return aggregate exercise price for in-money options
     */
    // function getInMoneyOptions(
    //     bytes32 _id,
    //     uint256 _perShareConsideration
    // )
    //     external
    //     view
    //     returns (
    //         uint256 _optionCount,
    //         uint256 _totalExercisePrice
    //     )
    // {
    //     Option[] storage o = optionData[_id];
    //     for (uint i; i < o.length; i++) {
    //         if (o[i].exercisePrice >= _perShareConsideration) continue;
    //         if (o[i].vestDate > now) continue;
    //         if (o[i].expiryDate < now) continue;
    //         uint256 _price = uint256(o[i].amount).mul(o[i].exercisePrice);
    //         _totalExercisePrice = _totalExercisePrice.add(_price);
    //         _optionCount = _optionCount.add(o[i].amount);
    //     }
    //     return (_optionCount, _totalExercisePrice);
    // }

    // function getOptions(
    //     bytes32 _id,
    //     uint256 _index
    // )
    //     external
    //     view
    //     returns (
    //         uint256 _amount,
    //         uint256 _price,
    //         uint256 _vestDate,
    //         uint256 _expiryDate
    //     )
    // {
    //     Option storage o = optionData[_id][_index];
    //     return (
    //         o.amount,
    //         o.exercisePrice,
    //         o.vestDate,
    //         o.expiryDate
    //     );
    // }

    /**
        @notice Modify eth peg
        @dev
            The peg is multiplied by the exercise price to determine the amount
            in wei that must be paid when exercising an option.
        @param _peg new peg value
        @return bool
     */
    function modifyPeg(uint256 _peg) external returns (bool) {
        if (!_onlyAuthority()) return false;
        ethPeg = _peg;
        emit EthPegSet(_peg);
        return true;
    }

    /**
        @notice issue new options
        @param _id investor ID
        @param _price exercise price for options being issued
        @param _amount array, quantities of options to issue
        @param _monthsToVest array, relative time for options to vest (months from now)
        @return bool success
     */
    function issueOptions(
        bytes32 _id,
        uint32 _price,
        uint64[] _amount,
        uint32[] _monthsToVest
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        require(_price > 0); // dev: exercise price == 0
        require(_amount.length == _monthsToVest.length); // dev: length mismatch

        _addExercisePrice(_price);
        OptionTotal storage t = totalAtPrice[_price];
        Option storage o = _saveOption(_id, _price);

        uint64 _total;
        uint256 _tMax = t.vestMap.length - 1;
        uint256 _oMax = expirationMonths - 1;

        for (uint256 i; i < _amount.length; i++) {
            require(_monthsToVest[i] < expirationMonths);
            uint256 _idx = _tMax - _monthsToVest[i];
            t.vestMap[_idx][0] = t.vestMap[_idx][0].add(_amount[i]);

            _idx = _oMax - _monthsToVest[i];
            o.vestMap[_idx] = o.vestMap[_idx].add(_amount[i]);

            _total = _total.add(_amount[i]);
            // TODO - stack too deep
            // emit NewOptions(
            //     _id,
            //     optionData[_id].length-1,
            //     _amount[i],
            //     _price,
            //     _vests,
            //     _expires
            // );
        }

        _idx = _tMax - expirationMonths;
        t.vestMap[_idx][1] = t.vestMap[_idx][1].add(_total);
        
        o.unvested = o.unvested.add(_total);
        t.unvested = t.unvested.add(_total);
        totalOptions = totalOptions.add(_total);
        require(token.authorizedSupply().sub(token.totalSupply()) >= totalOptions);

        return true;
    }

    /**
        @notice Add an exercise price to totalAtPrice linked list
        @param _price exercise price to add
     */
    function _addExercisePrice(uint32 _price) internal {
        OptionTotal storage t = totalAtPrice[_price];
        if (t.set) {
            _updateVestMap(_price);
            return;
        }
        totalLength = totalLength.add(1);
        t.set = true;
        t.length = uint16(FINAL_MONTH.sub(now).div(2592000));
        if (totalLimits[0] == 0) {
            totalLimits = [_price, _price];
            return;
        }
        if (_price > totalLimits[1]) {
            totalAtPrice[totalLimits[1]].next = _price;
            t.prev = totalLimits[1];
            totalLimits[1] = _price;
            return;
        }
        if (_price < totalLimits[0]) {
            totalAtPrice[totalLimits[0]].prev = _price;
            t.next = totalLimits[0];
            totalLimits[0] = _price;
            return;
        }
        uint32 i = totalLimits[0];
        while (totalAtPrice[i].next < _price) {
            i = totalAtPrice[i].next;
        }
        t.prev = i;
        t.next = totalAtPrice[i].next;
        totalAtPrice[t.next].prev = _price;
        totalAtPrice[i].next = _price;
    }

    function _saveOption(bytes32 _id, uint32 _price) internal returns (Option storage) {
        uint32 _expires = _getEpoch(expirationMonths);
        uint256 i = optionData[_id][_price].length;
        if (i > 0 && optionData[_id][_price][i-1].expiryDate == _expires) {
            return optionData[_id][_price][i-1];
        }
        optionData[_id][_price].length++;
        Option storage o = optionData[_id][_price][i];
        o.iso = true;
        o.expiryDate = _expires;
        o.length = expirationMonths;
        return o;
    }

    /**
        @notice exercise vested options
        @dev payable method, payment must exactly equal:
            exercise price * amount * eth peg
        @param _price option exercise price
        @param _amount number of options to exercise
        @return bool success
     */
    function exerciseOptions(
        uint32 _price,
        uint64 _amount
    )
        external
        payable
        returns (bool)
    {
        require (
            ethPeg.mul(_amount).mul(_price) == msg.value,
            "Incorrect Payment Amount"
        );
        bytes32 _id = issuer.getID(msg.sender);

        Option[] storage o = optionData[_id][_price];
        require(o.length > 1);
        uint64 _remaining = _amount;
        _updateVestMap(_price);
        for (uint256 i; i < o.length; i++) {
            _updateOptionVestMap(o[i]);
            if (o[i].vested == 0) continue;
            if (o[i].vested < _remaining) {
                _remaining = _remaining.sub(o[i].vested);
                o[i].vested = 0;
                continue;
            }
            o[i].vested = o[i].vested.sub(_remaining);
            totalAtPrice[_price].vested = totalAtPrice[_price].vested.sub(_amount);
            receiver.transfer(address(this).balance);
            totalOptions = totalOptions.sub(_amount);
            totalVestedOptions = totalVestedOptions.sub(_amount);
            require(token.mint(msg.sender, _amount));
            return true;
        }
        revert("Insufficient vested options");
    }

    /**
        @notice modify vesting date for one or more groups of options
        @dev time to vest can only be shortened, not extended
        @param _id investor ID
        @return bool success
     */
    function accellerateVesting(bytes32 _id) external returns (bool) {
        if (!_onlyAuthority()) return false;
        
        uint64 _grandTotal;
        uint32 _price = totalLimits[0];

        for (uint256 i; i < totalLength; i++) {
            Option[] storage o = optionData[_id][_price];
            if (o.length > 0) {
                uint64 _total = 0;
                for (uint256 x = 0; x < o.length; x++) {
                    if (o[x].unvested == 0) continue;
                    o[x].vested = o[x].vested.add(o[x].unvested);
                    _total = _total.add(_deleteUnvestedOptions(o, _price, 0));
                }
                if (_total > 0) {
                    totalAtPrice[_price].vested = totalAtPrice[_price].vested.add(_total);
                    _grandTotal = _grandTotal.add(_total);
                }
            }
            _price = totalAtPrice[_price].next;
        }
        totalVestedOptions = totalVestedOptions.add(_grandTotal);
    }

    /**
        @notice Terminate options
        @dev
            Terminates all options associated with an investor ID. Any
            groups that had already vested will still be available for
            terminationGracePeriod seconds.
        @param _id Investor ID
        @return bool success
     */
    function terminateOptions(bytes32 _id) external returns (bool) {
        if (!_onlyAuthority()) return false;
        
        uint64 _grandTotal;
        uint32 _price = totalLimits[0];

        for (uint256 i; i < totalLength; i++) {
            Option[] storage o = optionData[_id][_price];
            if (o.length > 0) {
                _grandTotal = _grandTotal.add(_deleteUnvestedOptions(o, _price, gracePeriodMonths));
            }
            _price = totalAtPrice[_price].next;
        }
        totalOptions = totalOptions.sub(_grandTotal);
    }

    function _deleteUnvestedOptions(
        Option[] storage o,
        uint32 _price,
        uint32 _gracePeriod 
    )
        internal
        returns (uint64 _total)
    {
        _updateVestMap(_price);
        uint64[2][1657] storage _vestMap = totalAtPrice[_price].vestMap;
        uint256 _tMax = totalAtPrice[_price].length - 1;
        for (uint256 i; i < _tMax; i++) {

            // ensure vestMap is accurate
            _updateOptionVestMap(o[i]);

            // delete unvested options
            uint256 _oMax = o[i].length - 1;
            _tMax = _tMax.sub(_oMax);
            for (uint256 x = _oMax; x+1 == 0; x--) {
                if (o[i].vestMap[x] == 0) continue;
                _vestMap[_tMax+x][0] = _vestMap[_tMax+x][0].sub(o[i].vestMap[x]);
            }
            _total = _total.add(o[i].unvested);
            o[i].unvested = 0;

            // adjust expiration date
            if (_gracePeriod == 0 || o[i].length < _gracePeriod) continue;
            _vestMap[_tMax-o[i].length][1] = _vestMap[_tMax-o[i].length][1].sub(o[i].vested);
            _vestMap[_tMax-_gracePeriod][1] = _vestMap[_tMax-_gracePeriod][1].add(o[i].vested);
            o[i].expiryDate = _getEpoch(_gracePeriod);
        }
        totalAtPrice[_price].unvested = totalAtPrice[_price].unvested.sub(_total);
        return _total;
    }

    /**
        @notice Total supply hook point method
        @dev Prevents totalSupply + totalOptions from exceeding authorizedSupply
     */
    function totalSupplyChanged(
        address,
        bytes32,
        uint8,
        uint16,
        uint256 _old,
        uint256 _new
    )
        external
        view
        returns (bool)
    {
        if (_old > _new) {
            require(token.authorizedSupply().sub(token.totalSupply()) >= totalOptions);
        }
        return true;
        
    }

    /**
        @notice update the option totals for a given OptionTotal struct
        @param _price exercise price to update
     */
    function _updateVestMap(uint32 _price) internal {
        /** if expected length == actual length, values are up to date */
        OptionTotal storage t = totalAtPrice[_price];
        uint256 _length = FINAL_MONTH.sub(now).div(2592000);
        if (_length == t.length) return;

        /** sum expired and vested options for months that have passed */
        uint64 _expiredTotal;
        uint64 _vestedTotal;
        for (uint256 i = _length; i < t.length; i++) {
            if (t.vestMap[i][0] == 0 && t.vestMap[i][1] == 0) continue;
            _expiredTotal = _expiredTotal.add(t.vestMap[i][1]);
            _vestedTotal = _vestedTotal.add(t.vestMap[i][0]);
            delete t.vestMap[i];
        }

        /** adjust totals and remove previous months */
        totalOptions = totalOptions.sub(_expiredTotal);
        totalVestedOptions = totalVestedOptions.add(_vestedTotal).sub(_expiredTotal);
        t.vested = t.vested.add(_vestedTotal).sub( _expiredTotal);
        t.unvested = t.unvested.sub(_vestedTotal);
        t.length = uint32(_length);
        _removeExercisePrice(_price);
    }

    function _updateOptionVestMap(Option storage o) internal {
        uint32 _length = o.expiryDate.sub(uint32(now)).div(2592000);
        if (_length >= o.length) return;

        uint64 _total;
        for (uint256 i = _length; i < o.length; i++) {
            if (o.vestMap[i] == 0) continue;
            _total = _total.add(o.vestMap[i]);
            delete o.vestMap[i];
        }
        o.vested = o.vested.add(_total);
        o.unvested = o.unvested.sub(_total);
        o.length = _length;
    }



    function _getIndex(uint256 _epoch) internal pure returns (uint256) {
        return FINAL_MONTH.sub(_epoch) / 2592000;
    }

    function _removeExercisePrice(uint32 _price) internal {
        OptionTotal storage t = totalAtPrice[_price];
        if (t.vested > 0 || t.unvested > 0) return;
        totalLength = totalLength.sub(1);
        if (totalLimits[0] == _price) {
            totalLimits[0] = t.next;
        }
        if (totalLimits[1] == _price) {
            totalLimits[1] = t.prev;
        }
        if (t.prev != 0) {
            totalAtPrice[t.prev].next = t.next;
        }
        if (t.next != 0) {
            totalAtPrice[t.next].prev = t.prev;
        }
        delete totalAtPrice[_price];
    }

    function _getEpoch(uint32 _months) internal view returns (uint32) {
        uint32 _now = uint32(now.div(2592000).add(1).mul(2592000));
        return _now.add(_months.mul(2592000));
    }

}
