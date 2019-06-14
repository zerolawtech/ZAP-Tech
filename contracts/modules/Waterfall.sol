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

    Preferred[] preferredTokens;

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
            require(_token != preferredTokens[i].token);
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

    SeriesConsideration[] considerations;
    struct SeriesConsideration {
        IToken token;
        uint256 dividendAmount;
        uint256 totalPerShareConsideration;
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
        require(dividendAmounts.length == preferredTokens.length);

        uint256 pariPasu = 0;
        uint256 total = 0;
        uint remaining = address(this).balance;
        for (uint256 i = pariPasu; i+1 != 0; i--) {
            considerations.length++;
            SeriesConsideration storage c = considerations[considerations.length-1];

            c.token = preferredTokens[i].token;
            preferredTokens[i].token.circulatingSupply();
            c.dividendAmount = dividendAmounts[i];

            uint256 _supply = c.token.circulatingSupply();
            c.totalPerShareConsideration = (
                preferredTokens[i].liquidationPrefPerShare.add(c.dividendAmount.div(_supply))
            );
            total += _supply * c.totalPerShareConsideration;
            if (preferredTokens[i].senior) {
                if (total > remaining) {
                    _reduceConsideration(pariPasu, remaining.mul(1000).div(total));
                    return true; // rekt
                }
                pariPasu = considerations.length;
            }
        }
    }

    function _reduceConsideration(uint256 i, uint256 _pct) internal {
        for (; i < considerations.length; i++) {
            considerations[i].totalPerShareConsideration = considerations[i].totalPerShareConsideration.mul(_pct).div(1000);
        }
    }


}
