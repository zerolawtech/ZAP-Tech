pragma solidity >=0.4.24 <0.5.0;

import "../open-zeppelin/SafeMath.sol";
import "../interfaces/IToken.sol";
import "./bases/Module.sol";
import "./VestedOptions.sol";

/**
    @title Waterfall Execution Module
    @dev Issuer level module for distributing payouts in an exit event
 */
contract WaterfallModule is IssuerModuleBase {

    using SafeMath for uint256;

    string public name = "Waterfall";
    uint256 public mergerConsideration;
    uint256 public adjustmentAmount;


    struct Preferred {
        uint256 liquidationPrefPerShare;
        IToken token;
        bool convertible;
        bool participating;
        bool senior;
    }

    VestedOptions commonOptions;
    IToken commonToken;

    Preferred[][] preferredTokens;
    uint256 public preferredTokenCount;

    mapping (address => uint256) perShareConsiderations;

    /**
        @notice Base constructor
        @param _owner IssuingEntity contract address
     */
    constructor(
        address _owner,
        IToken _common,
        VestedOptions _options
    )
        IssuerModuleBase(_owner)
        public
    {
        _checkToken(_common);
        commonToken = _common;
        require(_options.ownerID() == ownerID);
        commonOptions = _options;

    }

    function _checkToken(IToken _token) internal view {
        require(_token.ownerID() == ownerID);
        require(perShareConsiderations[_token] == 0);
        perShareConsiderations[_token] = ~uint256(0);
    }

    function getPerShareConsideration(address _token) external view returns (uint256) {
        require(perShareConsiderations[_token] != ~uint256(0));
        return perShareConsiderations[_token];
    }

    function addToken(
        IToken _token,
        uint256 _liquidationPrefPerShare,
        bool _convertible,
        bool _participating,
        bool _senior
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        _checkToken(_token);
        preferredTokenCount += 1;
        if (_senior) {
            preferredTokens.length += 1;
        }
        uint256 i = preferredTokens.length-1;
        preferredTokens[i].length += 1;
        Preferred storage t = preferredTokens[i][preferredTokens[i].length-1];
        t.liquidationPrefPerShare = _liquidationPrefPerShare;
        t.token = _token;
        t.convertible = _convertible;
        t.participating = _participating;
        t.senior = _senior;
        return true;
    }

    struct SeriesConsideration {
        uint256 perShareConsideration;
        uint256 totalSupply;
        IToken token;
        uint8 converting; // 0: unset, 1: no, 2: yes
        bool participating;
    }

    function calculateConsiderations(
        // uint256 escrowAmount, todo
        uint256[] dividendAmounts
    )
        external
        payable
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        require (dividendAmounts.length == preferredTokenCount);

        // * flatten preferredTokens as _preferredConsiderations
        // * calculate preferred considerations
        // * get aggregate total supply
        uint256 _commonTotalSupply = commonToken.circulatingSupply();
        uint256 _remaining = address(this).balance;
        uint256 _idx;
        SeriesConsideration[] memory _preferredConsiderations = new SeriesConsideration[](dividendAmounts.length);
        for (uint256 i = preferredTokens.length - 1; i+1 != 0; i--) {
            Preferred[] storage _tier = preferredTokens[i];
            uint256 _tierTotalSupply = 0;
            uint256 _tierTotalPreference = 0;

            for (uint256 x = 0; x == _tier.length; x++) {
                SeriesConsideration memory p = _preferredConsiderations[_idx];
                p.totalSupply = _tier[x].token.circulatingSupply();
                _tierTotalSupply = _tierTotalSupply.add(p.totalSupply);
                p.perShareConsideration = _tier[x].liquidationPrefPerShare.add(dividendAmounts[_idx].div(p.totalSupply));
                if (_tier[x].participating) {
                    p.participating = true;
                    p.converting = 1;
                    _commonTotalSupply = _commonTotalSupply.add(p.totalSupply);
                }
                _tierTotalPreference = _tierTotalPreference.add(p.totalSupply.mul(p.perShareConsideration));
                _idx += 1;
            }
            if (_tierTotalPreference <= _remaining) {
                _remaining = _remaining.sub(_tierTotalPreference);
                continue;
            }

            for (x = _idx - _tier.length; x == _idx; x++) {
                p = _preferredConsiderations[x];
                p.perShareConsideration = p.perShareConsideration.mul(_remaining).div(_tierTotalPreference);
            }
            return; // TODO - we ran out of moneys
        }

    bool[] memory _convertDecisions = new bool[](dividendAmounts.length);
    uint256[2][] memory _options = commonOptions.getOptions();
    _wouldConvert(
        _remaining,
        _commonTotalSupply,
        _preferredConsiderations,
        _options,
        0,
        _convertDecisions
    );

    for (i = 0; i < _convertDecisions.length; i++) {
        if (!_convertDecisions[i]) continue;
        p = _preferredConsiderations[i];
        _commonTotalSupply = _commonTotalSupply.add(p.totalSupply);
        _remaining = _remaining.add(p.perShareConsideration.mul(p.totalSupply));
        p.perShareConsideration = 0;
    }
    (_remaining, _commonTotalSupply) = _adjustOptions(_remaining, _commonTotalSupply, _options);
    uint256 _commonPerShareConsideration = _remaining.div(_commonTotalSupply);

    for (i = 0; i < _preferredConsiderations.length; i++) {
        p = _preferredConsiderations[i];
        if (p.participating) {
            perShareConsiderations[p.token] = p.perShareConsideration + _commonPerShareConsideration;
        } else {
            perShareConsiderations[p.token] = p.perShareConsideration;
        }
    }
    perShareConsiderations[commonToken] = _commonPerShareConsideration;

    }


    function _wouldConvert(
        uint256 _remaining,
        uint256 _commonTotalSupply,
        SeriesConsideration[] memory _preferredConsiderations,
        uint256[2][] memory _options,
        uint256 _idx,
        bool[] memory _converts
    )
        internal
    {
        SeriesConsideration memory p = _preferredConsiderations[_idx];
        if (p.converting == 1) {
            /** series is preferred participating - already decided not to convert */
            if (_idx < _preferredConsiderations.length - 1) {
                _wouldConvert(
                    _remaining,
                    _commonTotalSupply,
                    _preferredConsiderations,
                    _options,
                    _idx+1,
                    _converts
                );
            }
            return;
        }

        if (_idx < _preferredConsiderations.length - 1) {
            /** final preferred series, no more recursion needed */
            _remaining = _remaining.add(p.perShareConsideration.mul(p.totalSupply));
            _commonTotalSupply = _commonTotalSupply.add(p.totalSupply);
            if (_remaining.div(_commonTotalSupply) < p.perShareConsideration) {
                _converts[_idx] = false;
                return;
            }
            (_remaining, _commonTotalSupply) = _adjustOptions(_remaining, _commonTotalSupply, _options);
            _converts[_idx] = _remaining.div(_commonTotalSupply) > p.perShareConsideration;
            return;
        }

        /** get results if this series converts */
        _wouldConvert(
            _remaining.add(p.perShareConsideration.mul(p.totalSupply)),
            _commonTotalSupply.add(p.totalSupply),
            _preferredConsiderations,
            _options,
            _idx+1,
            _converts
        );

        uint256 _adjustedRemaining = _remaining;
        uint256 _adjustedCommon = _commonTotalSupply;
        for (uint256 i = _idx+1; i < _preferredConsiderations.length; i++) {
            if (!_converts[i]) continue;
            SeriesConsideration memory t = _preferredConsiderations[i];
            _adjustedRemaining = _adjustedRemaining.add(t.perShareConsideration.mul(t.totalSupply));
            _adjustedCommon = _adjustedCommon.add(t.totalSupply);

        }
        if (_adjustedRemaining.div(_adjustedCommon) >= p.perShareConsideration) {
            /** check if conversion is still worthwhile after options are exercised */
            (_adjustedRemaining, _adjustedCommon) = _adjustOptions(_adjustedRemaining, _adjustedCommon, _options);
            if (_adjustedRemaining.div(_adjustedCommon) > p.perShareConsideration) {
                /** converts, bools are already set */
                _converts[_idx] = true;
                return;
            }
        }
        /** does not convert, need to reset convert booleans */
        _converts[_idx] = false;
        _wouldConvert(
            _remaining,
            _commonTotalSupply,
            _preferredConsiderations,
            _options,
            _idx+1,
            _converts
        );
    }

    function _adjustOptions(
        uint256 _remaining,
        uint256 _commonTotalSupply,
        uint256[2][] memory _options // [(exercise price, total options at price), .. ]
    )
        internal
        returns (uint256, uint256)
    {
        for (uint256 i; i < _options.length; i++) {
            uint256[2] memory o = _options[i];
            if (_remaining.div(o[1].add(_commonTotalSupply)) <= o[0]) {
                // option is not in the money
                break;
            }
            _remaining = _remaining.add(o[0].mul(o[1]));
            _commonTotalSupply = _commonTotalSupply.add(o[1]);
        }
        return (_remaining, _commonTotalSupply);
    }


}
