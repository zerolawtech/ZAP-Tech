pragma solidity >=0.4.24 <0.5.0;

import "../IssuingEntity.sol";
import "../open-zeppelin/SafeMath.sol";


interface IMultiCheckpointModule {
    function totalSupplyAt(address, uint256) external view returns (uint256);
    function balanceAt(address, address, uint256) external view returns (uint256);
    function custodianBalanceAt(address, address, address, uint256) external view returns (uint256);
}


/**
    @title Governance Module Minimal Implementation
    @dev
        This is included purely for testing purposes, a real implementation
        will include some form of voting mechanism. Calls should only return
        true once an action has been approved.
*/
contract GovernanceMinimal {

    using SafeMath for uint256;

    IssuingEntity public issuer;
    IMultiCheckpointModule public checkpoint;

    mapping (address => mapping (bytes => bool)) approval;
    mapping (bytes32 => Proposal) proposals;

    struct Proposal {
        uint8 state; /** 0=undeclared, 1=pending, 2=active, 3=closed */
        uint8 maxVoteValue;
        uint64 checkpoint;
        uint64 start;
        uint64 end;
        Vote[] votes;
        string description;
        address approvalAddress;
        bytes approvalCalldata;
        /* holder => custodian address (0x00 if none) */
        mapping (address => mapping (address => uint256)) hasVoted;
    }

    struct Vote {
        uint16 requiredPct;
        uint16 quorumPct;
        uint256 totalVotes;
        uint256[] counts;
        Token[] tokens;
    }

    struct Token {
        address addr;
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

    /** TODO - getters */

    function newProposal(
        bytes32 _id,
        uint64 _checkpoint,
        uint64 _start,
        uint64 _end,
        string _description,
        uint8 _maxVoteValue,
        address _approvalAddress,
        bytes _approvalCalldata
    )
        external
        returns (bool)
    {
        if (!_checkPermitted()) return false;
        Proposal storage p = proposals[_id];
        require(p.state == 0);
        require(_checkpoint <= _start);
        /* overflow protection, value cannot be 0 or 255 */
        require(_maxVoteValue - 1 < 254);
        p.state = 1;
        p.checkpoint = _checkpoint;
        p.start = _start;
        p.end = _end;
        p.description = _description;
        p.maxVoteValue = _maxVoteValue;
        if (_approvalAddress != 0x00) {
            p.approvalAddress = _approvalAddress;
            p.approvalCalldata = _approvalCalldata;
        }
        /* TODO checkpoint - set it or verify it exists */
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
        v.tokens.length = _tokens.length;
        v.counts.length = p.maxVoteValue + 1;
        /* TODO make sure no duplicate entries in tokens array */
        for (uint256 i; i < _tokens.length; i++) {
            v.tokens[i] = Token(_tokens[i], _multipliers[i]);
        }
        /* TODO emit event */
        return true;
    }

    function vote(bytes32 _id, uint256 _vote) external returns (bool) {
        Proposal storage p = proposals[_id];
        require(_vote <= p.maxVoteValue);

        /* query checkpoint totalSupply and set total possible votes */
        if (p.state == 1) {
            require(now >= p.start);
            p.state = 2;
            for (uint256 i; i < p.votes.length; i++) {
                p.votes[i].totalVotes = _getTotalVotes(
                    p.votes[i].tokens,
                    p.checkpoint
                );
            }
        }
        require(p.state == 2);
        require(p.end >= now);
        require(p.hasVoted[msg.sender][0x00] == 0);
        p.hasVoted[msg.sender][0x00] = _vote + 1;

        for (i = 0; i < p.votes.length; i++) {
            p.votes[i].counts[_vote] = p.votes[i].counts[_vote].add(_getVotes(
                p.votes[i].tokens,
                p.checkpoint
            ));
        }
        /* TODO emit event? */
        return true;
    }

    function custodialVote(bytes32 _id, address _custodian) external returns (bool) {
        Proposal storage p = proposals[_id];
        require(p.state == 2);
        require(p.end >= now || p.end == 0);
        require(p.hasVoted[msg.sender][0x00] != 0);
        require(p.hasVoted[msg.sender][_custodian] == 0);
        uint256 _vote = p.hasVoted[msg.sender][0x00] - 1;
        p.hasVoted[msg.sender][_custodian] = _vote + 1;
        for (uint256 i; i < p.votes.length; i++) {
            p.votes[i].counts[_vote] += _getCustodianVotes(p.votes[i].tokens, _custodian, p.checkpoint);
        }
        /* TODO emit event? */
        return true;
    }

    /**
        TODO - the next 3 functions could be a single function using .call
        if this contract were solidity 0.5.x - once brownie can handle multiple
        solc versions, make that change!
     */
    function _getTotalVotes(
        Token[] storage t,
        uint256 _time
    )
        internal
        view
        returns
        (uint256 _total)
    {
        for (uint256 i; i < t.length; i++) {
            uint256 _ts = checkpoint.totalSupplyAt(t[i].addr, _time);
            _total = _total.add(_ts.mul(t[i].multiplier));
        }
        return _total;
    }

    function _getVotes(
        Token[] storage t,
        uint256 _time
    )
        internal
        view
        returns (uint256 _total)
    {
        for (uint256 i; i < t.length; i++) {
            uint256 _bal = checkpoint.balanceAt(t[i].addr, msg.sender, _time);
            _total = _total.add(_bal.mul(t[i].multiplier));
        }
        return _total;
    }

    function _getCustodianVotes(
        Token[] storage t,
        address _cust,
        uint256 _time
    )
        internal
        view
        returns (uint256 _total)
    {
        for (uint256 i; i < t.length; i++) {
            uint256 _bal = checkpoint.custodianBalanceAt(t[i].addr, msg.sender, _cust, _time);
            _total = _total.add(_bal.mul(t[i].multiplier));
        }
        return _total;
    }



    function closeVote(bytes32 _id) external returns (bool) {
        if (!_checkPermitted()) return false;
        Proposal storage p = proposals[_id];
        require(p.state == 2);
        require(p.end < now);
        if (p.end == 0) {

        }
        p.state = 3;
        
        /* TODO tally votes, give permission if yes */
    }





    function _checkApproval() internal {
        if (!approval[msg.sender][msg.data]) revert();
        approval[msg.sender][msg.data] = false;
    }


    function () external {
        _checkApproval();
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

}
