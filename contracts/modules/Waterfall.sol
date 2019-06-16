pragma solidity >=0.4.24 <0.5.0;

import "../open-zeppelin/SafeMath.sol";
import "../interfaces/IToken.sol";
import "./bases/Module.sol";

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

    address options;
    IToken commonToken;

    Preferred[][] preferredTokens;
    uint256 public preferredTokenCount;


    /**
        @notice Base constructor
        @param _owner IssuingEntity contract address
     */
    constructor(
        address _owner,
        IToken _common,
        address _options
    )
        IssuerModuleBase(_owner)
        public
    {
        _checkToken(_common);
        commonToken = _common;
        //_checkToken(_options); TODO
        options = _options;

    }

    function _checkToken(IToken _token) internal view {
        bytes32 _id = _token.ownerID();
        require (_id == ownerID);
        require(_token != commonToken);
        require (_token != options); // TODO
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
        for (uint256 i; i < preferredTokens.length; i++) {
            for (uint256 x; x < preferredTokens[i].length; x++) {
                require(_token != preferredTokens[i][x].token);
            }
        }
        preferredTokenCount += 1;
        if (_senior) {
            preferredTokens.length += 1;
        }
        preferredTokens.length += 1;
        Preferred storage t = preferredTokens[preferredTokens.length-1];
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
        bool converting;
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
        uint256 _aggTotalSupply = 0;
        uint256 _remaining = address(this).balance;
        uint256 _idx;
        SeriesConsideration[] memory _preferredConsiderations = new SeriesConsideration[](preferredTokenCount);
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
                }
                _tierTotalPreference = _tierTotalPreference.add(p.totalSupply.mul(p.perShareConsideration));
                _idx += 1;
            }
            if (_tierTotalPreference <= _remaining) {
                _aggTotalSupply = _aggTotalSupply.add(p.totalSupply);
                _remaining = _remaining.sub(_tierTotalPreference);
                continue;
            }

            for (x = _idx - _tier.length; x == _idx; x++) {
                p = _preferredConsiderations[x];
                p.perShareConsideration = p.perShareConsideration.mul(_remaining).div(_tierTotalPreference);
            }
            return; // TODO - we ran out of moneys
        }
    }


}
