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

    mapping (bytes32 => Option[]) optionData;

    struct ExercisePrice {
        uint64 vestedTotal;
        uint64 unvestedTotal;
        uint32 prev;
        uint32 next;
        bool set;
        uint64[2][] vestMap; // (vested total, expired total)
    }

    struct Option {
        uint64 amount;
        uint32 exercisePrice;
        uint32 vestDate;
        uint32 expiryDate;
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
        @notice view function to get total in money options
        @return dynamic array of (exercise price, total options at price)
     */
    function sortedTotals() external view returns (uint256[2][]) {
        uint256[2][] memory _options = new uint256[2][](exercisePriceLength);
        uint32 _index = exercisePriceLimits[0];
        for (uint256 i = 0; i < exercisePriceLength; i++) {
            _updateVestMap(_index);
            _options[i] = [uint256(_index), totalAtExercisePrice[_index].vestedTotal];
            _index = totalAtExercisePrice[_index].next;
        }
        return _options;
    }

    function getInMoneyOptions(
        bytes32 _id,
        uint256 _perShareConsideration
    )
        external
        view
        returns (
            uint256 _optionCount,
            uint256 _totalExercicePrice
        )
    {
        Option[] storage o = optionData[_id];
        for (uint i; i < o.length; i++) {
            if (o[i].exercisePrice >= _perShareConsideration) continue;
            if (o[i].vestDate > now) continue;
            if (o[i].expiryDate < now) continue;
            uint256 _price = uint256(o[i].amount).mul(o[i].exercisePrice);
            _totalExercicePrice = _totalExercicePrice.add(_price);
            _optionCount = _optionCount.add(o[i].amount);
        }
        return (_optionCount, _totalExercicePrice);
    }

    function getOptions(
        bytes32 _id,
        uint256 _index
    )
        external
        view
        returns (
            uint256 _amount,
            uint256 _exercisePrice,
            uint256 _vestDate,
            uint256 _expiryDate
        )
    {
        Option storage o = optionData[_id][_index];
        return (
            o.amount,
            o.exercisePrice,
            o.vestDate,
            o.expiryDate
        );
    }

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
        @param _monthsToVest array, relative time for options to vest (seconds from now)
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
        uint64 _total;
        uint32 _now = uint32(now.div(2592000).add(1).mul(2592000));
        uint32 _expires = (_now).add(expirationMonths.mul(2592000));
        
        ExercisePrice storage t = totalAtExercisePrice[_exercisePrice];
        if (!t.set) {
            _addExercisePrice(_exercisePrice);
        } else {
            _updateVestMap(_exercisePrice);
        }

        uint256 _indexMax = t.vestMap.length - 1;
        for (uint256 i; i < _amount.length; i++) {

            require(_monthsToVest[i] < expirationMonths);
            t.vestMap[_indexMax - _monthsToVest[i]][0] = t.vestMap[_indexMax - _monthsToVest[i]][0].add(_amount[i]);

            uint32 _vests = _now.add(_monthsToVest[i].mul(2592000));
            optionData[_id].push(Option(
                _amount[i],
                _exercisePrice,
                _vests,
                _expires
            ));
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
        t.unvestedTotal = t.unvestedTotal.add(_total);
        totalOptions = totalOptions.add(_total);
        require(token.authorizedSupply().sub(token.totalSupply()) >= totalOptions);

        return true;
    }

    /**
        @notice modify vesting date for one or more groups of options
        @dev time to vest can only be shortened, not extended
        @param _id investor ID
        @param _idx array, option indexes
        @param _vestDate new absolute time for options to vest
        @return bool success
     */
    function accellerateVestingDate(
        bytes32 _id,
        uint256[] _idx,
        uint32 _vestDate
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        for (uint256 i; i < _idx.length; i++) {
            require(
                optionData[_id][_idx[i]].vestDate >= _vestDate,
                "Cannot extend vesting date"
            );
            optionData[_id][_idx[i]].vestDate = _vestDate;
            emit VestDateModified(_id, _idx[i], _vestDate);
        }
        return true;
    }

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
        Option[] storage o = optionData[_id];
        uint256 _amount;
        for (uint256 i; i < o.length; i++) {
            if (o[i].vestDate > now) {
                _amount = _amount.add(o[i].amount);
                _removeOption(o[i]);
                delete o[i];
            } else {
                uint64[2][] storage _vestMap = totalAtExercisePrice[o[i].exercisePrice].vestMap;
                uint256 x = _getIndex(o[i].expiryDate);
                _vestMap[i][1] = _vestMap[i][1].sub(o[i].amount);
                o[i].expiryDate = uint32(now.div(2592000).add(1).add(terminationGracePeriodMonths).mul(2592000));
                x = _getIndex(o[i].expiryDate);
                _vestMap[x][1] = _vestMap[x][1].add(o[i].amount);
            }
        }
        totalOptions = totalOptions.sub(_amount);
        emit TerminatedOptions(_id, _amount);
        return true;
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

    function _updateVestMap(uint32 _exercisePrice) internal {
        ExercisePrice storage t = totalAtExercisePrice[_exercisePrice];
        uint256 _length = FINAL_MONTH.sub(now).div(2592000);
        if (_length == t.vestMap.length) return;

        uint64 _expiredTotal;
        uint64 _vestedTotal;
        for (uint256 i = _length; i < t.vestMap.length; i++) {
            _expiredTotal = _expiredTotal.add(t.vestMap[i][1]);
            _vestedTotal = _vestedTotal.add(t.vestMap[i][0]);
        }
        totalOptions = totalOptions.sub(_expiredTotal);
        totalVestedOptions = totalVestedOptions.add(_vestedTotal).sub(_expiredTotal);
        t.vestedTotal = t.vestedTotal.add(_vestedTotal).sub( _expiredTotal);
        t.unvestedTotal = t.unvestedTotal.sub(_vestedTotal);
        t.vestMap.length = _length;
        _removeExercisePrice(_exercisePrice);
    }

    /**
        @notice Add an exercise price to totalAtExercisePrice linked list
        @param _price exercise price to add
     */
    function _addExercisePrice(uint32 _price) internal {
        exercisePriceLength += 1;
        ExercisePrice storage t = totalAtExercisePrice[_price];
        t.set = true;
        t.vestMap.length = FINAL_MONTH.sub(now).div(2592000);
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

    function _removeOption(Option memory o) internal {
        ExercisePrice storage t = totalAtExercisePrice[o.exercisePrice];
        if (o.vestDate < now) {
            _updateVestMap(o.exercisePrice);
            if (o.expiryDate < now) return;
            t.vestedTotal = t.vestedTotal.sub(o.amount);
        } else {
            t.unvestedTotal = t.unvestedTotal.sub(o.amount);
            uint256 i = _getIndex(o.vestDate);
            t.vestMap[i][0] = t.vestMap[i][0].sub(o.amount);
        }

        i = _getIndex(o.expiryDate);
        t.vestMap[i][1] = t.vestMap[i][1].sub(o.amount);

        _removeExercisePrice(o.exercisePrice);
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