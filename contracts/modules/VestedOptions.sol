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

    string public constant name = "Options";

    uint256 public totalOptions;
    uint256 public ethPeg;
    uint32 public expiryDate;
    uint32 public terminationGracePeriod;
    address public receiver;

    /** linked list */
    uint96[2] exercisePriceLimits;
    uint64 exercisePriceLength;
    mapping (uint96 => ExercisePrice) public totalAtExercisePrice;

    mapping (bytes32 => uint256) public options;
    mapping (bytes32 => Option[]) optionData;

    struct ExercisePrice {
        uint256 total;
        uint96 prev;
        uint96 next;
    }

    struct Option {
        uint96 amount;
        uint96 exercisePrice;
        uint32 creationDate;
        uint32 vestDate;
    }

    event NewOptions(
        bytes32 indexed id,
        uint256 index,
        uint256 amount,
        uint256 exercisePrice,
        uint32 creationDate,
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
        @param _expiry time for options to expire, in seconds
        @param _gracePeriod amount of time that already vested options are
                            claimable if terminated
        @param _receiver address to send ETH to when options are exercised
     */
    constructor(
        SecurityToken _token,
        address _issuer,
        uint256 _ethPeg,
        uint32 _expiry,
        uint32 _gracePeriod,
        address _receiver
    )
        public
        STModuleBase(_token, _issuer)
    {
        ethPeg = _ethPeg;
        expiryDate = _expiry;
        terminationGracePeriod = _gracePeriod;
        receiver = _receiver;
        emit EthPegSet(_ethPeg);
    }

    /**
        @notice view function to get total in money options
        @return dynamic array of (exercise price, total options at price)
     */
    function getOptions() external view returns (uint256[2][]) {
        uint256[2][] memory _options = new uint256[2][](exercisePriceLength);
        uint96 _index = exercisePriceLimits[0];
        for (uint256 i = 0; i < exercisePriceLength; i++) {
            _options[i] = [_index, totalAtExercisePrice[_index].total];
            _index = totalAtExercisePrice[_index].next;
        }
        return _options;
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
        @param _vestDate array, relative time for options to vest (seconds from now)
        @return bool success
     */
    function issueOptions(
        bytes32 _id,
        uint96 _exercisePrice,
        uint96[] _amount,
        uint32[] _vestDate
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        require(_amount.length == _vestDate.length); // dev: length mismatch
        uint256 _total;
        uint32 _now = uint32(now);
        for (uint256 i; i < _amount.length; i++) {
            optionData[_id].push(Option(
                _amount[i],
                _exercisePrice,
                _now,
                _now.add(_vestDate[i])
            ));
            _total = _total.add(_amount[i]);
            emit NewOptions(
                _id,
                optionData[_id].length-1,
                _amount[i],
                _exercisePrice,
                _now,
                _now.add(_vestDate[i]),
                _now.add(expiryDate)
            );
        }
        options[_id] = options[_id].add(_total);
        totalOptions = totalOptions.add(_total);

        ExercisePrice storage t = totalAtExercisePrice[_exercisePrice];
        if (t.total == 0) {
            _addExercisePrice(_exercisePrice);
        }
        t.total = t.total.add(_total);

        return true;
    }

    /**
        @notice Add an exercise price to totalAtExercisePrice linked list
        @param _price exercise price to add
     */
    function _addExercisePrice(uint96 _price) internal {
        exercisePriceLength += 1;
        if (exercisePriceLimits[0] == 0) {
            exercisePriceLimits = [_price, _price];
            return;
        }
        ExercisePrice storage t = totalAtExercisePrice[_price];
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
        uint96 i = exercisePriceLimits[0];
        while (totalAtExercisePrice[i].next < _price) {
            i = totalAtExercisePrice[i].next;
        }
        t.prev = i;
        t.next = totalAtExercisePrice[i].next;
        totalAtExercisePrice[t.next].prev = _price;
        totalAtExercisePrice[i].next = _price;
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
        @notice reduces values of totalAtExercisePrice and exercisePrices
        @param _price exercise price to modify
        @param _amount amount to reduce total by
     */
    function _reduceTotal(uint96 _price, uint256 _amount) internal {
        ExercisePrice storage t = totalAtExercisePrice[_price];
        assert(t.total >= _amount); // TODO: remove me eventually, this should never happen
        if (t.total > _amount) {
            t.total = t.total.sub(_amount);
            return;
        }
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

    /**
        @notice exercise vested options
        @dev payable method, payment must exactly equal:
            exercise price * number of options * eth peg
        @param _idx array, option indexes
        @return bool success
     */
    function exerciseOptions(uint256[] _idx) external payable returns (bool) {
        bytes32 _id = issuer.getID(msg.sender);
        uint256 _amount;
        uint256 _price;
        for (uint256 i; i < _idx.length; i++) {
            Option storage o = optionData[_id][_idx[i]];
            require(o.vestDate <= now, "Options have not vested");
            require(o.creationDate.add(expiryDate) > now, "Options have expired");
            _amount = _amount.add(o.amount);
            _price = _price.add(uint256(o.exercisePrice).mul(o.amount));
            _reduceTotal(o.exercisePrice, o.amount);
            emit ClaimedOptions(_id, _idx[i], o.amount, o.exercisePrice);
            delete optionData[_id][_idx[i]];
        }
        require(msg.value == _price.mul(ethPeg), "Incorrect payment amount");
        receiver.transfer(address(this).balance);
        totalOptions = totalOptions.sub(_amount);
        options[_id] = options[_id].sub(_amount);
        require(token.mint(msg.sender, _amount));
        return true;
    }

    /**
        @notice cancel expired options
        @dev
            This method does not need to be called to block the claim of expired
            options. It is used to reduce totalOptions, freeing up the authorized
            supply so that other options or tokens may be issued.
        @param _id Investor ID
        @return bool success
     */
    function cancelExpiredOptions(bytes32 _id) external returns (bool) {
        Option[] storage o = optionData[_id];
        uint256 _amount;
        for (uint256 i; i < o.length; i++) {
            if (o[i].creationDate.add(expiryDate) > now) continue;
            _amount = _amount.add(o[i].amount);
            emit ExpiredOptions(_id, i, o[i].amount);
            delete o[i];
        }
        totalOptions = totalOptions.sub(_amount);
        options[_id] = options[_id].sub(_amount);
        return true;
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
        Option[] storage o = optionData[_id];
        uint256 _amount;
        for (uint256 i; i < o.length; i++) {
            if (o[i].vestDate > now) {
                _amount = _amount.add(o[i].amount);
                _reduceTotal(o[i].exercisePrice, o[i].amount);
                delete o[i];
            } else {
                o[i].creationDate = uint32(now).sub(expiryDate).add(terminationGracePeriod);
            }
        }
        totalOptions = totalOptions.sub(_amount);
        options[_id] = options[_id].sub(_amount);
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

}
