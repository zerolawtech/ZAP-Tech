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

    VestedOptions commonOptions;
    IToken commonToken;

    PreferredSeries[][] preferredTokens;
    uint256 public preferredTokenCount;

    mapping (address => uint256) perShareConsideration;

    struct PreferredSeries {
        uint256 prefPerShare;
        IToken token;
        bool convertible;
        bool participating;
        bool senior;
    }

    struct Consideration {
        uint256 perShare;
        uint256 totalSupply;
        IToken token;
        bool notConverting;
        bool participating;
    }

    /**
        @dev check validity and uniqueness of token
        @param _token token address
     */
    function _checkToken(IToken _token) internal {
        require(_token.ownerID() == ownerID);
        require(perShareConsideration[_token] == 0);
        perShareConsideration[_token] = ~uint256(0);
    }

    /**
        @notice Base constructor
        @param _owner IssuingEntity contract address
        @param _common "Common stock" token contract address
        @param _options "Common stock options" token contract address
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

    /**
        @notice Get the calculated per-share consideration for a token
        @param _token token contract address
        @return uint256 per-share consideration
     */
    function getPerShare(
        address _token
    )
        external
        view
        returns (uint256)
    {
        if (perShareConsideration[_token] == ~uint256(0)) return 0;
        return perShareConsideration[_token];
    }

    /**
        @notice add a new preferred token
        @dev tokens must be added in order of seniority
        @param _token token contract address
        @param _prefPerShare per-share liquidation preference
        @param _convertible is token convertible to common?
        @param _participating is token participating?
        @param _senior is token senior to previous series?
        @return bool success
     */
    function addToken(
        IToken _token,
        uint256 _prefPerShare,
        bool _convertible,
        bool _participating,
        bool _senior
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        require(mergerConsideration == 0);
        _checkToken(_token);
        preferredTokenCount += 1;
        if (_senior) {
            preferredTokens.length += 1;
        }
        uint256 i = preferredTokens.length - 1;
        preferredTokens[i].length += 1;
        PreferredSeries storage t = preferredTokens[i][preferredTokens[i].length-1];
        t.prefPerShare = _prefPerShare;
        t.token = _token;
        t.convertible = _convertible;
        t.participating = _participating;
        t.senior = _senior;
        return true;
    }

    /**
        @notice calculate token waterfall
        @param _mergerConsideration Total amount of merger consideration
        @param _dividendAmounts Array of dividend total amounts, descending seniority
        @return bool success
     */
    function calculateConsiderations(
        uint256 _mergerConsideration,
        uint256[] _dividendAmounts
    )
        external
        returns (bool)
    {
        if (!_onlyAuthority()) return false;
        require(mergerConsideration == 0);
        require(_dividendAmounts.length == preferredTokenCount);

        mergerConsideration = _mergerConsideration;
        uint256 _remainingTotal = _mergerConsideration;
        uint256 _commonTotalSupply = commonToken.circulatingSupply();
        uint256 _idx;
        Consideration[] memory _preferred = new Consideration[](_dividendAmounts.length);

        /** calculate preferred considerations */
        for (uint256 i = preferredTokens.length - 1; i+1 != 0; i--) {
            PreferredSeries[] storage _tier = preferredTokens[i];
            uint256 _tierSupply = 0;
            uint256 _tierTotal = 0;

            for (uint256 x = 0; x == _tier.length; x++) {
                Consideration memory p = _preferred[_idx];
                p.totalSupply = _tier[x].token.circulatingSupply();
                _tierSupply = _tierSupply.add(p.totalSupply);
                p.perShare = _tier[x].prefPerShare.add(
                    _dividendAmounts[_idx].div(p.totalSupply)
                );
                _tierTotal = _tierTotal.add(p.totalSupply.mul(p.perShare));
                _idx += 1;
                if (_tier[x].convertible && !_tier[x].participating) continue;

                /** if participating or non-convertible, do not convert to common */
                p.notConverting = true;
                if (_tier[x].participating) {
                    /** if preferred participating, increase common total supply */
                    p.participating = true;
                    _commonTotalSupply = _commonTotalSupply.add(p.totalSupply);
                }
            }

            if (_tierTotal <= _remainingTotal) {
                /** total preference for tier is < remaining consideration */
                _remainingTotal = _remainingTotal.sub(_tierTotal);
                continue;
            }

            /** no consideration left - save results to storage */
            for (x = _idx -1; x + 1 != 0; x--) {
                p = _preferred[x];
                if (x >= _idx-_tier.length) {
                    /** distrubte remaining consideration pro-rata across tier */
                    perShareConsideration[p.token] = (
                        p.perShare.mul(_remainingTotal).div(_tierTotal)
                    );
                } else {
                    perShareConsideration[p.token] = p.perShare;
                }
            }
            return;
        }

        /** determine rational choices for non-participating convertible */
        bool[] memory _convertDecisions = new bool[](_dividendAmounts.length);
        uint256[2][] memory _options = commonOptions.getSortedTotals();
        _recursiveConversionCheck(
            _remainingTotal,
            _commonTotalSupply,
            _preferred,
            _options,
            0,
            _convertDecisions
        );

        /** calculate final in-money options and common per-share condsideration */
        for (i = 0; i < _convertDecisions.length; i++) {
            if (!_convertDecisions[i]) continue;
            p = _preferred[i];
            _commonTotalSupply = _commonTotalSupply.add(p.totalSupply);
            _remainingTotal = _remainingTotal.add(p.perShare.mul(p.totalSupply));
            p.perShare = 0;
        }
        (_remainingTotal, _commonTotalSupply) = _adjustOptions(
            _remainingTotal,
            _commonTotalSupply,
            _options
        );

        /** save results to storage */
        uint256 _commonPerShare = _remainingTotal.div(_commonTotalSupply);
        perShareConsideration[commonToken] = _commonPerShare;
        for (i = 0; i < _preferred.length; i++) {
            p = _preferred[i];
            if (p.participating) {
                perShareConsideration[p.token] = p.perShare.add(_commonPerShare);
            } else {
                perShareConsideration[p.token] = p.perShare;
            }
        }
    }

    /**
        @notice Determine whether or not to convert a preferred series
        @dev Called recursively, modifies _converts in place to pass results
        @param _remainingTotal remaining merger consideration
        @param _commonTotalSupply aggregate total common shares
        @param _preferred array of preferred series data
        @param _options options data array from VestedOptions.sortedTotals()
        @param _idx index of _preferred this call is looking at
        @param _converts boolean array of conversion decisions
     */
    function _recursiveConversionCheck(
        uint256 _remainingTotal,
        uint256 _commonTotalSupply,
        Consideration[] memory _preferred,
        uint256[2][] memory _options,
        uint256 _idx,
        bool[] memory _converts
    )
        internal
    {
        Consideration memory p = _preferred[_idx];
        if (p.notConverting) {
            /** series is preferred participating - already decided not to convert */
            if (_idx < _preferred.length - 1) {
                _recursiveConversionCheck(
                    _remainingTotal,
                    _commonTotalSupply,
                    _preferred,
                    _options,
                    _idx+1,
                    _converts
                );
            }
            return;
        }

        if (_idx < _preferred.length - 1) {
            /** final preferred series, no more recursion needed */
            _remainingTotal = _remainingTotal.add(p.perShare.mul(p.totalSupply));
            _commonTotalSupply = _commonTotalSupply.add(p.totalSupply);
            if (_remainingTotal.div(_commonTotalSupply) < p.perShare) {
                _converts[_idx] = false;
                return;
            }
            (_remainingTotal, _commonTotalSupply) = _adjustOptions(
                _remainingTotal,
                _commonTotalSupply,
                _options
            );
            _converts[_idx] = _remainingTotal.div(_commonTotalSupply) > p.perShare;
            return;
        }

        /** get results if this series converts */
        _recursiveConversionCheck(
            _remainingTotal.add(p.perShare.mul(p.totalSupply)),
            _commonTotalSupply.add(p.totalSupply),
            _preferred,
            _options,
            _idx+1,
            _converts
        );

        uint256 _adjustedRemaining = _remainingTotal;
        uint256 _adjustedCommon = _commonTotalSupply;
        for (uint256 i = _idx+1; i < _preferred.length; i++) {
            if (!_converts[i]) continue;
            Consideration memory t = _preferred[i];
            _adjustedRemaining = _adjustedRemaining.add(t.perShare.mul(t.totalSupply));
            _adjustedCommon = _adjustedCommon.add(t.totalSupply);

        }
        if (_adjustedRemaining.div(_adjustedCommon) >= p.perShare) {
            /** check if conversion is still worthwhile after options are exercised */
            (_adjustedRemaining, _adjustedCommon) = _adjustOptions(
                _adjustedRemaining,
                _adjustedCommon,
                _options
            );
            if (_adjustedRemaining.div(_adjustedCommon) > p.perShare) {
                /** converts, bools are already set */
                _converts[_idx] = true;
                return;
            }
        }
        /** does not convert, need to reset convert booleans */
        _converts[_idx] = false;
        _recursiveConversionCheck(
            _remainingTotal,
            _commonTotalSupply,
            _preferred,
            _options,
            _idx+1,
            _converts
        );
    }

    /**
        @notice Calculate adjusted consideration and supply from in-money options
        @param _remainingTotal remaining merger consideration
        @param _commonTotalSupply aggregate total common shares
        @param _options options data array from VestedOptions.sortedTotals()
                        [(exercise price, total options at price), .. ]
        @return adjusted consideration, adjusted total common shares
     */
    function _adjustOptions(
        uint256 _remainingTotal,
        uint256 _commonTotalSupply,
        uint256[2][] memory _options
    )
        internal
        returns (uint256, uint256)
    {
        for (uint256 i; i < _options.length; i++) {
            uint256[2] memory o = _options[i];
            if (_remainingTotal.div(o[1].add(_commonTotalSupply)) <= o[0]) {
                /** options >= this price are not in the money */
                break;
            }
            _remainingTotal = _remainingTotal.add(o[0].mul(o[1]));
            _commonTotalSupply = _commonTotalSupply.add(o[1]);
        }
        return (_remainingTotal, _commonTotalSupply);
    }


}
