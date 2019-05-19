pragma solidity >=0.4.24 <0.5.0;

import "../IssuingEntity.sol";

/**
    @title Governance Module Minimal Implementation
    @dev
        This is included purely for testing purposes, a real implementation
        will include some form of voting mechanism. Calls should only return
        true once an action has been approved.
*/
contract GovernanceMinimal {

    IssuingEntity public issuer;
    address public checkpoint;

    mapping (address => mapping (bytes => bool)) approval;
    mapping (bytes32 => Proposal) proposals;

    struct Proposal {
        uint8 state;
        uint64 checkpoint;
        uint64 start;
        uint64 end;
        Vote[] votes;
        string description;
        address approvalAddress;
        bytes approvalCalldata;
    }

    struct Vote {
        uint16 requiredPct;
        uint16 quorumPct;
        Token[] eligibleTokens;
    }

    struct Token {
        address token;
        uint16 multiplier;
    }

    /**
        @notice Base constructor
        @param _issuer IssuingEntity contract address
     */
    constructor(IssuingEntity _issuer) public {
        issuer = _issuer;
    }

    /**
        @notice Checks that a call comes from a permitted module or the issuer
        @dev If the caller is the issuer, requires multisig approval
        @return bool multisig approved
     */
    function _checkPermitted() internal returns (bool) {
        return issuer.checkMultiSigExternal(
            msg.sender,
            keccak256(msg.data),
            msg.sig
        );
    }

    function newProposal(
        bytes32 _id,
        uint64 _checkpoint,
        uint64 _start,
        uint64 _end,
        string _description,
        address _approvalAddress,
        bytes _approvalCalldata
    )
        external
        returns (bool)
    {
        if (!_checkPermitted()) return false;
        Proposal storage p = proposals[_id];
        require(p.state == 0);
        p.state = 1;
        p.checkpoint = _checkpoint;
        p.start = _start;
        p.end = _end;
        p.description = _description;
        if (_approvalAddress != 0x00) {
            p.approvalAddress = _approvalAddress;
            p.approvalCalldata = _approvalCalldata;
        }
        /* TODO checkpoint? */
        /* TODO emit event */
        return true;
    }

    function newVote(
        bytes32 _id,
        uint16 _requiredPct,
        uint16 _quorumPct,
        address[] _tokens,
        uint16[] _multipliers
    )
        external
        returns (bool)
    {
        if (!_checkPermitted()) return false;
        Proposal storage p = proposals[_id];
        require(p.state == 1);
        require(_tokens.length == _multipliers.length);
        require(_requiredPct <= 10000);
        p.votes.length += 1;
        Vote storage v = p.votes[p.votes.length-1];
        v.requiredPct = _requiredPct;
        v.quorumPct = _quorumPct;
        v.eligibleTokens.length = _tokens.length;
        for (uint256 i; i < _tokens.length; i++) {
            v.eligibleTokens[i] = Token(_tokens[i], _multipliers[i]);
        }
        /* TODO emit event */
        return true;
    }

    

    /**
        @notice Approval to modify authorized supply
        @dev Called by IssuingEntity.modifyAuthorizedSupply
        @param _token Token contract seeking to modify authorized supply
        @param _value New authorized supply value
        @return permission boolean
     */
    function modifyAuthorizedSupply(
        address _token,
        uint256 _value
    )
        external
        returns (bool)
    {
        _checkApproval();
        return true;
    }

    /**
        @notice Approval to attach a new token contract
        @dev Called by IssuingEntity.addToken
        @param _token Token contract address
        @return permission boolean
     */
    function addToken(address _token) external returns (bool) {
        _checkApproval();
        return true;
    }

    function _checkApproval() internal {
        if (!approval[msg.sender][msg.data]) revert();
        approval[msg.sender][msg.data] = false;
    }

    function () external {
        _checkApproval();
    }

}
