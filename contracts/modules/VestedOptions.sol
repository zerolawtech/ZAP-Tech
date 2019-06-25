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

    uint64 public totalOptions;
    uint64 public totalVestedOptions;
    uint64 public ethPeg;
    uint32 public expirationMonths;
    uint32 public gracePeriodMonths;
    address public receiver;

    /** linked list */
    uint32[2] totalLimits;
    uint32 totalLength;
    mapping (uint32 => OptionTotal) public totalAtPrice;
    mapping (bytes32 => mapping (uint32 => Option[])) optionData;

    /**
        vestMap is a array of [vested total, expired total] where each entry
        corresponds to a 30 day period, descending from FINAL_MONTH. length of
        1657 == 2**32 // 2592000 (seconds in 30 days)
     */
    struct OptionTotal {
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

    event EthPegSet(uint256 peg);
    event NewOptions(
        bytes32 indexed id,
        bool iso,
        uint32 exercisePrice,
        uint32 expiryDate,
        uint64[] amount,
        uint32[] vestDate
    );
    event ExercisedOptions(
        bytes32 indexed id,
        uint32 exercisePrice,
        uint64 amount
    );
    event AccelleratedOptions(bytes32 indexed id, uint64 vestedTotal);
    event TerminatedOptions(bytes32 indexed id, uint64 terminatedTotal);

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
        uint64 _ethPeg,
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
    function getSortedTotals() external view returns (uint256[2][] _options) {
        uint32 _price = totalLimits[0];
        while (_price != 0) {
            uint32 _next = totalAtPrice[_price].next;
            _updateOptionTotal(_price);
            _price = _next;
        }
        _options = new uint256[2][](totalLength);
        _price = totalLimits[0];
        for (uint256 i; i < totalLength; i++) {
            _options[i] = [uint256(_price), totalAtPrice[_price].vested];
            _price = totalAtPrice[_price].next;
        }
        return _options;
    }

    /**
        @notice get total options at a given exercise price
        @param _price exercise price
        @return vested total, unvested total
     */
    function getTotalOptionsAtPrice(
        uint32 _price
    )
        external
        view
        returns (
            uint64 _vestedTotal,
            uint64 _unvestedTotal
        )
    {
        _updateOptionTotal(_price);
        return (totalAtPrice[_price].vested, totalAtPrice[_price].unvested);
    }

    /**
        @notice get information about an investor's options
        @param _id investor ID
        @return total vested, total unvested, array of (exercise price, array length)
     */
    function getOptions(
        bytes32 _id
    )
        external
        view
        returns (
            uint64 _vestedTotal,
            uint64 _unvestedTotal,
            uint256[2][] _exercisePrices
        )
    {
        uint256 _length;
        uint32 _price = totalLimits[0];
        while (_price != 0) {
            uint32 _next = totalAtPrice[_price].next;
            if (optionData[_id][_price].length > 0 && _updateOptionTotal(_price)) {
                _length++;
            }
            _price = _next;
        }
        _exercisePrices = new uint256[2][](_length);
        _price = totalLimits[0];
        uint256 i = 0;
        while (_price != 0) {
            Option[] storage o = optionData[_id][_price];
            if (o.length > 0) {
                _exercisePrices[i] = [_price, o.length];
                i++;
                for (uint256 y = 0; y < o.length; y++) {
                    _updateOption(o[y]);
                    _vestedTotal = _vestedTotal.add(o[y].vested);
                    _unvestedTotal = _unvestedTotal.add(o[y].unvested);
                }
            }
            _price = totalAtPrice[_price].next;
        }
        return (_vestedTotal, _unvestedTotal, _exercisePrices);
    }

    /**
        @notice get detailed information about specific options for an investor
        @param _id investor ID
        @param _price exercise price
        @param _idx option array index (use getOptions for possible values)
        @return vested total, unvested total, iso bool, expiry date, vestMap (ascending)
     */
    function getOptionsAtPrice(
        bytes32 _id,
        uint32 _price,
        uint256 _idx
    )
        external
        view
        returns (
            uint64 _vestedTotal,
            uint64 _unvestedTotal,
            bool _iso,
            uint32 _expiryDate,
            uint64[] _vestMap
        )
    {
        Option storage o = optionData[_id][_price][_idx];
        if (!_updateOptionTotal(_price)) return;
        _updateOption(o);
        _vestMap = new uint64[](o.length);
        for (uint256 i; i < o.length; i++) {
            _vestMap[i] = o.vestMap[o.length-1-i];
        }
        return (o.vested, o.unvested, o.iso, o.expiryDate, _vestMap);
    }

    /**
        @notice Get information about in-money options for a given investor
        @param _id investor ID
        @param _perShareConsideration per-share consideration to be paid
        @return number of options that are in the money
        @return aggregate exercise price for in-money options
     */
    function getInMoneyOptions(
        bytes32 _id,
        uint256 _perShareConsideration
    )
        external
        view
        returns (
            uint256 _optionCount,
            uint256 _totalExercisePrice
        )
    {
        uint32 _price = totalLimits[0];
        while (_price != 0 && _price < _perShareConsideration) {
            Option[] storage o = optionData[_id][_price];
            uint32 _next = totalAtPrice[_price].next;
            if (o.length > 0 && _updateOptionTotal(_price)) {
                uint256 _total = 0;
                for (uint256 x = 0; x < o.length; x++) {
                    _updateOption(o[x]);
                    if (o[x].vested == 0) continue;
                    _total = _total.add(o[x].vested);
                    _totalExercisePrice = _totalExercisePrice.add(o[x].vested.mul(_price));
                }
                _optionCount = _optionCount.add(_total);
            }
            _price = _next;
        }
        return (_optionCount, _totalExercisePrice);
    }

    /**
        @notice Modify eth peg
        @dev
            The peg is multiplied by the exercise price to determine the amount
            in wei that must be paid when exercising an option.
        @param _peg new peg value
        @return bool
     */
    function modifyPeg(uint64 _peg) external returns (bool) {
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
        bool _iso,
        uint64[] _amount,
        uint32[] _monthsToVest
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        require(_price > 0); // dev: exercise price == 0
        require(_amount.length == _monthsToVest.length); // dev: length mismatch

        /* get storage structs */
        OptionTotal storage t = _addExercisePrice(_price);
        Option storage o = _saveOption(_id, _price, _iso);

        uint64 _total;
        uint256 _tMax = t.length - 1;
        uint256 _oMax = expirationMonths - 1;

        for (uint256 i; i < _amount.length; i++) {
            require(_monthsToVest[i] <= _oMax); // dev: vest > expiration

            /* add to Option and OptionTotal vestMaps */
            uint256 _idx = _tMax - _monthsToVest[i];
            t.vestMap[_idx][0] = t.vestMap[_idx][0].add(_amount[i]);
            _idx = _oMax - _monthsToVest[i];
            o.vestMap[_idx] = o.vestMap[_idx].add(_amount[i]);

            _total = _total.add(_amount[i]);
        }

        /* store expiration amount */
        _idx = _tMax - expirationMonths;
        t.vestMap[_idx][1] = t.vestMap[_idx][1].add(_total);
        
        /* increase totals, final check */
        o.unvested = o.unvested.add(_total);
        t.unvested = t.unvested.add(_total);
        totalOptions = totalOptions.add(_total);
        require(token.authorizedSupply().sub(token.totalSupply()) >= totalOptions); // dev: exceeds authorized
        // TODO emit event
        return true;
    }

    /**
        @notice Add an exercise price to totalAtPrice linked list
        @param _price exercise price to add
        @return OptionTotal struct
     */
    function _addExercisePrice(uint32 _price) internal returns (OptionTotal storage t) {
        t = totalAtPrice[_price];
        if (_updateOptionTotal(_price)) return t;

        /* add new entry to totalAtPrice */
        totalLength = totalLength.add(1);
        t.length = uint16(FINAL_MONTH.sub(now).div(2592000));

        if (totalLength == 1) {
            /* length is 1, min and max are both the new entry */
            totalLimits = [_price, _price];
            return t;
        }
        if (_price > totalLimits[1]) {
            /* new value is greater than previous upper limit */
            totalAtPrice[totalLimits[1]].next = _price;
            t.prev = totalLimits[1];
            totalLimits[1] = _price;
            return t;
        }
        if (_price < totalLimits[0]) {
            /* new value is less than previous lower limit */
            totalAtPrice[totalLimits[0]].prev = _price;
            t.next = totalLimits[0];
            totalLimits[0] = _price;
            return t;
        }
        /* iterate totalAtPrice to find where to insert new entry */
        uint32 i = totalLimits[0];
        while (totalAtPrice[i].next < _price) {
            i = totalAtPrice[i].next;
        }
        /* add new entry */
        t.prev = i;
        t.next = totalAtPrice[i].next;
        totalAtPrice[t.next].prev = _price;
        totalAtPrice[i].next = _price;
        return t;
    }

    /**
        @notice Extends an OptionData array if needed, and returns an Option struct
        @param _id investor ID
        @param _price exercise price to add
        @return Option struct
     */
    function _saveOption(
        bytes32 _id,
        uint32 _price,
        bool _iso
    )
        internal
        returns (Option storage)
    {
        uint32 _expires = _getEpoch(expirationMonths);
        Option[] storage _options = optionData[_id][_price];
        uint256 i = _options.length;
        if (i > 0 && _options[i-1].expiryDate == _expires) {
            /* struct exists for this expiration date */
            require(_iso == _options[i-1].iso); // dev: iso mismatch
            return _options[i-1];
        }
        /* add new struct to end of array */
        _options.length++;
        Option storage o = _options[i];
        if (_iso) {
            o.iso = _iso;
        }
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
        require (ethPeg.mul(_amount).mul(_price) == msg.value, "Incorrect payment");

        bytes32 _id = issuer.getID(msg.sender);
        Option[] storage o = optionData[_id][_price];
        require(o.length > 0 && _updateOptionTotal(_price), "No options at this price");

        uint64 _remaining = _amount;
        for (uint256 i; i < o.length; i++) {
            /* iterate Options and reduce vested amounts */
            _updateOption(o[i]);
            if (o[i].vested == 0) continue;
            if (o[i].vested < _remaining) {
                _remaining = _remaining.sub(o[i].vested);
                o[i].vested = 0;
                continue;
            }
            /* success! reduce totals */
            o[i].vested = o[i].vested.sub(_remaining);
            totalAtPrice[_price].vested = totalAtPrice[_price].vested.sub(_amount);
            _removeOptionTotal(_price);
            totalOptions = totalOptions.sub(_amount);
            totalVestedOptions = totalVestedOptions.sub(_amount);

            /* transfer eth, mint tokens */
            receiver.transfer(address(this).balance);
            require(token.mint(msg.sender, _amount));
            emit ExercisedOptions(_id, _price, _amount);
            return true;
        }
        revert("Insufficient vested options");
    }

    /**
        @notice Immediately vest all options for a given investor ID
        @param _id investor ID
        @return bool success
     */
    function accellerateVesting(bytes32 _id) external returns (bool) {
        if (!_onlyAuthority()) return false;

        uint64 _grandTotal;
        uint32 _price = totalLimits[0];

        /* iterate exercise prices */
        while (_price != 0) {
            Option[] storage o = optionData[_id][_price];
            uint32 _next = totalAtPrice[_price].next;
            if (o.length > 0) {
                uint64 _total = 0;
                /* iterate Options, increase vested total by unvested total */
                for (uint256 i = 0; i < o.length; i++) {
                    if (o[i].unvested == 0) continue;
                    o[i].vested = o[i].vested.add(o[i].unvested);
                }
                /* remove unvested totals from Option vestMaps */
                _total = _deleteUnvestedOptions(o, _price, 0);
                if (_total > 0) {
                    /* modify totals */
                    totalAtPrice[_price].vested = totalAtPrice[_price].vested.add(_total);
                    _grandTotal = _grandTotal.add(_total);
                }
            }
            _price = _next;
        }
        totalVestedOptions = totalVestedOptions.add(_grandTotal);
        emit AccelleratedOptions(_id, _grandTotal);
        return true;
    }

    /**
        @notice Terminate options
        @dev
            Terminates all unvested options associated with an investor ID.
            Options that have already vested will have their expiration date
            decreased to gracePeriodMonths * 2592000
        @param _id Investor ID
        @return bool success
     */
    function terminateOptions(bytes32 _id) external returns (bool) {
        if (!_onlyAuthority()) return false;
        
        uint64 _grandTotal;
        uint32 _price = totalLimits[0];

        while (_price != 0) {
            Option[] storage o = optionData[_id][_price];
            uint32 _next = totalAtPrice[_price].next;
            if (o.length > 0) {
                _grandTotal = _grandTotal.add(
                    _deleteUnvestedOptions(o, _price, gracePeriodMonths)
                );
            }
            _price = _next;
        }
        totalOptions = totalOptions.sub(_grandTotal);
        emit TerminatedOptions(_id, _grandTotal);
        return true;
    }

    /**
        @notice Delete unvested options
        @dev if _gracePeriod is left as 0, it is not adjusted
        @param o storage pointer to Option[] array
        @param _price Option exercise price
        @param _gracePeriod Adjusted grace period for vested options
        @return total deleted options
     */
    function _deleteUnvestedOptions(
        Option[] storage o,
        uint32 _price,
        uint32 _gracePeriod 
    )
        internal
        returns (uint64 _total)
    {
        _updateOptionTotal(_price);
        uint64[2][1657] storage _vestMap = totalAtPrice[_price].vestMap;
        uint256 _tMax = totalAtPrice[_price].length - 1;
        for (uint256 i; i <= o.length; i++) {
            /* ensure Option vestMap is accurate */
            _updateOption(o[i]);
            if (o[i].length == 0) continue;

            /* iterate vestMap, delete unvested options */
            uint256 _oMax = o[i].length - 1;
            uint256 _tMin = _tMax.sub(_oMax);
            for (uint256 x = _oMax; x+1 == 0; x--) {
                if (o[i].vestMap[x] == 0) continue;
                _vestMap[_tMin+x][0] = _vestMap[_tMin+x][0].sub(o[i].vestMap[x]);
            }
            _total = _total.add(o[i].unvested);
            o[i].unvested = 0;

            /* adjust expiration date */
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
        @notice advance vestMap and update totals for an OptionTotal struct
        @dev also updates totalOptions and totalVestedOptions
        @param _price exercise price to update
     */
    function _updateOptionTotal(uint32 _price) internal returns (bool) {
        /* if expected length == actual length, values are up to date */
        OptionTotal storage t = totalAtPrice[_price];
        if (t.length == 0) return false;
        uint256 _length = FINAL_MONTH.sub(now).div(2592000);
        if (_length >= t.length) return _length > 0;

        /* sum expired and vested options for months that have passed */
        uint64 _expiredTotal;
        uint64 _vestedTotal;
        for (uint256 i = _length; i < t.length; i++) {
            if (t.vestMap[i][0] == 0 && t.vestMap[i][1] == 0) continue;
            _expiredTotal = _expiredTotal.add(t.vestMap[i][1]);
            _vestedTotal = _vestedTotal.add(t.vestMap[i][0]);
            delete t.vestMap[i];
        }

        /* adjust totals and remove previous months */
        if (_vestedTotal > 0) {
            totalVestedOptions = totalVestedOptions.add(_vestedTotal).sub(_expiredTotal);
            t.vested = t.vested.add(_vestedTotal).sub( _expiredTotal);
            t.unvested = t.unvested.sub(_vestedTotal);
        }
        if (_expiredTotal > 0) {
            totalOptions = totalOptions.sub(_expiredTotal);
        }

        /* only store length if entry was not removed */
        if (!_removeOptionTotal(_price)) {
            t.length = uint32(_length);
        }
        return t.length > 0;
    }

    /**
        @notice advance vestMap and update totals for an Option struct
        @dev
            this method does not update any totals outside of the struct, it
            should only be called along with _updateOptionTotal
        @param o Option storage pointer
     */
    function _updateOption(Option storage o) internal {
        /* if expected length == actual length, values are up to date */
        uint32 _length;
        if (now < o.expiryDate) {
            _length = o.expiryDate.sub(uint32(now)).div(2592000);
            if (_length >= o.length) return;
        }

        /* sum vested options for months that have passed */
        uint64 _vestedTotal;
        for (uint256 i = _length; i < o.length; i++) {
            if (o.vestMap[i] == 0) continue;
            _vestedTotal = _vestedTotal.add(o.vestMap[i]);
            delete o.vestMap[i];
        }

        /* adjust totals and remove previous months */
        o.vested = o.vested.add(_vestedTotal);
        o.unvested = o.unvested.sub(_vestedTotal);
        o.length = _length;
    }

    /**
        @notice check if an OptionTotal is empty, and if yes remove it
        @param _price exercise price to check / remove
        @return bool was OptionTotal removed?
     */
    function _removeOptionTotal(uint32 _price) internal returns (bool) {
        OptionTotal storage t = totalAtPrice[_price];
        if (t.vested > 0 || t.unvested > 0) return false;
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
        t.prev = 0;
        t.next = 0;
        t.length = 0;
        return true;
    }

    /** @dev generate an epoch time based on a number of months */
    function _getEpoch(uint32 _months) internal view returns (uint32) {
        uint32 _now = uint32(now.div(2592000).add(1).mul(2592000));
        return _now.add(_months.mul(2592000));
    }

}
