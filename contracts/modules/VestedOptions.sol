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
    uint32 public terminationGracePeriodMonths;
    address public receiver;

    /** linked list */
    uint32[2] exercisePriceLimits;
    uint32 exercisePriceLength;
    mapping (uint32 => ExercisePrice) public totalAtExercisePrice;

    /**
        vestMap is a dynamic array of [vested total, expired total] where
        each entry corresponds to a 30 day period, descending from FINAL_MONTH
     */
    struct ExercisePrice {
        bool set;
        uint64 vestedTotal;
        uint64 unvestedTotal;
        uint32 prev;
        uint32 next;
        uint32 length;
        uint64[2][1657] vestMap;
    }

    mapping (bytes32 => mapping (uint32 => Option[])) optionData;

    struct Option {
        bool iso;
        uint64 vestedTotal;
        uint64 unvestedTotal;
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
        ethPeg = _ethPeg;
        expirationMonths = _expireMonths;
        terminationGracePeriodMonths = _gracePeriodMonths;
        receiver = _receiver;
        emit EthPegSet(_ethPeg);
    }

    /**
        @notice get total amount of vested options at each exercise price
        @dev array is sorted by exercise price ascending
        @return dynamic array of (exercise price, total vested options at price)
     */
    function sortedTotals() external view returns (uint256[2][]) {
        uint256[2][] memory _options = new uint256[2][](exercisePriceLength);
        uint32 _price = exercisePriceLimits[0];
        for (uint256 i = 0; i < exercisePriceLength; i++) {
            _updateVestMap(_price);
            _options[i] = [uint256(_price), totalAtExercisePrice[_price].vestedTotal];
            _price = totalAtExercisePrice[_price].next;
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
    //         uint256 _exercisePrice,
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
        @param _exercisePrice exercise price for options being issued
        @param _amount array, quantities of options to issue
        @param _monthsToVest array, relative time for options to vest (months from now)
        @return bool success
     */
    function issueOptions(
        bytes32 _id,
        uint32 _exercisePrice,
        uint64[] _amount,
        uint32[] _monthsToVest
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        require(_exercisePrice > 0); // dev: exercise price == 0
        require(_amount.length == _monthsToVest.length); // dev: length mismatch

        _addExercisePrice(_exercisePrice);
        ExercisePrice storage t = totalAtExercisePrice[_exercisePrice];
        Option storage o = _saveOption(_id, _exercisePrice);

        uint64 _total;
        uint256 _indexMax = t.vestMap.length - 1;
        uint256 _oMax = expirationMonths - 1;

        for (uint256 i; i < _amount.length; i++) {
            require(_monthsToVest[i] < expirationMonths);
            t.vestMap[_indexMax - _monthsToVest[i]][0] = t.vestMap[_indexMax - _monthsToVest[i]][0].add(_amount[i]);

            o.vestMap[_oMax - _monthsToVest[i]] = o.vestMap[_oMax - _monthsToVest[i]].add(_amount[i]);

            _total = _total.add(_amount[i]);
            // TODO - stack too deep
            // emit NewOptions(
            //     _id,
            //     optionData[_id].length-1,
            //     _amount[i],
            //     _exercisePrice,
            //     _vests,
            //     _expires
            // );
        }

        t.vestMap[_indexMax - expirationMonths][1] = t.vestMap[_indexMax - expirationMonths][1].add(_total);
        o.unvestedTotal = o.unvestedTotal.add(_total);
        t.unvestedTotal = t.unvestedTotal.add(_total);
        totalOptions = totalOptions.add(_total);
        require(token.authorizedSupply().sub(token.totalSupply()) >= totalOptions);

        return true;
    }

    function _saveOption(bytes32 _id, uint32 _price) internal returns (Option storage) {
        uint32 _now = uint32(now.div(2592000).add(1).mul(2592000));
        uint32 _expires = (_now).add(expirationMonths.mul(2592000));
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
        @notice modify vesting date for one or more groups of options
        @dev time to vest can only be shortened, not extended
        @param _id investor ID
        @param _idx array, option indexes
        @param _vestDate new absolute time for options to vest
        @return bool success
     */
    // function accellerateVestingDate(
    //     bytes32 _id,
    //     uint256[] _idx,
    //     uint32 _vestDate
    // )
    //     external
    //     returns (bool)
    // {
    //     if (!_onlyAuthority()) return false;
    //     for (uint256 i; i < _idx.length; i++) {
    //         require(
    //             optionData[_id][_idx[i]].vestDate >= _vestDate,
    //             "Cannot extend vesting date"
    //         );
    //         optionData[_id][_idx[i]].vestDate = _vestDate;
    //         emit VestDateModified(_id, _idx[i], _vestDate);
    //     }
    //     return true;
    // }

    /**
        @notice exercise vested options
        @dev payable method, payment must exactly equal:
            exercise price * number of options * eth peg
        @param _idx array, option indexes
        @return bool success
     */
    // function exerciseOptions(uint256[] _idx) external payable returns (bool) {
    //     bytes32 _id = issuer.getID(msg.sender);
    //     uint256 _amount;
    //     uint256 _price;
    //     for (uint256 i; i < _idx.length; i++) {
    //         Option storage o = optionData[_id][_idx[i]];
    //         require(o.vestDate <= now, "Options have not vested");
    //         require(o.expiryDate > now, "Options have expired");
    //         _amount = _amount.add(o.amount);
    //         _price = _price.add(uint256(o.exercisePrice).mul(o.amount));
    //         _reduceTotal(o.exercisePrice, o.amount);
    //         emit ClaimedOptions(_id, _idx[i], o.amount, o.exercisePrice);
    //         delete optionData[_id][_idx[i]];
    //     }
    //     require(msg.value == _price.mul(ethPeg), "Incorrect payment amount");
    //     receiver.transfer(address(this).balance);
    //     totalOptions = totalOptions.sub(_amount);
    //     require(token.mint(msg.sender, _amount));
    //     return true;
    // }

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
        uint32 _price = exercisePriceLimits[0];

        for (uint256 i; i < exercisePriceLength; i++) {
            Option[] storage o = optionData[_id][_price];
            if (o.length > 0) {
                _grandTotal += _terminateOptionsAtPrice(o, _price);
            }
            _price = totalAtExercisePrice[_price].next;
        }
        totalOptions = totalOptions.sub(_grandTotal);
    }

    function _terminateOptionsAtPrice(
        Option[] storage o,
        uint32 _price
    )
        internal
        returns (uint64 _total)
    {
        _updateVestMap(_price);
        uint64[2][1657] storage _vestMap = totalAtExercisePrice[_price].vestMap;
        uint256 _indexMax = totalAtExercisePrice[_price].length - 1;
        for (uint256 i; i < _indexMax; i++) {
            _updateOptionVestMap(o[i]);
            _total = _total.add(o[i].unvestedTotal);
            o[i].unvestedTotal = 0;
            if (o[i].length < terminationGracePeriodMonths) continue;
            _vestMap[_indexMax-o[i].length][1] += o[i].vestedTotal;
            _vestMap[_indexMax-terminationGracePeriodMonths][1] += o[i].vestedTotal;
            uint256 _oMax = o[i].length - 1;
            _indexMax -= _oMax;
            for (uint256 x = _oMax; x+1 == 0; x--) {
                if (o[i].vestMap[x] == 0) continue;
                _vestMap[_indexMax+x][0] -= o[i].vestMap[x];
            }
        }
        totalAtExercisePrice[_price].unvestedTotal -= _total;
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
        @notice update the option totals for a given ExercisePrice struct
        @param _price exercise price to update
     */
    function _updateVestMap(uint32 _price) internal {
        /** if expected length == actual length, values are up to date */
        ExercisePrice storage t = totalAtExercisePrice[_price];
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
        t.vestedTotal = t.vestedTotal.add(_vestedTotal).sub( _expiredTotal);
        t.unvestedTotal = t.unvestedTotal.sub(_vestedTotal);
        t.length = uint32(_length);
        _removeExercisePrice(_price);
    }

    function _updateOptionVestMap(Option storage o) internal {
        uint32 _length = o.expiryDate.sub(uint32(now)).div(2592000);
        if (_length == o.length) return;

        uint64 _total;
        for (uint256 i = _length; i < o.length; i++) {
            if (o.vestMap[i] == 0) continue;
            _total = _total.add(o.vestMap[i]);
            delete o.vestMap[i];
        }
        o.vestedTotal = o.vestedTotal.add(_total);
        o.unvestedTotal = o.unvestedTotal.sub(_total);
        o.length = _length;
    }

    /**
        @notice Add an exercise price to totalAtExercisePrice linked list
        @param _price exercise price to add
     */
    function _addExercisePrice(uint32 _price) internal {
        ExercisePrice storage t = totalAtExercisePrice[_price];
        if (t.set) {
            _updateVestMap(_price);
            return;
        }
        exercisePriceLength += 1;
        t.set = true;
        t.length = uint16(FINAL_MONTH.sub(now).div(2592000));
        if (exercisePriceLimits[0] == 0) {
            exercisePriceLimits = [_price, _price];
            return;
        }
        if (_price > exercisePriceLimits[1]) {
            totalAtExercisePrice[exercisePriceLimits[1]].next = _price;
            t.prev = exercisePriceLimits[1];
            exercisePriceLimits[1] = _price;
            return;
        }
        if (_price < exercisePriceLimits[0]) {
            totalAtExercisePrice[exercisePriceLimits[0]].prev = _price;
            t.next = exercisePriceLimits[0];
            exercisePriceLimits[0] = _price;
            return;
        }
        uint32 i = exercisePriceLimits[0];
        while (totalAtExercisePrice[i].next < _price) {
            i = totalAtExercisePrice[i].next;
        }
        t.prev = i;
        t.next = totalAtExercisePrice[i].next;
        totalAtExercisePrice[t.next].prev = _price;
        totalAtExercisePrice[i].next = _price;
    }

    function _getIndex(uint256 _epoch) internal pure returns (uint256) {
        return FINAL_MONTH.sub(_epoch) / 2592000;
    }

    function _removeExercisePrice(uint32 _price) internal {
        ExercisePrice storage t = totalAtExercisePrice[_price];
        if (t.vestedTotal > 0 || t.unvestedTotal > 0) return;
        exercisePriceLength -= 1;
        if (exercisePriceLimits[0] == _price) {
            exercisePriceLimits[0] = t.next;
        }
        if (exercisePriceLimits[1] == _price) {
            exercisePriceLimits[1] = t.prev;
        }
        if (t.prev != 0) {
            totalAtExercisePrice[t.prev].next = t.next;
        }
        if (t.next != 0) {
            totalAtExercisePrice[t.next].prev = t.prev;
        }
        delete totalAtExercisePrice[_price];
    }

}